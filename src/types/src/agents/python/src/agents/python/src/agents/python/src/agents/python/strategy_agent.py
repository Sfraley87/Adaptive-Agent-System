from typing import List
from types import UserStateProfile, AgentSignal

def run_strategy_agent(state: UserStateProfile) -> List[AgentSignal]:
    """
    Strategy Agent - Evaluates task priorities, backlog health, and strategic alignment.
    
    Watches:
    - Business priorities
    - Backlog health
    - Recent wins vs priorities
    - Time of week (planning opportunities)
    """
    signals: List[AgentSignal] = []

    # High-value tasks available
    open_tasks = state.total_ideas - state.completed_ideas
    if open_tasks > 0:
        signals.append(AgentSignal(
            agent="strategy",
            signal="high_value_task_available",
            confidence=0.85,
            summary=f"{open_tasks} tasks waiting. Prioritised suggestions are ready.",
            suggested_action="surface_task_suggestions"
        ))

    # Priority alignment check
    if len(state.priorities_summary) == 0:
        signals.append(AgentSignal(
            agent="strategy",
            signal="priorities_not_set",
            confidence=0.95,
            summary="No business priorities defined. Task scoring and suggestions won't be accurate.",
            suggested_action="prompt_priorities_setup"
        ))
    elif len(state.priorities_summary) > 0 and state.recent_wins_count > 0:
        top_priorities = ", ".join(state.priorities_summary[:2])
        signals.append(AgentSignal(
            agent="strategy",
            signal="aligned_progress",
            confidence=0.75,
            summary=f"{state.recent_wins_count} recent wins aligned with priorities: {top_priorities}.",
            suggested_action=None
        ))

    # Backlog health check
    open_ideas = state.total_ideas - state.completed_ideas
    if open_ideas > 20:
        signals.append(AgentSignal(
            agent="strategy",
            signal="idea_backlog_overloaded",
            confidence=0.8,
            summary=f"{open_ideas} open ideas is a lot. Consider a triage session to archive or score lower-priority items.",
            suggested_action="admin_batch_recommended"
        ))

    # No wins recently but tasks exist
    if state.recent_wins_count == 0 and open_ideas > 0:
        signals.append(AgentSignal(
            agent="strategy",
            signal="next_best_action",
            confidence=0.85,
            summary="No wins logged this week but tasks are available. A quick completion would restart momentum.",
            suggested_action="surface_quick_win",
            payload={"recommended_task_type": "low"}
        ))

    # Planning recommendation
    is_monday = state.day_of_week == 1
    is_planning_mode = state.suggested_work_mode == "planning"
    should_recommend_planning = is_planning_mode or (not state.has_checked_in_today and is_monday)
    
    if should_recommend_planning:
        confidence = 0.9 if is_monday else 0.65
        summary = (
            "Monday morning — good time to set the week's intention."
            if is_monday
            else "Low momentum detected. A short planning session could clarify next actions."
        )
        signals.append(AgentSignal(
            agent="strategy",
            signal="planning_session_recommended",
            confidence=confidence,
            summary=summary,
            suggested_action="prompt_weekly_planning"
        ))

    return signals
