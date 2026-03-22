import type { AgentSignal, UserStateProfile } from "../types/adaptive";

export function runWorkspaceAgent(state: UserStateProfile): AgentSignal[] {
  const signals: AgentSignal[] = [];

  // Check if user is ready to unlock next tier
  const canUnlockTier2 = state.tier === 1 && state.recentWinsCount >= 1;
  const canUnlockTier3 = state.tier === 2 && state.recentWinsCount >= 3;
  const canUnlockTier4 = state.tier === 3;

  if (canUnlockTier2) {
    signals.push({
      agent: "workspace",
      signal: "user_ready_for_unlock",
      confidence: 0.95,
      summary: "User has logged their first win. Daily Rituals and Wins are ready to unlock.",
      suggestedAction: "surface_unlock_prompt",
      payload: { nextTier: 2 },
    });
  } else if (canUnlockTier3) {
    signals.push({
      agent: "workspace",
      signal: "user_ready_for_unlock",
      confidence: 0.95,
      summary: "3+ wins logged. Flow Priming, Energy Patterns, and Priorities are ready to unlock.",
      suggestedAction: "surface_unlock_prompt",
      payload: { nextTier: 3 },
    });
  } else if (canUnlockTier4) {
    signals.push({
      agent: "workspace",
      signal: "user_ready_for_unlock",
      confidence: 0.7,
      summary: "User has been using the app consistently. Full toolkit is available on request.",
      suggestedAction: "surface_unlock_prompt",
      payload: { nextTier: 4 },
    });
  }

  // Workspace complexity vs tolerance
  if (state.overwhelmRisk > 0.5 && state.tier >= 3) {
    signals.push({
      agent: "workspace",
      signal: "workspace_too_complex",
      confidence: state.overwhelmRisk,
      summary: "High overwhelm risk with a complex workspace. Consider temporarily simplifying the view.",
      suggestedAction: "simplify_workspace",
    });
  }

  // Healthy workspace
  if (
    state.tier >= 2 &&
    state.overwhelmRisk < 0.3 &&
    state.momentumScore > 0.4 &&
    state.workspaceComplexityTolerance > 0.5
  ) {
    signals.push({
      agent: "workspace",
      signal: "workspace_healthy",
      confidence: 0.8,
      summary: "Workspace complexity matches user tolerance. Good balance.",
    });
  }

  // Underused modules
  const underused = state.activeModules.filter(m => (state.moduleUsage[m] ?? 0) < 2);
  if (underused.length > 2) {
    signals.push({
      agent: "workspace",
      signal: "hide_unused_module",
      confidence: 0.6,
      summary: `Several active modules have low usage: ${underused.join(", ")}. Could declutter the sidebar.`,
      payload: { modules: underused },
    });
  }

  return signals;
}
