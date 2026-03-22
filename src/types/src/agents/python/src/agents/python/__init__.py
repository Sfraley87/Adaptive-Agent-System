"""
Adaptive Agent System - Python Implementation

Multi-agent orchestration framework for building intelligent, adaptive user experiences.
"""

from types import (
    AgentSignal,
    UserStateProfile,
    AdaptationAction,
    OrchestratorResult,
)
from flow_agent import run_flow_agent
from strategy_agent import run_strategy_agent
from workspace_agent import run_workspace_agent
from adaptation_agent import run_adaptation_agent
from orchestrator import run_orchestrator

__all__ = [
    "AgentSignal",
    "UserStateProfile",
    "AdaptationAction",
    "OrchestratorResult",
    "run_flow_agent",
    "run_strategy_agent",
    "run_workspace_agent",
    "run_adaptation_agent",
    "run_orchestrator",
]

__version__ = "1.0.0"
