export type AgentSignal = {
  agent: "flow" | "strategy" | "workspace" | "adaptation";
  signal: string;
  confidence: number;
  summary: string;
  suggestedAction?: string;
  payload?: Record<string, any>;
};

export type UserStateProfile = {
  userId: string;
  tier: number;
  currentEnergy: "high" | "medium" | "low" | null;
  feedbackStyle: "celebratory" | "direct" | "balanced" | null;
  momentumScore: number;
  overwhelmRisk: number;
  workspaceComplexityTolerance: number;
  peakFocusWindows: Array<{ day: string; hour: number; confidence: number }>;
  moduleUsage: Record<string, number>;
  hiddenModules: string[];
  activeModules: string[];
  prioritiesSummary: string[];
  recentWinsCount: number;
  totalIdeas: number;
  completedIdeas: number;
  frictionSignals: string[];
  suggestedWorkMode: "deep" | "light" | "admin" | "planning" | null;
  lastAdaptationAt: string | null;
  hourOfDay: number;
  dayOfWeek: number;
  hasCheckedInToday: boolean;
  recentSprintCount: number;
};

export type AdaptationAction = {
  type: string;
  params?: Record<string, any>;
  applied: boolean;
  reason: string;
};

export type OrchestratorResult = {
  signals: AgentSignal[];
  actions: AdaptationAction[];
  stateProfile: UserStateProfile;
  suggestedEnergyFilter: "high" | "medium" | "low" | null;
  appliedAt: string;
};

export type AdaptiveEvent =
  | "dashboard_opened"
  | "task_completed"
  | "checkin_submitted"
  | "feedback_submitted"
  | "sprint_completed"
  | "tier_unlocked";
