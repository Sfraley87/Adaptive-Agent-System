from typing import List
from types import UserStateProfile, AgentSignal

DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

def run_flow_agent(state: UserStateProfile) -> List[AgentSignal]:
    """
    Flow Agent - Monitors user energy, momentum, and optimal work conditions.
    
    Watches:
    - Current energy level (from daily check-in)
    - Peak focus windows (learned patterns)
    - Momentum (recent wins)
    - Overwhelm risk
    """
    signals: List[AgentSignal] = []

    # Energy state detection
    if state.current_energy == "low":
        signals.append(AgentSignal(
            agent="flow",
            signal="low_energy_state",
            confidence=0.9,
            summary="User reported low energy today. Light, quick tasks will be more sustainable.",
            suggested_action="surface_easy_tasks",
            payload={
                "recommended_task_type": "low",
                "max_minutes": 30
            }
        ))
    
    elif state.current_energy == "high":
        # Check if in peak focus window
        is_peak_window = any(
            w["day"] == DAY_NAMES[state.day_of_week] and
            abs(w["hour"] - state.hour_of_day) <= 1
            for w in state.peak_focus_windows
        )
        
        signals.append(AgentSignal(
            agent="flow",
            signal="high_energy_state",
            confidence=0.95 if is_peak_window else 0.8,
            summary=(
                "High energy AND in a known peak focus window. Prime time for deep work."
                if is_peak_window
                else "User reported high energy. Good conditions for focused work."
            ),
            suggested_action="surface_deep_tasks",
            payload={
                "recommended_task_type": "high",
                "in_peak_window": is_peak_window
            }
        ))

    # Focus window detection (even without check-in)
    if not state.has_checked_in_today and len(state.peak_focus_windows) > 0:
        in_known_peak = any(
            w["day"] == DAY_NAMES[state.day_of_week] and
            abs(w["hour"] - state.hour_of_day) <= 1 and
            w.get("confidence", 0) >= 0.8
            for w in state.peak_focus_windows
        )
        
        if in_known_peak:
            signals.append(AgentSignal(
                agent="flow",
                signal="high_focus_window",
                confidence=0.75,
                summary="Historical patterns show this is a peak focus time, even without today's check-in.",
                suggested_action="suggest_deep_work",
                payload={"hour_of_day": state.hour_of_day}
            ))

    # Overwhelm risk detection
    if state.overwhelm_risk > 0.6:
        signals.append(AgentSignal(
            agent="flow",
            signal="likely_overwhelm",
            confidence=state.overwhelm_risk,
            summary=f"High overwhelm risk ({int(state.overwhelm_risk * 100)}%). Large backlog + low energy = paralysis risk.",
            suggested_action="simplify_task_view",
            payload={
                "open_ideas": state.total_ideas - state.completed_ideas
            }
        ))

    # Momentum detection - building
    if state.momentum_score >= 0.6:
        signals.append(AgentSignal(
            agent="flow",
            signal="momentum_building",
            confidence=state.momentum_score,
            summary=f"Strong recent activity ({state.recent_wins_count} wins this week). Keep the energy going.",
            suggested_action="celebrate_and_continue"
        ))
    
    # Momentum detection - stalled
    elif state.momentum_score < 0.2 and state.recent_wins_count == 0:
        signals.append(AgentSignal(
            agent="flow",
            signal="momentum_stalled",
            confidence=0.8,
            summary="No recent wins. A small, easy task to restart momentum would help.",
            suggested_action="surface_quick_win",
            payload={
                "recommended_task_type": "low",
                "max_minutes": 15
            }
        ))

    # Sprint recommendation
    if state.current_energy != "low" and "incomplete_sprints" not in state.friction_signals:
        signals.append(AgentSignal(
            agent="flow",
            signal="recommend_sprint",
            confidence=0.7,
            summary="Conditions are good for a focused sprint session.",
            suggested_action="prompt_sprint_start"
        ))

    return signals
