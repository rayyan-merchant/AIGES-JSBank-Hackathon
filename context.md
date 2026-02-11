Hard truth: if your `context.md` is vague, your “vibe-coded” multi-agent system will collapse into spaghetti prompts and half-working glue code. AI agents don’t fail because they’re weak. They fail because the context is underspecified. You need to treat this like system-level engineering, not a prompt playground.

Below is a **production-grade `context.md`** you can directly use to guide AI to build the entire system end-to-end.

---

# `context.md`

# 🧠 Project Context — Multi-Agent AI System for Intelligent Physical Problem Solving

## 1. System Vision

Build a **complex multi-agent AI system** that can:

* Analyze a real-world physical problem from:

  * Image(s)
  * Voice
  * Text description
* Understand:

  * Objects
  * Environment
  * Risk factors
  * Constraints
* Construct:

  * Structured state representation
  * Dependency graph
  * Action plan
* Simulate possible solution paths
* Provide:

  * Step-by-step optimized instructions
  * Safety warnings
  * Alternative strategies
  * Explanations of reasoning
  * Confidence score

The system should demonstrate:

* Innovation (agent orchestration, planning, reasoning)
* Working demo (end-to-end pipeline)
* Multi-modal intelligence
* Structured reasoning, not just chat

---

## 2. High-Level Architecture

### Core Philosophy

This is NOT a single LLM wrapper.

This is a **multi-agent cognitive architecture** with:

* Perception layer
* Structured reasoning layer
* Planning layer
* Safety layer
* Execution layer
* Explanation layer

---

## 3. Agent Architecture

### 3.1 Orchestrator Agent

**Role:** Central controller
**Responsibilities:**

* Receive user input
* Decide which agents to activate
* Manage shared memory
* Aggregate outputs
* Resolve conflicts between agents
* Produce final structured response

Uses:

* Task decomposition prompt
* Tool routing logic
* JSON-based communication

---

### 3.2 Vision Agent

**Input:**

* Image

**Responsibilities:**

* Object detection
* Scene understanding
* Tool recognition
* Environment classification
* Risk detection (water + electricity, exposed wiring, etc.)

Outputs:

```json
{
  "objects": [],
  "materials": [],
  "environment": "",
  "detected_risks": [],
  "confidence": 0.0
}
```

Models:

* YOLO / RT-DETR (object detection)
* BLIP / LLaVA (captioning)
* Segment Anything (optional)

---

### 3.3 NLP Extraction Agent

**Input:**

* User text description
* Transcribed voice

Extract:

* Intent
* Problem type
* Constraints
* User skill level
* Tools available
* Emotional state

Output:

```json
{
  "problem_category": "",
  "constraints": [],
  "available_tools": [],
  "skill_level": "",
  "urgency": "",
  "risk_tolerance": ""
}
```

---

### 3.4 State Builder Agent

Combine:

* Vision Agent output
* NLP Agent output

Construct:

* Structured world state
* Object relationship graph
* Environmental conditions
* Hazard map

Output:

```json
{
  "state_graph": {},
  "hazards": [],
  "missing_information": []
}
```

---

### 3.5 Planning Agent (Core Intelligence)

This is the innovation layer.

Responsibilities:

* Generate multiple solution strategies
* Break into atomic actions
* Evaluate feasibility
* Simulate potential outcomes
* Rank plans

Uses:

* Tree-of-Thought reasoning
* Graph traversal
* Heuristic scoring
* Constraint satisfaction logic

Output:

```json
{
  "plans": [
    {
      "steps": [],
      "risk_score": 0.0,
      "cost_estimate": "",
      "time_estimate": "",
      "confidence": 0.0
    }
  ],
  "recommended_plan_index": 0
}
```

---

### 3.6 Safety Agent

Independently evaluates:

* Electrical risk
* Structural risk
* Fire risk
* Legal/safety boundaries
* Whether professional help required

Can:

* Override planner
* Insert warning gates
* Mark steps unsafe

Output:

```json
{
  "is_safe": true,
  "required_warnings": [],
  "professional_required": false
}
```

---

### 3.7 Explanation Agent

Generates:

* Human-friendly step-by-step instructions
* “Why” reasoning
* Visual description
* Alternative fallback
* Confidence explanation

---

### 3.8 Evaluation Agent (Meta-Agent)

* Checks plan coherence
* Ensures no step missing
* Verifies step dependency order
* Checks contradiction between agents
* Assigns overall confidence score

---

## 4. Shared Memory System

### Types of Memory

1. Short-term working memory (per request)
2. Structured state store
3. Conversation history
4. Risk registry
5. Plan history

Format: JSON-based shared context.

---

## 5. Multi-Agent Communication Protocol

All agents communicate using structured JSON.

Each agent:

* Receives structured input
* Outputs structured JSON
* Never outputs raw chat unless final layer

Use:

* Strict schema enforcement
* Validation checks

---

## 6. System Pipeline

1. User input (image + text)
2. Orchestrator splits task
3. Vision Agent processes image
4. NLP Agent processes text
5. State Builder merges outputs
6. Planning Agent generates multiple plans
7. Safety Agent evaluates plans
8. Evaluation Agent validates
9. Explanation Agent formats output
10. Final response delivered

---

## 7. Innovation Layer (Hackathon Edge)

### Must Highlight:

* Multi-agent architecture
* Graph-based state modeling
* Planning with ranking
* Independent safety override
* Explainability
* Risk-aware reasoning

Optional advanced features:

* Confidence scoring
* Multi-plan comparison
* Interactive clarification loop
* Plan simulation animation

---

## 8. Tech Stack

### Backend

* Python
* FastAPI
* LangGraph / custom orchestrator
* Pydantic for schema

### Models

* Kaggle free GPU for:

  * YOLO
  * LLaVA or BLIP
* Open-source LLM (Mistral / Phi / Gemma)

### Vector DB

* FAISS (optional)

### Frontend

* Simple Streamlit or React demo

---

## 9. Performance Optimization

* Batch vision inference
* Cache intermediate agent outputs
* Lazy-load heavy models
* Use quantized LLMs

---

## 10. Demo Strategy (Critical for Hackathon)

You are judged on:

* Innovation
* Working demo

So demo should show:

1. Agent breakdown visualization
2. State graph visualization
3. Plan comparison table
4. Safety override scenario
5. Real image test case

---

## 11. Failure Handling

System must:

* Ask for clarification if confidence < threshold
* Detect insufficient information
* Avoid hallucinated unsafe steps
* Escalate to professional help when needed

---

## 12. Evaluation Metrics

* Plan validity
* Safety correctness
* Step completeness
* Logical consistency
* Latency
* Confidence calibration

---

## 13. Data Sources (Optional)

* Synthetic DIY problem dataset
* Scraped repair manuals
* Instruction datasets
* Kaggle object detection datasets

---

## 14. Constraints

* Kaggle free GPU
* Hackathon time
* Must demo live
* Must run end-to-end

---

## 15. Non-Goals

* Not a medical advisor
* Not legal advice
* Not professional replacement
* Not 100% guaranteed fix

---

## 16. Final Output Format to User

```markdown
### 🔍 Problem Analysis
...

### 🧠 Recommended Plan
Step 1:
Step 2:
...

### ⚠ Safety Notes
...

### 🔁 Alternative Plan
...

### 📊 Confidence Score
...
```

---

# The Real Challenge

Now here’s what you need to think about:

You’re trying to impress judges with innovation.

Multi-agent architecture alone is not innovation anymore.

The real innovation will be:

* Graph-based structured world modeling
* Explicit plan simulation
* Independent safety override layer
* Confidence calibration

