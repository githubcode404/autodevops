"""
Planner Agent：需求分析与任务分解
核心能力：长链推理的第一步，将模糊需求转化为结构化任务清单
"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    """
    职责：
    1. 解析自然语言需求，提取功能性与非功能性需求
    2. 识别潜在风险（技术债务、合规要求、性能瓶颈）
    3. 分解为可并行的子任务，确定依赖关系
    4. 输出：任务清单、风险报告、验收标准
    """

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        requirement = input_data["requirement"]
        constraints = input_data.get("constraints", {})

        # 模拟深度推理过程
        analysis = self._analyze_requirement(requirement)
        tasks = self._decompose_tasks(analysis)
        risks = self._identify_risks(analysis, constraints)

        return {
            "summary": f"Decomposed into {len(tasks)} tasks with {len(risks)} risks identified",
            "confidence": 0.92,
            "tasks": tasks,
            "risks": risks,
            "acceptance_criteria": self._generate_criteria(analysis),
            "technical_constraints": constraints,
        }

    def _analyze_requirement(self, requirement: str) -> Dict:
        """需求解析：识别实体、动作、约束"""
        # 实际实现中调用 LLM 进行结构化提取
        return {
            "domain": self._extract_domain(requirement),
            "entities": self._extract_entities(requirement),
            "actions": self._extract_actions(requirement),
            "scale": self._estimate_scale(requirement),
        }

    def _decompose_tasks(self, analysis: Dict) -> List[Dict]:
        """任务分解：将需求拆分为可执行的子任务"""
        tasks = []
        domain = analysis["domain"]

        # 根据领域特征生成任务模板
        if "电商" in domain or "ecommerce" in domain:
            tasks = [
                {"id": "T1", "name": "用户认证服务", "priority": "high", "deps": []},
                {"id": "T2", "name": "商品目录服务", "priority": "high", "deps": []},
                {"id": "T3", "name": "订单处理服务", "priority": "high", "deps": ["T1", "T2"]},
                {"id": "T4", "name": "库存管理服务", "priority": "high", "deps": ["T3"]},
                {"id": "T5", "name": "支付网关集成", "priority": "high", "deps": ["T3"]},
                {"id": "T6", "name": "秒杀/限流模块", "priority": "critical", "deps": ["T4"]},
                {"id": "T7", "name": "监控与告警", "priority": "medium", "deps": ["T1-T6"]},
            ]

        return tasks

    def _identify_risks(self, analysis: Dict, constraints: Dict) -> List[Dict]:
        """风险识别"""
        risks = []

        # 根据约束条件识别风险
        if constraints.get("latency", "") and "ms" in str(constraints.get("latency", "")):
            risks.append({
                "type": "performance",
                "description": "低延迟要求可能需要引入缓存层（Redis/Memcached）",
                "mitigation": "架构阶段设计多级缓存策略",
                "severity": "high"
            })

        if "秒杀" in str(analysis) or "spike" in str(analysis):
            risks.append({
                "type": "reliability",
                "description": "高并发场景下库存超卖风险",
                "mitigation": "引入分布式锁 + 消息队列削峰",
                "severity": "critical"
            })

        return risks

    def _extract_domain(self, req: str) -> str:
        domains = ["电商", "社交", "金融", "物联网", "AI"]
        for d in domains:
            if d in req:
                return d
        return "通用"

    def _extract_entities(self, req: str) -> List[str]:
        # 简化实现
        return ["用户", "订单", "商品"]

    def _extract_actions(self, req: str) -> List[str]:
        return ["创建", "查询", "更新", "删除"]

    def _estimate_scale(self, req: str) -> str:
        if "1000" in req or "万" in req:
            return "large"
        return "medium"

    def _generate_criteria(self, analysis: Dict) -> List[str]:
        return [
            "所有 API 响应时间 P95 < 500ms",
            "系统可用性 > 99.9%",
            "支持水平扩展至 10 倍流量",
        ]