"""
Agent 基类，定义所有 Agent 的通用接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAgent(ABC):
    def __init__(self, memory):
        self.memory = memory
        self.name = self.__class__.__name__

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行 Agent 核心逻辑"""
        pass

    def recall(self, key: str) -> Any:
        """从共享记忆中检索信息"""
        return self.memory.retrieve(key)

    def think(self, prompt: str) -> str:
        """
        模拟推理过程（实际实现中调用 LLM API）
        此处为演示结构，实际部署需接入 OpenAI/Claude/本地模型
        """
        # 生产环境：return call_llm(prompt)
        return f"[{self.name}] Processing: {prompt[:50]}..."