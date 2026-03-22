# Adaptive Agent System - Architecture Deep Dive

## The Problem We Solve

Traditional adaptive systems hit a wall:
- **Too many rules** → Each new feature requires updating 10 other rules
- **Hard to debug** → Why did the app make that decision? Nobody knows
- **Brittle** → Change one rule, break three others
- **Not scalable** → Works for 5 rules, nightmare for 50

**Our Solution:** Let independent agents vote, not fight.

---

## Core Concept: Signal-Based Orchestration

Instead of:
```typescript
// ❌ Traditional (spaghetti)
if (lowEnergy && noWins && manyTasks && isMonday && !checkedIn) {
  // This one line has 5 dependencies, touching 3 different concerns
  showEasyTasks();
}
```

We do:
```typescript
// ✅ Our way (clean orchestration)
Flow Agent → "low_energy_state" (confidence: 0.9)
Strategy Agent → "next_best_action" (confidence: 0.85)
Workspace Agent → "workspace_healthy" (confidence: 0.8)
Adaptation Agent → "no_change_needed" (confidence: 0.75)

Orchestrator: "Okay, Flow wins. Show easy tasks."
```

**Benefits:**
- Each agent is independent (can test separately)
- Confidence automatically breaks ties (no hard-coded priorities)
- Observable (you can see exactly why a decision was made)
- Extensible (add a 5th agent? Just works)

---

## The Four Agents Explained

### 1️⃣ Flow Agent 🌊 - "How is the user feeling right now?"

**What it monitors:**
- Current energy level (from daily check-in: high/medium/low)
- Peak focus windows (learned from historical patterns)
- Momentum (recent wins in past 3 days)
- Overwhelm risk (too many tasks + low energy = danger)

**What it recommends:**
- "Low energy? Surface 15-minute tasks only"
- "High energy + peak window? Now's the time for deep work"
- "No wins? Here's an easy win to restart momentum"
- "Overwhelmed? Simplify the view"

**Example Signal:**
```typescript
{
  agent: "flow",
  signal: "momentum_stalled",
  confidence: 0.8,  // Pretty sure about this
  summary: "No wins in 3 days. Need a quick win to restart.",
  suggestedAction: "surface_quick_win"
}
```

---

### 2️⃣ Strategy Agent 🎯 - "What should the user work on?"

**What it monitors:**
- Business priorities (user-defined goals)
- Task backlog health (is it overloaded?)
- Recent wins vs. priorities (are we aligned?)
- Time of week (Monday = planning time)

**What it recommends:**
- "No priorities? Set those first"
- "Backlog has 25 items? Time to triage"
- "Wins aligned with priorities? Keep going!"
- "Monday morning? Plan the week"

**Example Signal:**
```typescript
{
  agent: "strategy",
  signal: "idea_backlog_overloaded",
  confidence: 0.8,
  summary: "28 open tasks. Consider archiving old ones.",
  suggestedAction: "admin_batch_recommended"
}
```

---

### 3️⃣ Workspace Agent 🎛️ - "Should we unlock new features?"

**What it monitors:**
- Feature tier (1-4, more features as user proves ready)
- Recent achievements (wins)
- Cognitive load (overwhelm risk)
- Feature usage (is this module even used?)

**What it recommends:**
- "Got your first win? Unlock Daily Rituals"
- "Got 3 wins? Unlock Flow Priming"
- "Overwhelmed? Hide advanced features"
- "That module unused for weeks? Hide it"

**Example Signal:**
```typescript
{
  agent: "workspace",
  signal: "user_ready_for_unlock",
  confidence: 0.95,  // Very confident!
  summary: "First win achieved. Ready for tier 2 features.",
  suggestedAction: "surface_unlock_prompt",
  payload: { nextTier: 2 }
}
```

---

### 4️⃣ Adaptation Agent 🔄 - "Should we change settings?"

**What it monitors:**
- Friction signals (win droughts, incomplete sprints, etc.)
- User feedback text (keyword matching)
- Behavioral patterns (what's working, what isn't)
- Momentum trends (is the user stable?)

**What it recommends:**
- "No wins? Lower the task difficulty filter"
- "Many incomplete sprints? Suggest shorter ones"
- "User said 'overwhelmed'? Simplify UI"
- "In flow state? Don't change anything!"

**Example Signal:**
```typescript
{
  agent: "adaptation",
  signal: "preference_patch",
  confidence: 0.7,
  summary: "No wins in 5 days. Suggest lowering energy filter.",
  suggestedAction: "lower_default_energy_threshold",
  payload: { suggestedEnergyFilter: "low" },
  applied: false  // Needs user approval!
}
```

---

## How Orchestration Works

### Step 1: Build User State
```
Query database for:
- Energy level (from today's check-in)
- Recent accomplishments (past 7 days)
- All ideas + completion status
- Business priorities
- Historical patterns
- Sprint sessions

Result: UserStateProfile with everything we know
```

### Step 2: Run All Agents (in parallel)
```
Flow Agent → "What signals from psychology?"
Strategy Agent → "What signals from priorities?"
Workspace Agent → "What signals from features?"
Adaptation Agent → "What signals from learning?"

Result: ~15-20 signals, each with confidence
```

### Step 3: Sort by Confidence
```
Signals before:
- flow: "high_energy" (0.9)
- strategy: "backlog_overloaded" (0.8)
- workspace: "workspace_healthy" (0.8)
- adaptation: "no_change" (0.85)

After sorting:
1. flow: "high_energy" (0.9) ← wins
2. adaptation: "no_change" (0.85)
3. strategy: "backlog_overloaded" (0.8)
4. workspace: "workspace_healthy" (0.8)
```

### Step 4: Convert to Actions
```
"High energy in peak window?"
→ Action: "recommend_deep_work"
→ Applied: true (safe, no side effects)

"Preference patch proposed?"
→ Action: "preference_patch_proposed"
→ Applied: false (needs user consent)
```

### Step 5: Return to App
```typescript
{
  signals: [...all signals...],
  actions: [
    { type: "recommend_deep_work", applied: true },
    { type: "suppress_unlock_prompt", applied: true },
  ],
  stateProfile: { /* full user state */ },
  suggestedEnergyFilter: "high",
  appliedAt: "2024-03-22T14:30:00Z"
}
```

---

## Safety & Philosophy

### Phase 1: No Auto-Apply of Preferences
- UI changes → Auto-apply (safe)
- Preference patches → Require user consent

This prevents "system changing behavior behind my back" feeling.

### Observable & Auditable
Every decision includes:
- **Which agent made it**
- **The confidence level**
- **The reasoning** (summary)
- **What action it triggered**

Debug nightmares become simple: "Why did it do that?" → Look at the signal.

### Graceful Degradation
Missing data? No problem:
- No energy check-in → Use historical patterns
- No historical patterns → Assume neutral
- No priorities → Still make suggestions

System works even with sparse data.

---

## Real-World Example: Monday Morning

**Time:** 9 AM Monday
**User state:**
- Energy: high
- Momentum: 0.4 (2 wins last week)
- Open tasks: 15
- Priorities: "Launch v2", "Customer success"
- Historical peak window: Monday 10-11 AM

**Agent signals:**

```
🌊 Flow Agent:
  ✓ high_energy_state (confidence: 0.8)
    "Not in peak window yet, but energy is good"
  ✓ high_focus_window (confidence: 0.75)
    "Historical data: Monday 10-11 AM is peak focus"

🎯 Strategy Agent:
  ✓ planning_session_recommended (confidence: 0.9)
    "Monday morning is planning time"
  ✓ high_value_task_available (confidence: 0.85)
    "15 tasks waiting, prioritized suggestions ready"

🎛️ Workspace Agent:
  ✓ workspace_healthy (confidence: 0.8)
    "Good balance of features and user tolerance"

🔄 Adaptation Agent:
  ✓ no_persistent_change_needed (confidence: 0.75)
    "Momentum is building, no changes recommended"
```

**Orchestrator decision:**
1. Sort by confidence
2. Strategy wins with 0.9 (planning_session_recommended)
3. But Flow's peak window is also high (0.75)
4. Flow's high_energy (0.8) supports it

**Result:**
```json
{
  "actions": [
    {
      "type": "prompt_weekly_planning",
      "applied": true,
      "reason": "Monday morning + good energy + momentum building"
    },
    {
      "type": "surface_peak_focus_hint",
      "applied": true,
      "reason": "Historical peak window in 1 hour (10 AM)"
    }
  ],
  "suggestedEnergyFilter": "high",
  "summary": "Plan your week now, then deep work at 10 AM"
}
```

**App response:**
- Shows planning prompt
- Highlights "next hour is your peak focus time"
- Surfaces high-energy tasks
- Unlocks nothing (workspace healthy)

---

## Why This Pattern Works

| Problem | Traditional | Our System |
|---------|-------------|-----------|
| Adding new logic | Update 5 rules | Create one new agent |
| Debugging decisions | "Why did this happen?" 😤 | "Flow said X with 0.9 confidence" ✅ |
| Conflicting rules | Explicit priorities, brittle | Confidence auto-resolves |
| Testing | Integration hell | Test each agent independently |
| Scaling | More rules = exponential complexity | More agents = linear complexity |
| Observability | Black box | Fully transparent signals |

---

## Future Extensions

The system is built to scale:

```typescript
// Add a "Performance Agent" - monitors system metrics
function runPerformanceAgent(state): AgentSignal[] {
  if (appLatency > 500ms) {
    return [{
      agent: "performance",
      signal: "high_latency",
      confidence: 0.85,
      suggestedAction: "suggest_offline_mode"
    }];
  }
  return [];
}

// Add to orchestrator, everything else works automatically
```

Or a "Social Agent", "Health Agent", "Finance Agent" — all independent, all coordinate through confidence.

---

This is production-ready AI architecture. ✨
