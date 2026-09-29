# Hackathon Demo Video Script & Walkthrough (3–5 Minutes)

This script is structured to maximize points across all judging criteria:
- **Investigation accuracy (30%)**
- **Evidence quality & explainability (15%)**
- **Agentic effectiveness & efficiency (15%)**
- **Agentic design, engineering & code quality (15%)**
- **Innovation (15%)**
- **Final presentation & Q&A (10%)**

---

## 🎬 Video Recording Plan

### Minute 0:00 – 0:45: The Problem & The Core Question
- **Visual**: Show the Metrics Dashboard Header with TigerGraph connected and the ROI callout card.
- **Script**:
  > *"Welcome judges. In this hackathon, our goal wasn't just to build an agent—it was to answer the fundamental industry question: **When does complex retrieval actually need an agent, and when is it overkill?**
  >
  > Standard RAG is fast, but it treats text chunks in isolation. GraphRAG adds structure, but standard fixed traversals can't reason across conditions. We built an autonomous **Agentic GraphRAG System** powered by TigerGraph, evaluated on all 100 benchmark questions and 50 hidden questions over a 5.4-million-token Olympic corpus."*

---

### Minute 0:45 – 1:45: The Architecture & TigerGraph Integration
- **Visual**: Switch to `docs/architecture.md` or the TigerGraph Subgraph Explorer tab.
- **Script**:
  > *"Here is our system architecture:
  >
  > 1. At the base layer, 2,951 documents are indexed in both **TigerGraph Savanna (OlympicGraph)** and a dense FAISS vector index.
  > 2. Incoming queries first enter our **Query Complexity Router**, which determines whether an agent is actually required.
  > 3. If required, our **Agent Orchestrator** manages state, dynamic tool dispatch across 8 specialized tools (including `TemporalReasonerTool`, `AggregationReasonerTool`, and `VenueDateSearchTool`), and records an observable trace in our **Agent Harness**.
  > 4. Before returning, the **EvidenceValidatorTool** validates grounding and fact sufficiency against the source corpus."*

---

### Minute 1:45 – 3:00: Live 3-Way Benchmark Comparison & Agentic Trace
- **Visual**: Switch to the **⚡ Live 3-Way Playground** tab on the Dashboard.
- **Action**:
  1. Click the **Aggregation Query Preset**: *"According to the provided corpus, how many biathlon events at the 2018 Winter Olympics had more than 73 competitors?"*
  2. Click **Benchmark All 3**.
  3. Show the live results:
     - **Standard RAG**: Retrieves a chunk and guesses an event title (Wrong / 0% EM).
     - **GraphRAG**: Links entities, but fixed 1-hop traversal fails to aggregate across vertices (0% EM).
     - **Agentic GraphRAG**: Accurately outputs **5** with Grounding PASS in 19 ms!
  4. Switch to the **🕵️ Agentic Trace Inspector** tab to show:
     - Step 1: Query classification as aggregation.
     - Step 2: Dynamic tool selection of `AggregationReasonerTool`.
     - Step 3: Graph aggregation filtering vertices where `competitors > 73`.
     - Step 4: Evidence validation and stopping criteria satisfaction.
- **Action 2 (Overkill Demo)**:
  1. Click **Direct Lookup**: *"How many nations competed in Swimming at the 2016 Summer Olympics – Men's 100 metre butterfly?"*
  2. Explain:
     > *"Notice that for direct lookups, the router recognizes an agent is NOT required. Standard RAG answers with 65% lower latency and 40% fewer tokens. This proves our system intelligently prevents agent overkill!"*

---

### Minute 3:00 – 4:00: Benchmark Results & Deliverables Summary
- **Visual**: Switch to **📊 Benchmark Overview** and **📋 100-Question Benchmark Data** tabs.
- **Script**:
  > *"Looking at our full 100-question evaluation:
  > - On **Aggregation**, Agentic GraphRAG achieves **57.1% EM vs 0% for RAG and GraphRAG**.
  > - On **Superlatives**, it reaches **60.0% EM vs 20% for baseline RAG**.
  > - Our **50 hidden questions** have been fully predicted and exported to `submission_eval_hidden_output.jsonl` with complete agentic traces, token breakdowns, and citations.
  >
  > Everything is open-source, fully reproducible with 1-click launch scripts, and backed by TigerGraph GSQL schemas."*

---

### Minute 4:00 – 4:15: Conclusion
- **Script**:
  > *"Thank you to the TigerGraph team for this incredible challenge. We look forward to Round 2!"*
