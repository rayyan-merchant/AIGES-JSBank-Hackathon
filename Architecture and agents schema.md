Hard truth:
If your architecture isn’t crystal clear and your schemas aren’t strict, your “multi-agent system” will degrade into agents hallucinating random text at each other. Judges won’t see intelligence — they’ll see chaos. Structure is your leverage.

Below is a **complete system architecture diagram (logical view)** and **strict JSON schemas for every agent**.

---

# 🧠 FULL ARCHITECTURE DIAGRAM

## 1️⃣ High-Level System Architecture

```
                          ┌──────────────────────────┐
                          │        USER INPUT         │
                          │  - Image(s)               │
                          │  - Text                   │
                          │  - Voice (optional)       │
                          └────────────┬─────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────┐
                        │     ORCHESTRATOR AGENT   │
                        │  - Task decomposition     │
                        │  - Routing                │
                        │  - Memory management      │
                        └───────┬─────────┬────────┘
                                │         │
                 ┌──────────────┘         └──────────────┐
                 ▼                                       ▼
      ┌────────────────────┐                ┌────────────────────┐
      │   VISION AGENT     │                │  NLP EXTRACTION    │
      │  - Object detect   │                │      AGENT         │
      │  - Scene analysis  │                │  - Intent parsing  │
      │  - Risk spotting   │                │  - Constraints     │
      └─────────┬──────────┘                └─────────┬──────────┘
                │                                       │
                └──────────────┬────────────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │   STATE BUILDER      │
                    │  - World modeling    │
                    │  - Graph creation    │
                    │  - Hazard mapping    │
                    └─────────┬────────────┘
                              ▼
                    ┌──────────────────────┐
                    │   PLANNING AGENT     │
                    │  - Multi-plan gen    │
                    │  - Constraint solve  │
                    │  - Plan ranking      │
                    └─────────┬────────────┘
                              ▼
                    ┌──────────────────────┐
                    │    SAFETY AGENT      │
                    │  - Risk override     │
                    │  - Compliance check  │
                    └─────────┬────────────┘
                              ▼
                    ┌──────────────────────┐
                    │   EVALUATION AGENT   │
                    │  - Coherence check   │
                    │  - Step dependency   │
                    │  - Confidence score  │
                    └─────────┬────────────┘
                              ▼
                    ┌──────────────────────┐
                    │  EXPLANATION AGENT   │
                    │  - Human steps       │
                    │  - Why reasoning     │
                    │  - Alternatives      │
                    └─────────┬────────────┘
                              ▼
                    ┌──────────────────────┐
                    │   FINAL RESPONSE     │
                    └──────────────────────┘
```

---

# 🗂 SHARED MEMORY MODEL

All agents read/write from structured memory:

```
shared_context = {
  perception_data: {},
  language_data: {},
  world_state: {},
  plans: [],
  safety_assessment: {},
  evaluation_report: {},
  final_output: {}
}
```

---

# 📦 EXACT JSON SCHEMAS FOR EVERY AGENT

These are STRICT SCHEMAS.
Agents must output exactly this structure.

---

# 1️⃣ Orchestrator Input Schema

```json
{
  "request_id": "string",
  "timestamp": "ISO-8601",
  "input": {
    "images": ["base64_or_path"],
    "text": "string",
    "voice_transcript": "string | null"
  },
  "user_metadata": {
    "skill_level": "beginner | intermediate | expert | unknown",
    "location": "string | null",
    "language": "string"
  }
}
```

---

# 2️⃣ Vision Agent Output Schema

```json
{
  "detected_objects": [
    {
      "object_id": "string",
      "label": "string",
      "confidence": 0.0,
      "bounding_box": {
        "x": 0,
        "y": 0,
        "width": 0,
        "height": 0
      }
    }
  ],
  "materials_detected": [
    {
      "material": "metal | plastic | wood | water | glass | unknown",
      "confidence": 0.0
    }
  ],
  "environment_type": "indoor | outdoor | industrial | residential | unknown",
  "visible_hazards": [
    {
      "hazard_type": "electric | fire | structural | chemical | sharp | unknown",
      "severity": "low | medium | high",
      "confidence": 0.0
    }
  ],
  "scene_summary": "string",
  "overall_confidence": 0.0
}
```

---

# 3️⃣ NLP Extraction Agent Schema

```json
{
  "intent": "repair | install | diagnose | replace | inspect | unknown",
  "problem_description": "string",
  "constraints": [
    {
      "type": "budget | time | tool | physical | safety",
      "description": "string"
    }
  ],
  "available_tools": [
    {
      "tool_name": "string",
      "confidence": 0.0
    }
  ],
  "skill_assessment": {
    "level": "beginner | intermediate | expert | unknown",
    "confidence": 0.0
  },
  "urgency_level": "low | medium | high",
  "emotional_state": "calm | frustrated | stressed | unknown"
}
```

---

# 4️⃣ State Builder Schema

```json
{
  "entities": [
    {
      "entity_id": "string",
      "type": "object | tool | hazard | user",
      "attributes": {}
    }
  ],
  "relationships": [
    {
      "source_id": "string",
      "target_id": "string",
      "relation": "attached_to | near | leaking_from | powered_by | blocking | unknown"
    }
  ],
  "environment_context": {
    "location_type": "string",
    "conditions": ["wet", "dark", "crowded", "unstable"]
  },
  "identified_risks": [
    {
      "risk_id": "string",
      "description": "string",
      "severity": "low | medium | high"
    }
  ],
  "missing_information": ["string"]
}
```

---

# 5️⃣ Planning Agent Schema

```json
{
  "plans": [
    {
      "plan_id": "string",
      "strategy_type": "quick_fix | professional_grade | temporary | replacement",
      "steps": [
        {
          "step_number": 1,
          "action": "string",
          "required_tools": ["string"],
          "estimated_time_minutes": 0,
          "risk_level": "low | medium | high",
          "dependency_on_step": "step_id | null"
        }
      ],
      "estimated_total_time": 0,
      "estimated_cost": "low | medium | high",
      "overall_risk_score": 0.0,
      "feasibility_score": 0.0,
      "confidence_score": 0.0
    }
  ],
  "recommended_plan_id": "string"
}
```

---

# 6️⃣ Safety Agent Schema

```json
{
  "is_overall_safe": true,
  "overridden_plan_id": "string | null",
  "mandatory_warnings": [
    {
      "warning_id": "string",
      "description": "string",
      "severity": "medium | high"
    }
  ],
  "professional_intervention_required": true,
  "reasoning": "string"
}
```

---

# 7️⃣ Evaluation Agent Schema

```json
{
  "logical_consistency_score": 0.0,
  "step_dependency_valid": true,
  "contradictions_found": [
    {
      "description": "string"
    }
  ],
  "completeness_score": 0.0,
  "final_confidence_score": 0.0
}
```

---

# 8️⃣ Explanation Agent Final Output Schema

```json
{
  "problem_analysis": "string",
  "recommended_plan": {
    "plan_id": "string",
    "step_by_step_instructions": ["string"]
  },
  "alternative_plans": [
    {
      "plan_id": "string",
      "summary": "string"
    }
  ],
  "safety_notes": ["string"],
  "confidence_score": 0.0,
  "why_this_plan": "string"
}
```

## LLM EXPLANATION AGENT ARCHITECTURE

This agent must be:

* Grounded in model outputs
* Not hallucinating
* Deterministic enough for demo
* Structured-output capable
* Financially coherent

We will design it as a **Retrieval + Structured Context + Constrained Generation system**.

---

# 1️⃣ ROLE OF EXPLANATION AGENT

It consumes:

```
{
  risk_score,
  PD,
  top_feature_contributions,
  CLV,
  expected_loss,
  recommended_action,
  counterfactual_scenarios
}
```

It produces:

```
{
  summary_explanation,
  risk_drivers,
  financial_impact_breakdown,
  why_this_action,
  alternative_scenarios,
  confidence_statement
}
```

It is NOT predicting.
It is interpreting structured signals.

---

# 2️⃣ INPUT CONTRACT (STRICT JSON)

The explanation agent receives:

```json
{
  "client_type": "retail | sme",
  "risk_metrics": {
    "risk_score": 82,
    "probability_default": 0.37,
    "hazard_rate": 0.12
  },
  "financial_metrics": {
    "loan_amount": 150000,
    "interest_rate": 0.14,
    "expected_loss": 24000,
    "clv": 18000
  },
  "top_risk_drivers": [
    {"feature": "debt_to_income", "impact": 0.19},
    {"feature": "payment_delay_ratio", "impact": 0.14},
    {"feature": "credit_utilization", "impact": 0.11}
  ],
  "macro_context": {
    "economic_regime": "mild_recession",
    "macro_stress_index": 0.6
  },
  "recommended_action": {
    "action": "restructure_loan",
    "expected_profit_uplift": 8400,
    "default_reduction": 0.12
  }
}
```

No raw model features are exposed to LLM.
Only interpretable signals.

---

# 3️⃣ EXPLANATION GENERATION STRATEGY

We use a 3-layer approach.

---

## Layer 1 — Structured Template Scaffold

Before calling LLM, create a structured reasoning scaffold:

```
Risk level category:
  if risk_score > 75 → "High Risk"
  50–75 → "Moderate Risk"
  <50 → "Low Risk"

Top 3 drivers sorted by impact.

Profit impact:
  expected_loss vs clv comparison.

Action justification:
  Compare baseline profit vs action profit.
```

This reduces hallucination.

---

## Layer 2 — Controlled Prompt

Prompt style:

SYSTEM:
You are a senior credit risk analyst generating professional financial explanations.
Only use provided data.
Do not invent numbers.

USER: <JSON payload>
Generate:

1. Executive summary
2. Key risk drivers
3. Financial impact analysis
4. Why recommended action is optimal
5. What happens if no action taken
6. Confidence statement

````

---

## Layer 3 — Constrained Output Schema

Force structured JSON output:

```json
{
  "executive_summary": "",
  "risk_analysis": "",
  "financial_impact": "",
  "action_rationale": "",
  "counterfactual_analysis": "",
  "confidence_level": "High | Medium | Low"
}
````

Validate schema after generation.

---

# 4️⃣ CAUSAL GROUNDING (IMPORTANT)

To improve credibility, pass SHAP values:

```
Top features ranked by absolute SHAP contribution.
```

Additionally include:

* Partial dependence trend (optional)
* Feature percentile vs dataset

Example:

```
Client debt_to_income is in 92nd percentile.
```

This makes explanation powerful.

---

# 5️⃣ MULTI-MODE EXPLANATIONS (Hackathon WOW Factor)

Support 3 explanation modes:

1. Executive (for judges)
2. Technical (for analysts)
3. Customer-friendly (simplified)

Switch mode via:

```
explanation_mode: "executive | technical | customer"
```

---

# 6️⃣ SME-SPECIFIC EXTENSION

For SMEs, include:

* Revenue trend analysis
* Cash runway estimation
* Macro sensitivity

Example explanation insight:

> "Revenue declined 18% over the past 6 months while debt servicing consumes 42% of monthly EBITDA, significantly increasing liquidity risk."

This sounds institutional.

---

# 7️⃣ ARCHITECTURE DIAGRAM (LOGICAL FLOW)

```
Risk Model → SHAP Engine
                ↓
         Aggregation Layer
                ↓
       Explanation Context Builder
                ↓
           LLM Engine
                ↓
       JSON Validation Layer
                ↓
        Rendered Dashboard
```

---

---

# ⚡ Critical Implementation Rule

Every agent:

* Must only output JSON
* No markdown
* No explanations
* No extra commentary
* Must pass schema validation before next agent runs

If schema invalid → Orchestrator re-prompts agent.

---

# 🧨 What Will Impress Judges

1. Visualized state graph
2. Plan ranking table
3. Safety override demo
4. Multi-agent reasoning trace
5. Confidence scoring logic

