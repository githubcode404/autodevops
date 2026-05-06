"""
DevOps Agent：部署运维自动化
核心能力：生成 CI/CD 配置、容器化、监控告警、自动扩缩容
"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent


class DevOpsAgent(BaseAgent):
    """
    职责：
    1. 生成 Dockerfile、docker-compose.yml、K8s manifests
    2. 配置 CI/CD 流水线（GitHub Actions/GitLab CI）
    3. 设置监控（Prometheus metrics、Grafana dashboards、AlertManager rules）
    4. 自动扩缩容策略（HPA/VPA）
    5. 蓝绿部署/金丝雀发布配置
    """

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        previous = input_data.get("previous_artifacts", {})
        code = previous.get("coding", {}).get("code", {})
        architecture = previous.get("architecture", {}).get("architecture", {})

        services = list(code.keys())

        # 生成部署产物
        dockerfiles = self._generate_dockerfiles(services)
        k8s_manifests = self._generate_k8s_manifests(services, architecture)
        cicd_config = self._generate_cicd(services)
        monitoring = self._generate_monitoring(services)

        return {
            "summary": f"Generated deployment configs for {len(services)} services",
            "confidence": 0.90,
            "dockerfiles": dockerfiles,
            "kubernetes": k8s_manifests,
            "cicd": cicd_config,
            "monitoring": monitoring,
            "deployment_strategy": "blue-green",
            "rollback_policy": "automatic on error_rate > 1% or p95_latency > 1s",
        }

    def _generate_dockerfiles(self, services: List[str]) -> Dict[str, str]:
        """生成容器化配置"""
        dockerfiles = {}
        for svc in services:
            dockerfiles[svc] = f'''# {svc} Service Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .

EXPOSE 8000
CMD ["uvicorn", "{svc.lower().replace(' ', '_')}_service:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        return dockerfiles

    def _generate_k8s_manifests(self, services: List[str], architecture: Dict) -> Dict[str, str]:
        """生成 K8s 部署配置"""
        manifests = {}
        for svc in services:
            svc_safe = svc.lower().replace(" ", "-")
            manifests[svc] = f'''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {svc_safe}
  labels:
    app: {svc_safe}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {svc_safe}
  template:
    metadata:
      labels:
        app: {svc_safe}
    spec:
      containers:
      - name: {svc_safe}
        image: autodevops/{svc_safe}:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/v1/{svc_safe.replace('-', '')}/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/{svc_safe.replace('-', '')}/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {svc_safe}-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {svc_safe}
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
'''
        return manifests

    def _generate_cicd(self, services: List[str]) -> Dict[str, str]:
        """生成 CI/CD 配置"""
        return {
            "github_actions.yml": '''name: AutoDevOps CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests with coverage
        run: pytest --cov=src --cov-report=xml --cov-fail-under=80
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [用户认证, 商品目录, 订单处理, 库存管理]
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: |
          docker build -t autodevops/${{ matrix.service }}:${{ github.sha }} .
          docker tag autodevops/${{ matrix.service }}:${{ github.sha }} autodevops/${{ matrix.service }}:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f k8s/
          kubectl rollout status deployment/
''',
            "gitlab-ci.yml": "# GitLab CI 配置（备用）"
        }

    def _generate_monitoring(self, services: List[str]) -> Dict[str, str]:
        """生成监控配置"""
        return {
            "prometheus_rules.yml": '''groups:
- name: autodevops-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"

  - alert: HighLatency
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "P95 latency exceeds 500ms"
''',
            "grafana_dashboard.json": '{"title": "AutoDevOps Overview", "panels": [...]}'
        }