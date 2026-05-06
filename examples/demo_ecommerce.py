"""
AutoDevOps 演示：电商秒杀系统端到端生成
运行此脚本展示完整的 Agent 协作流程
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.orchestrator import Orchestrator


async def main():
    print("=" * 60)
    print("AutoDevOps 演示：电商秒杀系统")
    print("=" * 60)

    orchestrator = Orchestrator()

    # 定义需求与约束
    requirement = (
        "构建一个支持秒杀活动的电商订单系统，"
        "需要处理 10万 QPS 的瞬时流量，"
        "保证库存不超卖，支持多种支付方式，"
        "订单状态实时同步给用户"
    )

    constraints = {
        "budget": "云成本 < ¥5000/月",
        "latency": "P95 < 200ms",
        "availability": "99.99%",
        "compliance": "等保三级",
    }

    print(f"\n📋 需求: {requirement}")
    print(f"🔒 约束: {constraints}\n")

    # 执行端到端流程
    result = await orchestrator.execute(requirement, constraints)

    # 输出结果
    print("\n" + "=" * 60)
    print("执行结果")
    print("=" * 60)
    print(f"最终状态: {result.stage.value}")
    print(f"总耗时: {result.metrics.get('total_duration_sec', 0):.2f} 秒")
    print(f"重试次数: {result.retry_count}")

    print("\n📊 各阶段决策记录:")
    for decision in result.decisions:
        print(f"  • [{decision['stage']}] {decision['agent']} "
              f"(置信度: {decision['confidence']:.2f}, 耗时: {decision['duration_sec']:.2f}s)")

    print("\n🏗️ 生成产物概览:")
    for stage, artifact in result.artifacts.items():
        if isinstance(artifact, dict) and 'summary' in artifact:
            print(f"  • {stage}: {artifact['summary']}")

    if result.stage.value == "completed":
        print("\n✅ 系统已成功设计并生成部署配置！")
        print("下一步: 执行 `kubectl apply -f k8s/` 部署到集群")
    else:
        print(f"\n❌ 执行失败: {result.artifacts.get('error', 'Unknown error')}")

    # 输出执行轨迹
    print("\n" + "=" * 60)
    print("完整执行轨迹")
    print("=" * 60)
    print(orchestrator.get_execution_trace(result))


if __name__ == "__main__":
    asyncio.run(main())