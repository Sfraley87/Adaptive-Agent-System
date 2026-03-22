"""
Example: Using the Adaptive Agent System in Python

This shows how to use the orchestrator in a Python application.
"""

from datetime import datetime
from src.agents.python.types import UserStateProfile
from src.agents.python.orchestrator import run_orchestrator


def create_mock_user_state() -> UserStateProfile:
    """Create a mock user state for demonstration."""
    return UserStateProfile(
        user_id="user_001",
        tier=2,
        current_energy="low",
        feedback_style="balanced",
        momentum_score=0.2,
        overwhelm_risk=0.65,
        workspace_complexity_tolerance=0.5,
        peak_focus_windows=[
            {"day": "Monday", "hour": 10, "confidence": 0.85},
            {"day": "Wednesday", "hour": 14, "confidence": 0.8},
        ],
        module_usage={
            "dashboard": 10,
            "ideas": 5,
            "chat": 2,
            "wins": 1,
            "rituals": 0,
        },
        hidden_modules=["priming", "energy", "crm"],
        active_modules=["dashboard", "ideas", "chat", "wins"],
        priorities_summary=["Launch v2", "Customer Success"],
        recent_wins_count=0,
        total_ideas=25,
        completed_ideas=8,
        friction_signals=["win_drought", "idea_backlog_large"],
        suggested_work_mode="light",
        last_adaptation_at=None,
        hour_of_day=9,
        day_of_week=1,  # Monday
        has_checked_in_today=False,
        recent_sprint_count=2,
    )


def demo_basic_orchestration():
    """Demo 1: Basic orchestration run."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Orchestration")
    print("="*70)

    state = create_mock_user_state()
    result = run_orchestrator(
        user_id="user_001",
        event="dashboard_opened",
        state=state
    )

    print(f"\n📊 User State Summary:")
    print(f"  - Energy: {state.current_energy}")
    print(f"  - Momentum: {state.momentum_score * 100:.0f}%")
    print(f"  - Overwhelm Risk: {state.overwhelm_risk * 100:.0f}%")
    print(f"  - Open Tasks: {state.total_ideas - state.completed_ideas}")

    print(f"\n🧠 Agent Signals (sorted by confidence):")
    for signal in result.signals[:5]:  # Top 5
        emoji = {
            "flow": "🌊",
            "strategy": "🎯",
            "workspace": "🎛️",
            "adaptation": "🔄"
        }.get(signal.agent, "❓")
        
        print(f"\n  {emoji} [{signal.agent}] {signal.signal}")
        print(f"     Confidence: {signal.confidence:.0%}")
        print(f"     Summary: {signal.summary}")
        if signal.suggested_action:
            print(f"     Action: {signal.suggested_action}")

    print(f"\n⚡ Recommended Actions:")
    for action in result.actions:
        status = "✓ APPLY" if action.applied else "ℹ PROPOSE"
        print(f"  [{status}] {action.type}")
        print(f"       {action.reason}")

    print(f"\n💡 Energy Filter: {result.suggested_energy_filter}")
    print(f"🕐 Orchestration completed at: {result.applied_at}")


def demo_with_feedback():
    """Demo 2: Orchestration with user feedback."""
    print("\n" + "="*70)
    print("DEMO 2: Orchestration with Feedback Analysis")
    print("="*70)

    state = create_mock_user_state()
    feedback = "I feel really overwhelmed, there are too many tasks and the interface is too complicated"

    result = run_orchestrator(
        user_id="user_001",
        event="feedback_submitted",
        state=state,
        feedback_text=feedback
    )

    print(f"\n💬 User Feedback: '{feedback}'")
    print(f"\n🔍 Adaptation Agent Analysis:")
    
    adaptation_signals = [s for s in result.signals if s.agent == "adaptation"]
    for signal in adaptation_signals:
        print(f"\n  🔄 {signal.signal}")
        print(f"     Confidence: {signal.confidence:.0%}")
        print(f"     Summary: {signal.summary}")

    print(f"\n🛡️  Safety Measures (Auto-Applied):")
    for action in result.actions:
        if action.applied:
            print(f"  ✓ {action.type}: {action.reason}")

    print(f"\n📝 Proposed Changes (Require User Approval):")
    for action in result.actions:
        if not action.applied:
            print(f"  ? {action.type}: {action.reason}")


def demo_signal_breakdown_by_agent():
    """Demo 3: See what each agent detected."""
    print("\n" + "="*70)
    print("DEMO 3: Signal Breakdown by Agent")
    print("="*70)

    state = create_mock_user_state()
    result = run_orchestrator(
        user_id="user_001",
        event="dashboard_opened",
        state=state
    )

    # Group signals by agent
    signals_by_agent = {}
    for signal in result.signals:
        if signal.agent not in signals_by_agent:
            signals_by_agent[signal.agent] = []
        signals_by_agent[signal.agent].append(signal)

    for agent_name in ["flow", "strategy", "workspace", "adaptation"]:
        emoji = {
            "flow": "🌊",
            "strategy": "🎯",
            "workspace": "🎛️",
            "adaptation": "🔄"
        }[agent_name]
        
        signals = signals_by_agent.get(agent_name, [])
        print(f"\n{emoji} {agent_name.upper()}: ({len(signals)} signals)")
        
        for signal in signals:
            print(f"   • {signal.signal} (confidence: {signal.confidence:.0%})")
            print(f"     → {signal.summary[:60]}...")


if __name__ == "__main__":
    print("\n🤖 Adaptive Agent System - Python Examples")
    print("="*70)

    # Run demos
    demo_basic_orchestration()
    demo_with_feedback()
    demo_signal_breakdown_by_agent()

    print("\n" + "="*70)
    print("✨ Orchestration Examples Complete!")
    print("="*70 + "\n")
