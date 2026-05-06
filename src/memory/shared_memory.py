"""
共享记忆系统：多 Agent 协作的信息中枢
使用向量数据库存储语义记忆，Redis 存储短期工作记忆
"""

from typing import Any, Dict, Optional
import json
import hashlib


class SharedMemory:
    """
    实现多 Agent 间的信息共享与长期记忆

    存储结构：
    - 短期记忆（工作区）：当前执行上下文
    - 长期记忆（向量库）：历史项目经验、最佳实践
    - 元记忆：Agent 间的协作模式与偏好
    """

    def __init__(self):
        # 生产环境应接入 ChromaDB + Redis
        self._store: Dict[str, Any] = {}
        self._vectors: Dict[str, list] = {}

    def store(self, key: str, value: Any, metadata: Optional[Dict] = None):
        """存储信息到共享记忆"""
        entry = {
            "value": value,
            "metadata": metadata or {},
            "timestamp": __import__('time').time(),
        }
        self._store[key] = entry

        # 模拟向量存储（实际应嵌入模型生成向量）
        self._vectors[key] = self._simple_hash(key)

    def retrieve(self, key: str) -> Optional[Any]:
        """检索信息"""
        entry = self._store.get(key)
        return entry["value"] if entry else None

    def search_similar(self, query: str, top_k: int = 3) -> list:
        """语义相似度搜索（模拟）"""
        # 生产环境：query_embedding = embed(query); similarity_search(vectors, query_embedding)
        return [
            {"key": k, "score": 0.95, "value": v["value"]}
            for k, v in list(self._store.items())[:top_k]
        ]

    def get_context_window(self, agent_name: str) -> Dict:
        """获取指定 Agent 的上下文窗口"""
        return {
            "recent_decisions": [v for k, v in self._store.items() if "stage_" in k],
            "relevant_memories": self.search_similar(agent_name),
        }

    def _simple_hash(self, text: str) -> list:
        """模拟文本嵌入（生产环境使用 sentence-transformers）"""
        h = hashlib.md5(text.encode()).hexdigest()
        return [int(h[i:i + 2], 16) / 255.0 for i in range(0, 16, 2)]