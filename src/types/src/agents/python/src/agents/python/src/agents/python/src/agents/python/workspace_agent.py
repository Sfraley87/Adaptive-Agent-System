from typing import List
from types import UserStateProfile, AgentSignal

def run_workspace_agent(state: UserStateProfile) -> List[AgentSignal]:
    """
    Workspace Agent - Manages feature unlocks, UI complexity, and workspace health.
    
    Watches:
    - Feature tier progression
    - Overwhelm risk vs complexity tolerance
    - Module usage patterns
    """
    signals: List[AgentSignal] = []

    # Tier unlock detection
    can_unlock_tier_2 = state.tier == 1 and state.recent_wins_count >= 1
    can_unlock_tier_3 = state.tier == 2 and state.recent_wins_count >= 3
    can_unlock_tier_4 = state.tier == 3

    if can_unlock_tier_2:
        signals.append(AgentSignal(
            agent="workspace",
            signal="user_ready_for_unlock",
            confidence=0.95,
            summary="User has logged their first win. Daily Rituals and Wins are ready to unlock.",
            suggested_action="surface_unlock_prompt",
            payload={"next_tier": 2}
        ))
    
    elif can_unlock_tier_3:
        signals.append(AgentSignal(
            agent="workspace",
            signal="user_ready_for_unlock",
            confidence=0.95,
            summary="3+ wins logged. Flow Priming, Energy Patterns, and Priorities are ready to unlock.",
            suggested_action="surface_unlock_prompt",
            payload={"next_tier": 3}
        ))
    
    elif can_unlock_tier_4:
        signals.append(AgentSignal(
            agent="workspace",
            signal="user_ready_for_unlock",
            confidence=0.7,
            summary="User has been using the app consistently. Full toolkit is available on request.",
            suggested_action="surface_unlock_prompt",
            payload={"next_tier": 4}
        ))

    # Workspace complexity check
    if state.overwhelm_risk > 0.5 and state.tier >= 3:
        signals.append(AgentSignal(
            agent="workspace",
            signal="workspace_too_complex",
            confidence=state.overwhelm_risk,
            summary="High overwhelm risk with a complex workspace. Consider temporarily simplifying the view.",
            suggested_action="simplify_workspace"
        ))

    # Healthy workspace indicator
    if (state.tier >= 2 and
        state.overwhelm_risk < 0.3 and
        state.momentum_score > 0.4 and
        state.workspace_complexity_tolerance > 0.5):
        signals.append(AgentSignal(
            agent="workspace",
            signal="workspace_healthy",
            confidence=0.8,
            summary="Workspace complexity matches user tolerance. Good balance.",
            suggested_action=None
        ))

    # Underused modules detection
    underused = [
        module for module in state.active_modules
        if state.module_usage.get(module, 0) < 2
    ]
    
    if len(underused) > 2:
        modules_str = ", ".join(underused)
        signals.append(AgentSignal(
            agent="workspace",
            signal="hide_unused_module",
            confidence=0.6,
            summary=f"Several active modules have low usage: {modules_str}. Could declutter the sidebar.",
            payload={"modules": underused}
        ))

    return signals
