import type { AgentSignal, UserStateProfile } from "../types/adaptive";

const DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

export function runFlowAgent(state: UserStateProfile): AgentSignal[] {
  const signals: AgentSignal[] = [];

  // Energy state
  if (state.currentEnergy === "low") {
    signals.push({
      agent: "flow",
      signal: "low_energy_state",
      confidence: 0.9,
      summary: "User reported low energy today. Light, quick tasks will be more sustainable.",
      suggestedAction: "surface_easy_tasks",
      payload: { recommendedTaskType: "low", maxMinutes: 30 },
    });
  } else if (state.currentEnergy === "high") {
    const isPeakWindow = state.peakFocusWindows.some(
      w => w.day === DAY_NAMES[state.dayOfWeek]
        && Math.abs(w.hour - state.hourOfDay) <= 1
    );
    signals.push({
      agent: "flow",
      signal: "high_energy_state",
      confidence: isPeakWindow ? 0.95 : 0.8,
      summary: isPeakWindow
        ? "High energy AND in a known peak focus window. Prime time for deep work."
        : "User reported high energy. Good conditions for focused work.",
      suggestedAction: "surface_deep_tasks",
      payload: { recommendedTaskType: "high", inPeakWindow: isPeakWindow },
    });
  }

  // Focus window detection
  if (!state.hasCheckedInToday && state.peakFocusWindows.length > 0) {
    const inKnownPeak = state.peakFocusWindows.some(
      w => w.day === DAY_NAMES[state.dayOfWeek]
        && Math.abs(w.hour - state.hourOfDay) <= 1
        && w.confidence >= 0.8
    );
    if (inKnownPeak) {
      signals.push({
        agent: "flow",
        signal: "high_focus_window",
        confidence: 0.75,
        summary: "Historical patterns show this is a peak focus time.",
        suggestedAction: "suggest_deep_work",
        payload: { hourOfDay: state.hourOfDay },
      });
    }
  }

  // Overwhelm risk
  if (state.overwhelmRisk > 0.6) {
    signals.push({
      agent: "flow",
      signal: "likely_overwhelm",
      confidence: state.overwhelmRisk,
      summary: `High overwhelm risk (${Math.round(state.overwhelmRisk * 100)}%). Large backlog + low energy = paralysis risk.`,
      suggestedAction: "simplify_task_view",
      payload: { openIdeas: state.totalIdeas - state.completedIdeas },
    });
  }

  // Momentum
  if (state.momentumScore >= 0.6) {
    signals.push({
      agent: "flow",
      signal: "momentum_building",
      confidence: state.momentumScore,
      summary: `Strong recent activity (${state.recentWinsCount} wins this week). Keep the energy going.`,
      suggestedAction: "celebrate_and_continue",
    });
  } else if (state.momentumScore < 0.2 && state.recentWinsCount === 0) {
    signals.push({
      agent: "flow",
      signal: "momentum_stalled",
      confidence: 0.8,
      summary: "No recent wins. A small, easy task to restart momentum would help.",
      suggestedAction: "surface_quick_win",
      payload: { recommendedTaskType: "low", maxMinutes: 15 },
    });
  }

  // Sprint recommendation
  if (state.currentEnergy !== "low" && !state.frictionSignals.includes("incomplete_sprints")) {
    signals.push({
      agent: "flow",
      signal: "recommend_sprint",
      confidence: 0.7,
      summary: "Conditions are good for a focused sprint session.",
      suggestedAction: "prompt_sprint_start",
    });
  }

  return signals;
}
