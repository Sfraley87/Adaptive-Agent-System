from typing import Optional, List
from datetime import datetime
from types import UserStateProfile, OrchestratorResult, AdaptationAction, AgentSignal
from flow_agent import run_flow_agent
from strategy_agent import run_strategy_agent
from workspace_agent import run_workspace_agent
from adaptation_agent import run_adaptation_agent

def resolve_energy_filter(
    signals: List[AgentSignal],
    state: UserStateProfile
) -> Optional[str]:
    """
    Determine energy filter from signals, preferring high-confidence signals.
    """
    flow_signals = [s for s in signals if s.agent == "flow"]
    
    low_energy = next(
        (s for s in flow_signals if s.signal == "low_energy_state"),
        None
    )
    high_energy = next(
        (s for s in flow_signals if s.signal == "high_energy_state"),
        None
    )
    momentum_stalled = next(
        (s for s in flow_signals if s.signal == "momentum_stalled"),
        None
    )
    
    # Check for adaptation suggestion
    adaptation_patch = next(
        (s for s in signals 
         if s.agent == "adaptation" and 
         s.payload and 
         "suggested_energy_filter" in s.payload),
        None
    )
    
    if adaptation_patch and adaptation_patch.payload:
        return adaptation_patch.payload.get("suggested_energy_filter")
    
    if low_energy and low_energy.confidence > 0.7:
        return "low"
    
    if momentum_stalled:
        return "low"
    
    if high_energy and high_energy.confidence > 0.8:
        return "high"
    
    return state.current_energy


def build_actions(
    signals: List[AgentSignal],
    state: UserStateProfile
) -> List[AdaptationAction]:
    """
    Convert signals into concrete adaptation actions.
    """
    actions: List[AdaptationAction] = []

    # Rule: low energy → surface easy tasks
    low_energy_signal = next(
        (s for s in signals if s.signal == "low_energy_state" and s.confidence > 0.7),
        None
    )
    if low_energy_signal:
        actions.append(AdaptationAction(
            type="bias_task_suggestions",
            params={"energy_filter": "low", "max_minutes": 30},
            applied=True,
            reason="Flow Agent detected low energy state"
        ))

    # Rule: high energy + peak window → recommend deep work
    high_energy = next(
        (s for s in signals if s.signal == "high_energy_state"),
        None
    )
    peak_window = next(
        (s for s in signals if s.signal == "high_focus_window"),
        None
    )
    
    if high_energy and (
        (high_energy.payload and high_energy.payload.get("in_peak_window")) or
        peak_window
    ):
        actions.append(AdaptationAction(
            type="recommend_deep_work",
            params={"energy_filter": "high"},
            applied=True,
            reason="High energy during known peak focus window"
        ))

    # Rule: overwhelming workspace → suppress unlocks
    overwhelm = next(
        (s for s in signals if s.signal == "likely_overwhelm" and s.confidence > 0.6),
        None
    )
    workspace_too_complex = next(
        (s for s in signals if s.signal == "workspace_too_complex"),
        None
    )
    
    if overwhelm or workspace_too_complex:
        actions.append(AdaptationAction(
            type="suppress_unlock_prompt",
            params={},
            applied=True,
            reason="User is overwhelmed — do not surface new complexity"
        ))

    # Rule: momentum stalled → surface quick win
    momentum_stalled = next(
        (s for s in signals if s.signal == "momentum_stalled"),
        None
    )
    if momentum_stalled:
        actions.append(AdaptationAction(
            type="surface_quick_win",
            params={"energy_filter": "low", "max_minutes": 15},
            applied=True,
            reason="Strategy + Flow agents both suggest momentum needs a restart"
        ))

    # Rule: no check-in yet → nudge
    prompt_checkin = next(
        (s for s in signals if s.signal == "prompt_checkin"),
        None
    )
    if prompt_checkin and state.hour_of_day >= 9:
        actions.append(AdaptationAction(
            type="surface_checkin_prompt",
            params={},
            applied=False,
            reason="Adaptation Agent: no check-in today, energy context missing"
        ))

    # Rule: preference patches need consent
    preference_patches = [
        s for s in signals
        if s.agent == "adaptation" and s.signal == "preference_patch"
    ]
    for patch in preference_patches:
        actions.append(AdaptationAction(
            type="preference_patch_proposed",
            params=patch.payload or {},
            applied=False,
            reason="Adaptation Agent proposal — requires explicit user consent (Phase 1 safety rule)"
        ))

    return actions


def run_orchestrator(
    user_id: str,
    event: str,
    state: UserStateProfile,
    feedback_text: Optional[str] = None
) -> OrchestratorResult:
    """
    Main orchestrator - coordinates all four agents and returns adaptation result.
    
    Args:
        user_id: User identifier
        event: Type of event (dashboard_opened, task_completed, etc.)
        state: User state profile
        feedback_text: Optional recent feedback from user
    
    Returns:
        OrchestratorResult with signals, actions, and recommendations
    """
    
    # Run all agents in parallel (conceptually)
    all_signals: List[AgentSignal] = []
    
    all_signals.extend(run_flow_agent(state))
    all_signals.extend(run_strategy_agent(state))
    all_signals.extend(run_workspace_agent(state))
    all_signals.extend(run_adaptation_agent(state, feedback_text))

    # Sort signals by confidence (highest first)
    signals = sorted(all_signals, key=lambda s: s.confidence, reverse=True)

    # Build actions
    actions = build_actions(signals, state)

    # Determine energy filter
    energy_filter = resolve_energy_filter(signals, state)

    return OrchestratorResult(
        signals=signals,
        actions=actions,
        state_profile=state,
        suggested_energy_filter=energy_filter,
        applied_at=datetime.now().isoformat()
    )
