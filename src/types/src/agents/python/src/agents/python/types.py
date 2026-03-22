from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass

@dataclass
class AgentSignal:
    agent: Literal["flow", "strategy", "workspace", "adaptation"]
    signal: str
    confidence: float
    summary: str
    suggested_action: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

@dataclass
class UserStateProfile:
    user_id: str
    tier: int
    current_energy: Optional[Literal["high", "medium", "low"]]
    feedback_style: Optional[Literal["celebratory", "direct", "balanced"]]
    momentum_score: float
    overwhelm_risk: float
    workspace_complexity_tolerance: float
    peak_focus_windows: List[Dict[str, Any]]
    module_usage: Dict[str, int]
    hidden_modules: List[str]
    active_modules: List[str]
    priorities_summary: List[str]
    recent_wins_count: int
    total_ideas: int
    completed_ideas: int
    friction_signals: List[str]
    suggested_work_mode: Optional[Literal["deep", "light", "admin", "planning"]]
    last_adaptation_at: Optional[str]
    hour_of_day: int
    day_of_week: int
    has_checked_in_today: bool
    recent_sprint_count: int

@dataclass
class AdaptationAction:
    type: str
    params: Optional[Dict[str, Any]] = None
    applied: bool = False
    reason: str = ""

@dataclass
class OrchestratorResult:
    signals: List[AgentSignal]
    actions: List[AdaptationAction]
    state_profile: UserStateProfile
    suggested_energy_filter: Optional[Literal["high", "medium", "low"]]
    applied_at: str
