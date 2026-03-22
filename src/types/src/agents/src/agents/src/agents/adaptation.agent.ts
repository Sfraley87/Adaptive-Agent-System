import type { AgentSignal, UserStateProfile } from "../types/adaptive";

export function runAdaptationAgent(state: UserStateProfile, recentFeedbackText?: string): AgentSignal[] {
  const signals: AgentSignal[] = [];

  // Friction signals → propose adaptations
  if (state.frictionSignals.includes("idea_backlog_large")) {
    signals.push({
      agent: "adaptation",
      signal: "reduce_complexity",
      confidence: 0.75,
      summary: "Large idea backlog is a known friction point. Filtering tasks by energy type reduces overwhelm.",
      suggestedAction: "enable_energy_filter_default",
    });
  }

  if (state.frictionSignals.includes("win_drought")) {
    signals.push({
      agent: "adaptation",
      signal: "preference_patch",
      confidence: 0.7,
      summary: "No wins for a while. Surface easier tasks more prominently to rebuild momentum.",
      suggestedAction: "lower_default_energy_threshold",
      payload: { suggestedEnergyFilter: "low" },
    });
  }

  if (state.frictionSignals.includes("incomplete_sprints")) {
    signals.push({
      agent: "adaptation",
      signal: "reduce_sprint_duration",
      confidence: 0.65,
      summary: "Multiple incomplete sprints detected. Shorter sprint durations may improve completion rate.",
      suggestedAction: "suggest_shorter_sprints",
      payload: { recommendedMaxDuration: 25 },
    });
  }

  if (state.frictionSignals.includes("no_checkin_today") && state.hourOfDay >= 9) {
    signals.push({
      agent: "adaptation",
      signal: "prompt_checkin",
      confidence: 0.8,
      summary: "No morning check-in yet. Energy context would improve task suggestions.",
      suggestedAction: "surface_checkin_prompt",
    });
  }

  // Feedback text analysis
  if (recentFeedbackText) {
    const text = recentFeedbackText.toLowerCase();

    if (text.includes("overwhelm") || text.includes("too much") || text.includes("complicated")) {
      signals.push({
        agent: "adaptation",
        signal: "reduce_notifications",
        confidence: 0.8,
        summary: "Feedback suggests overwhelm. Workspace simplification recommended.",
        suggestedAction: "simplify_workspace",
      });
    }

    if (text.includes("shorter") || text.includes("quick") || text.includes("sprint")) {
      signals.push({
        agent: "adaptation",
        signal: "preference_patch",
        confidence: 0.75,
        summary: "Feedback implies preference for shorter work sessions.",
        suggestedAction: "reduce_sprint_duration",
        payload: { field: "sprintDurations", hint: "shorter" },
      });
    }

    if (text.includes("dark mode") || text.includes("theme")) {
      signals.push({
        agent: "adaptation",
        signal: "expose_hidden_feature",
        confidence: 0.9,
        summary: "User is requesting a UI feature. Flag for product team.",
        payload: { featureRequest: text },
      });
    }
  }

  // Positive momentum → no disruption needed
  if (state.momentumScore > 0.7 && state.frictionSignals.length === 0) {
    signals.push({
      agent: "adaptation",
      signal: "no_persistent_change_needed",
      confidence: 0.85,
      summary: "User is in flow. No workspace changes recommended — avoid disruption.",
    });
  }

  return signals;
}
