"""
AutoDevOps Orchestrator
多 Agent 协调核心，实现长链推理与质量门禁
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time

from src.agents.planner_agent import PlannerAgent
from src.agents.architect_agent import ArchitectAgent
from src.agents.coder_agent import CoderAgent
from src.agents.tester_agent import TesterAgent
from src.agents.devops_agent import DevOpsAgent
from src.memory.shared_memory import SharedMemory

logger = logging.getLogger(__name__)


class Stage(Enum):
    PLANNING = "planning"
    ARCHITECTURE = "architecture"
    CODING = "coding"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ExecutionContext:
    requirement: str
    constraints: Dict[str, Any]
    stage: Stage = Stage.PLANNING
    artifacts: Dict[str, Any] = field(default_factory=dict)
    decisions: List[Dict] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3


class Orchestrator:
    def __init__(self, llm_config: Optional[Dict] = None):
        self.memory = SharedMemory()
        self.agents = {
            "planner": PlannerAgent(self.memory),
            "architect": ArchitectAgent(self.memory),
            "coder": CoderAgent(self.memory),
            "tester": TesterAgent(self.memory),
            "devops": DevOpsAgent(self.memory),
        }
        self.quality_gates = {
            "test_coverage": 0.80,
            "performance_p95_latency_ms": 500,
            "security_score": 0.90,
        }

    async def execute(self, requirement: str, constraints: Optional[Dict] = None) -> ExecutionContext:
        context = ExecutionContext(
            requirement=requirement,
            constraints=constraints or {},
            metrics={"start_time": time.time()}
        )

        try:
            context = await self._run_stage(context, "planner", Stage.PLANNING, Stage.ARCHITECTURE)
            context = await self._run_stage(context, "architect", Stage.ARCHITECTURE, Stage.CODING)
            context = await self._run_stage(context, "coder", Stage.CODING, Stage.TESTING)
            context = await self._run_stage(context, "tester", Stage.TESTING, Stage.DEPLOYMENT)

            if not self._pass_quality_gate(context):
                context = await self._handle_quality_failure(context)

            context = await self._run_stage(context, "devops", Stage.DEPLOYMENT, Stage.COMPLETED)
            context.metrics["total_duration_sec"] = time.time() - context.metrics["start_time"]

        except Exception as e:
            context.stage = Stage.FAILED
            context.artifacts["error"] = str(e)

        return context

    async def _run_stage(self, context, agent_name, current_stage, next_stage):
        context.stage = current_stage
        agent = self.agents[agent_name]

        stage_input = {
            "requirement": context.requirement,
            "constraints": context.constraints,
            "previous_artifacts": context.artifacts,
            "stage_history": context.decisions,
        }

        start = time.time()
        result = await agent.execute(stage_input)
        duration = time.time() - start

        context.decisions.append({
            "stage": current_stage.value,
            "agent": agent_name,
            "duration_sec": duration,
            "summary": result.get("summary", ""),
            "confidence": result.get("confidence", 0.0),
        })

        context.artifacts[current_stage.value] = result
        self.memory.store(f"stage_{current_stage.value}", result)
        context.stage = next_stage
        return context

    def _pass_quality_gate(self, context):
        test_results = context.artifacts.get("testing", {})
        coverage = test_results.get("coverage", 0)
        latency = test_results.get("performance", {}).get("p95_latency_ms", float('inf'))
        security = test_results.get("security_score", 0)

        passed = (
                coverage >= self.quality_gates["test_coverage"] and
                latency <= self.quality_gates["performance_p95_latency_ms"] and
                security >= self.quality_gates["security_score"]
        )

        context.metrics["quality_gate"] = {
            "passed": passed,
            "coverage": coverage,
            "latency_p95": latency,
            "security": security,
        }
        return passed

    async def _handle_quality_failure(self, context):
        if context.retry_count >= context.max_retries:
            raise RuntimeError(f"Quality gate failed after {context.max_retries} retries")

        context.retry_count += 1
        context.artifacts["coding_feedback"] = context.artifacts.get("testing", {}).get("failures", [])
        context.stage = Stage.CODING

        context = await self._run_stage(context, "coder", Stage.CODING, Stage.TESTING)
        context = await self._run_stage(context, "tester", Stage.TESTING, Stage.DEPLOYMENT)

        if not self._pass_quality_gate(context):
            context = await self._handle_quality_failure(context)

        return context

    def get_execution_trace(self, context):
        trace = []
        for decision in context.decisions:
            trace.append(f"[{decision['stage']}] {decision['agent']} "
                         f"(confidence: {decision['confidence']:.2f}, "
                         f"duration: {decision['duration_sec']:.2f}s)")
        return "\n".join(trace)"""
AutoDevOps Orchestrator
多 Agent 协调核心，实现长链推理与质量门禁
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time

from src.agents.planner_agent import PlannerAgent
from src.agents.architect_agent import ArchitectAgent
from src.agents.coder_agent import CoderAgent
from src.agents.tester_agent import TesterAgent
from src.agents.devops_agent import DevOpsAgent
from src.memory.shared_memory import SharedMemory

logger = logging.getLogger(__name__)

class Stage(Enum):
    PLANNING = "planning"
    ARCHITECTURE = "architecture"
    CODING = "coding"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ExecutionContext:
    requirement: str
    constraints: Dict[str, Any]
    stage: Stage = Stage.PLANNING
    artifacts: Dict[str, Any] = field(default_factory=dict)
    decisions: List[Dict] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3

class Orchestrator:
    def __init__(self, llm_config: Optional[Dict] = None):
        self.memory = SharedMemory()
        self.agents = {
            "planner": PlannerAgent(self.memory),
            "architect": ArchitectAgent(self.memory),
            "coder": CoderAgent(self.memory),
            "tester": TesterAgent(self.memory),
            "devops": DevOpsAgent(self.memory),
        }
        self.quality_gates = {
            "test_coverage": 0.80,
            "performance_p95_latency_ms": 500,
            "security_score": 0.90,
        }

    async def execute(self, requirement: str, constraints: Optional[Dict] = None) -> ExecutionContext:
        context = ExecutionContext(
            requirement=requirement,
            constraints=constraints or {},
            metrics={"start_time": time.time()}
        )

        try:
            context = await self._run_stage(context, "planner", Stage.PLANNING, Stage.ARCHITECTURE)
            context = await self._run_stage(context, "architect", Stage.ARCHITECTURE, Stage.CODING)
            context = await self._run_stage(context, "coder", Stage.CODING, Stage.TESTING)
            context = await self._run_stage(context, "tester", Stage.TESTING, Stage.DEPLOYMENT)

            if not self._pass_quality_gate(context):
                context = await self._handle_quality_failure(context)

            context = await self._run_stage(context, "devops", Stage.DEPLOYMENT, Stage.COMPLETED)
            context.metrics["total_duration_sec"] = time.time() - context.metrics["start_time"]

        except Exception as e:
            context.stage = Stage.FAILED
            context.artifacts["error"] = str(e)

        return context

    async def _run_stage(self, context, agent_name, current_stage, next_stage):
        context.stage = current_stage
        agent = self.agents[agent_name]

        stage_input = {
            "requirement": context.requirement,
            "constraints": context.constraints,
            "previous_artifacts": context.artifacts,
            "stage_history": context.decisions,
        }

        start = time.time()
        result = await agent.execute(stage_input)
        duration = time.time() - start

        context.decisions.append({
            "stage": current_stage.value,
            "agent": agent_name,
            "duration_sec": duration,
            "summary": result.get("summary", ""),
            "confidence": result.get("confidence", 0.0),
        })

        context.artifacts[current_stage.value] = result
        self.memory.store(f"stage_{current_stage.value}", result)
        context.stage = next_stage
        return context

    def _pass_quality_gate(self, context):
        test_results = context.artifacts.get("testing", {})
        coverage = test_results.get("coverage", 0)
        latency = test_results.get("performance", {}).get("p95_latency_ms", float('inf'))
        security = test_results.get("security_score", 0)

        passed = (
            coverage >= self.quality_gates["test_coverage"] and
            latency <= self.quality_gates["performance_p95_latency_ms"] and
            security >= self.quality_gates["security_score"]
        )

        context.metrics["quality_gate"] = {
            "passed": passed,
            "coverage": coverage,
            "latency_p95": latency,
            "security": security,
        }
        return passed

    async def _handle_quality_failure(self, context):
        if context.retry_count >= context.max_retries:
            raise RuntimeError(f"Quality gate failed after {context.max_retries} retries")

        context.retry_count += 1
        context.artifacts["coding_feedback"] = context.artifacts.get("testing", {}).get("failures", [])
        context.stage = Stage.CODING

        context = await self._run_stage(context, "coder", Stage.CODING, Stage.TESTING)
        context = await self._run_stage(context, "tester", Stage.TESTING, Stage.DEPLOYMENT)

        if not self._pass_quality_gate(context):
            context = await self._handle_quality_failure(context)

        return context

    def get_execution_trace(self, context):
        trace = []
        for decision in context.decisions:
            trace.append(f"[{decision['stage']}] {decision['agent']} "
                        f"(confidence: {decision['confidence']:.2f}, "
                        f"duration: {decision['duration_sec']:.2f}s)")
        return "\n".join(trace)