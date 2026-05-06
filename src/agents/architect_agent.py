"""
Architect Agent：系统架构设计
核心能力：根据 Planner 输出设计技术架构，生成交付给 Coder 的详细设计约束
"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent


class ArchitectAgent(BaseAgent):
    """
    职责：
    1. 选择技术栈（考虑团队熟悉度、社区活跃度、云原生支持）
    2. 设计服务边界与接口契约（OpenAPI/Swagger）
    3. 数据模型设计（ER 图、索引策略）
    4. 非功能性设计：缓存策略、消息队列选型、分库分表方案
    """

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        previous = input_data.get("previous_artifacts", {})
        planner_output = previous.get("planning", {})
        tasks = planner_output.get("tasks", [])
        risks = planner_output.get("risks", [])
        constraints = input_data.get("constraints", {})

        # 基于任务特征设计架构
        architecture = self._design_architecture(tasks, risks, constraints)
        interfaces = self._design_interfaces(architecture)
        data_model = self._design_data_model(architecture)
        infra = self._design_infrastructure(architecture, constraints)

        return {
            "summary": f"Designed {len(architecture['services'])} microservices with {architecture['pattern']}",
            "confidence": 0.88,
            "architecture": architecture,
            "interfaces": interfaces,
            "data_model": data_model,
            "infrastructure": infra,
            "design_decisions": self._record_decisions(architecture),
        }

    def _design_architecture(self, tasks: List[Dict], risks: List[Dict], constraints: Dict) -> Dict:
        """核心架构设计"""
        # 根据任务复杂度选择架构模式
        has_critical = any(r["severity"] == "critical" for r in risks)
        pattern = "event-driven-microservices" if has_critical else "layered-monolith"

        services = []
        for task in tasks:
            if "服务" in task["name"]:
                services.append({
                    "name": task["name"],
                    "type": "service",
                    "scale_policy": "auto" if task["priority"] == "critical" else "manual",
                    "dependencies": task["deps"],
                })

        return {
            "pattern": pattern,
            "services": services,
            "communication": "gRPC + Message Queue (RabbitMQ/Apache Kafka)",
            "gateway": "Kong/AWS API Gateway",
            "service_mesh": "Istio（如需高级流量管理）",
        }

    def _design_interfaces(self, architecture: Dict) -> List[Dict]:
        """设计 API 接口契约"""
        interfaces = []
        for svc in architecture["services"]:
            interfaces.append({
                "service": svc["name"],
                "endpoints": [
                    {"method": "GET", "path": f"/api/v1/{svc['name']}/health", "auth": "none"},
                    {"method": "POST", "path": f"/api/v1/{svc['name']}", "auth": "JWT"},
                ],
                "protocol": "REST" if svc["type"] == "service" else "gRPC",
            })
        return interfaces

    def _design_data_model(self, architecture: Dict) -> Dict:
        """数据模型设计"""
        return {
            "database": "PostgreSQL（主库）+ Redis（缓存）+ ClickHouse（分析）",
            "sharding_strategy": "按用户 ID 哈希分片",
            "indexing": ["B-Tree on user_id", "GiST on geo_location", "Inverted on search_text"],
            "backup": "每日全量 + 实时增量（WAL）",
        }

    def _design_infrastructure(self, architecture: Dict, constraints: Dict) -> Dict:
        """基础设施设计"""
        budget = constraints.get("budget", "")
        if "500" in str(budget):
            return {
                "platform": "阿里云/腾讯云轻量应用服务器",
                "container": "Docker Compose（初期）→ Kubernetes（增长期）",
                "ci_cd": "GitHub Actions",
                "monitoring": "Prometheus + Grafana + AlertManager",
                "cost_optimization": ["Spot 实例", "CDN 缓存", "对象存储生命周期策略"],
            }
        return {"platform": "Kubernetes", "container": "Docker", "ci_cd": "ArgoCD"}

    def _record_decisions(self, architecture: Dict) -> List[Dict]:
        """记录架构决策（ADR）"""
        return [
            {"id": "ADR-001", "decision": f"采用 {architecture['pattern']}", "rationale": "高并发风险要求服务解耦"},
            {"id": "ADR-002", "decision": "使用 PostgreSQL 主库", "rationale": "ACID 保证 + JSONB 灵活 schema"},
        ]