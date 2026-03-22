from typing import List, Optional
from types import UserStateProfile, AgentSignal

def run_adaptation_agent(
    state: UserStateProfile,
    recent_feedback_text: Optional[str] = None
) -> List[AgentSignal]:
    """
    Adaptation Agent - Proposes long-term system adaptations based on patterns and feedback.
    
    Watches:
    - Friction signals (win droughts, incomplete sprints, etc.)
    - User feedback text
    - Behavioral patterns
    - Momentum trends
    """
    signals: List[AgentSignal] = []

    # Friction-based adaptations
    if "idea_backlog_large" in state.friction_signals:
        signals.append(AgentSignal(
            agent="adaptation",
            signal="reduce_complexity",
            confidence=0.75,
            summary="Large idea backlog is a known friction point. Filtering tasks by energy type reduces overwhelm.",
            suggested_action="enable_energy_filter_default"
        ))

    if "win_drought" in state.friction_signals:
        signals.append(AgentSignal(
            agent="adaptation",
            signal="preference_patch",
            confidence=0.7,
            summary="No wins for a while. Surface easier tasks more prominently to rebuild momentum.",
            suggested_action="lower_default_energy_threshold",
            payload={"suggested_energy_filter": "low"}
        ))

    if "incomplete_sprints" in state.friction_signals:
        signals.append(AgentSignal(
            agent="adaptation",
            signal="reduce_sprint_duration",
            confidence=0.65,
            summary="Multiple incomplete sprints detected. Shorter sprint durations may improve completion rate.",
            suggested_action="suggest_shorter_sprints",
            payload={"recommended_max_duration": 25}
        ))

    if "no_checkin_today" in state.friction_signals and state.hour_of_day >= 9:
        signals.append(AgentSignal(
            agent="adaptation",
            signal="prompt_checkin",
            confidence=0.8,
            summary="No morning check-in yet. Energy context would improve task suggestions.",
            suggested_action="surface_checkin_prompt"
        ))

    # Feedback text analysis
    if recent_feedback_text:
        text_lower = recent_feedback_text.lower()

        # Overwhelm detection
        overwhelm_keywords = ["overwhelm", "too much", "complicated"]
        if any(keyword in text_lower for keyword in overwhelm_keywords):
            signals.append(AgentSignal(
                agent="adaptation",
                signal="reduce_notifications",
                confidence=0.8,
                summary="Feedback suggests overwhelm. Workspace simplification recommended.",
                suggested_action="simplify_workspace"
            ))

        # Sprint duration preference
        sprint_keywords = ["shorter", "quick", "sprint"]
        if any(keyword in text_lower for keyword in sprint_keywords):
            signals.append(AgentSignal(
                agent="adaptation",
                signal="preference_patch",
                confidence=0.75,
                summary="Feedback implies preference for shorter work sessions.",
                suggested_action="reduce_sprint_duration",
                payload={"field": "sprint_durations", "hint": "shorter"}
            ))

        # Feature request
        theme_keywords = ["dark mode", "theme"]
        if any(keyword in text_lower for keyword in theme_keywords):
            signals.append(AgentSignal(
                agent="adaptation",
                signal="expose_hidden_feature",
                confidence=0.9,
                summary="User is requesting a UI feature. Flag for product team.",
                payload={"feature_request": recent_feedback_text}
            ))

    # Positive momentum → no disruption
    if state.momentum_score > 0.7 and len(state.friction_signals) == 0:
        signals.append(AgentSignal(
            agent="adaptation",
            signal="no_persistent_change_needed",
            confidence=0.85,
            summary="User is in flow. No workspace changes recommended — avoid disruption.",
            suggested_action=None
        ))

    return signals
