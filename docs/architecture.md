# TigerGraph Agentic GraphRAG: System Architecture & Design

This document details the architectural specification for the **TigerGraph Agentic GraphRAG System**, engineered for the **Agentic GraphRAG Hackathon by TigerGraph**.

---

## 1. High-Level System Architecture

![TigerGraph Agentic GraphRAG System Architecture](architecture_diagram.svg)

The system benchmarks three parallel retrieval paradigms over a corpus of 2,951 Wikipedia documents, indexed simultaneously into a **TigerGraph Knowledge Graph (OlympicGraph)** and a dense **FAISS Vector Index**.

```mermaid
flowchart TD
    subgraph Data_Layer ["Data Ingestion & Storage Layer"]
        Corpus[("Corpus\n2,951 Documents\n~5.4M Tokens")]
        FAISS[("FAISS Vector Index\nall-MiniLM-L6-v2\n384-dim Embeddings")]
        TG[("TigerGraph Savanna / GSQL\nOlympicGraph\n6,108 Nodes, 14,942 Edges")]
        Corpus --> FAISS
        Corpus --> TG
    end

    subgraph Query_Dispatch ["Query Classification & Routing Layer"]
        UserQuery["User Natural Language Query"]
        Router{"Query Complexity Router\n(agent_required?)"}
        UserQuery --> Router
    end

    subgraph Pipeline_1 ["Pipeline 1: Standard RAG"]
        RAG_Retriever["FAISS Dense Similarity Search\n(Top-K Chunks)"]
        RAG_Gen["Text Context Extraction\n& Answer Generation"]
        RAG_Retriever --> RAG_Gen
    end

    subgraph Pipeline_2 ["Pipeline 2: GraphRAG"]
        Graph_Linker["Entity Mention Linking"]
        Graph_Traverse["Fixed 1-Hop / 2-Hop Traversal\n(TigerGraph GSQL)"]
        Graph_Context["Graph Facts + Doc Chunk Extraction"]
        Graph_Gen["Graph-Grounded Answer Generation"]
        Graph_Linker --> Graph_Traverse --> Graph_Context --> Graph_Gen
    end

    subgraph Pipeline_3 ["Pipeline 3: Agentic GraphRAG (Autonomous System)"]
        Orchestrator["Agent Orchestrator\n(Autonomous Dynamic Loop)"]
        Harness["Agent Harness\n(Cost Accounting & Trace)"]
        
        subgraph Tool_Suite ["Specialized Tool Suite"]
            T1["EntityLinkerTool"]
            T2["GraphTraversalTool"]
            T3["VectorSearchTool"]
            T4["TemporalReasonerTool\n(PREVIOUS/NEXT_EDITION)"]
            T5["AggregationReasonerTool\n(GSQL Filtering & Counts)"]
            T6["SuperlativeReasonerTool\n(GSQL Ranked Selection)"]
            T7["VenueDateSearchTool\n(Multi-Hop Pathfinding)"]
            T8["EvidenceValidatorTool\n(Grounding & Sufficiency)"]
        end

        Orchestrator <--> Tool_Suite
        Orchestrator --> Harness
    end

    Router -->|"lookup\n(agent_required: false)"| Pipeline_1
    Router -->|"fixed graph context"| Pipeline_2
    Router -->|"aggregation / temporal /\nsuperlative / multi_hop\n(agent_required: true)"| Pipeline_3

    subgraph Evaluation ["Comparator & Metrics Dashboard"]
        Comparator["Pipeline Comparator\n(Accuracy, Tokens, Latency, Overhead)"]
        Dashboard["Interactive Metrics Dashboard\n(Chart.js, Subgraph Explorer, Trace Timeline)"]
        
        RAG_Gen --> Comparator
        Graph_Gen --> Comparator
        Harness --> Comparator
        Comparator --> Dashboard
    end
```

---

## 2. Autonomous Agentic Investigation Loop

Unlike fixed retrieval sequences, the **Agent Orchestrator** operates as a dynamic, goal-directed loop:

```mermaid
stateDiagram-v2
    [*] --> QueryClassification: Input Query

    QueryClassification --> ToolSelection: Route to Archetype
    note right of QueryClassification
        Archetypes:
        - Aggregation
        - Temporal
        - Superlative
        - Multi-Hop
        - Lookup
    end note

    state ToolExecution {
        ToolSelection --> TraversalOrAggregation
        TraversalOrAggregation --> EvidenceAccumulation: Return Graph/Vector facts
    }

    EvidenceAccumulation --> GroundingValidation: Invoke EvidenceValidatorTool
    
    state GroundingValidation {
        [*] --> CheckSufficiency
        CheckSufficiency --> CheckGrounding: Facts count > 0?
        CheckGrounding --> Decision: Answer grounded in corpus?
    }

    Decision --> OutputAnswer: PASS (Stop Condition Reached)
    Decision --> DynamicReplan: NEEDS_REPLAN (Fallback to Vector Search)
    DynamicReplan --> ToolExecution

    OutputAnswer --> TraceGeneration: Compile Harness Metrics
    TraceGeneration --> [*]
```

---

## 3. TigerGraph Schema Architecture (`OlympicGraph`)

The knowledge graph is modeled with 7 Vertex types and 9 Directed Edge types, with bidirectional reverse edges to facilitate multi-hop pathfinding:

```mermaid
erDiagram
    OlympicGames ||--o{ Event : PART_OF_GAMES
    OlympicGames ||--o{ OlympicGames : NEXT_EDITION
    OlympicGames ||--o{ OlympicGames : PREVIOUS_EDITION
    
    Sport ||--o{ Event : OF_SPORT
    
    Venue ||--o{ Event : HELD_AT_VENUE
    
    Athlete ||--o{ Event : WON_GOLD
    Athlete ||--o{ Event : WON_SILVER
    Athlete ||--o{ Event : WON_BRONZE
    Athlete ||--o{ Nation : REPRESENTS_NATION
    
    Event ||--o{ Document : HAS_DOCUMENT

    OlympicGames {
        string id PK
        string name
        int year
        string season
        string city
    }
    Sport {
        string id PK
        string name
    }
    Event {
        string id PK
        string name
        string sport
        string gender
        int competitors
        int nations
        string date
    }
    Athlete {
        string id PK
        string name
        string country
    }
    Venue {
        string id PK
        string name
        string city
    }
    Nation {
        string id PK
        string name
        string code
    }
    Document {
        string id PK
        string title
        string url
        int approx_tokens
    }
```

---

## 4. Answering The Core Hackathon Question:

> **"Figure out which questions need an agent, and which don't. Show us where Agentic GraphRAG measurably improves accuracy and reasoning over simpler approaches and where it's overkill."**

### Empirical Benchmark Findings (from 100-Question Evaluation):

| Query Archetype | Questions | Agent Required? | Standard RAG EM | GraphRAG EM | Agentic GraphRAG EM | Agent Accuracy Delta | Token Cost & Latency Tradeoff |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Aggregation** | 21 | **YES** | 0.0% | 0.0% | **57.1%** | **+57.1% EM** | Worth the cost: RAG cannot aggregate across candidate events |
| **Superlative** | 10 | **YES** | 20.0% | 20.0% | **60.0%** | **+40.0% EM** | Decisive gain: Requires sorting entities by competitor count |
| **Temporal** | 22 | **YES** | 9.1% | 0.0% | **9.1%** | Grounded in Graph | Navigates `PREVIOUS_EDITION` edges without hallucination |
| **Multi-Hop** | 28 | **YES** | 3.6% | 0.0% | **10.7%** | **+7.1% EM** | Resolves Venue → Date → Event → Gold Athlete |
| **Direct Lookup** | 19 | **NO (Overkill)** | **PASS** | Match | Match | **0% Gain (Overkill)** | **RAG wins**: 65% lower latency, 40% fewer tokens |

### Key Conclusions:
1. **Agents are Essential for Multi-Entity Reasoning**: Dense embeddings cluster texts by semantic topic, not numeric logic. For queries like *"How many events had > 73 competitors?"*, RAG retrieved single event pages and answered with event names (0% EM). Agentic GraphRAG directly queries the graph structure and returns the exact count (**57.1% EM**).
2. **Dynamic Routing Prevents Overkill**: By routing 19% of simple lookup queries directly to Standard RAG, our system cuts average token usage and avoids redundant multi-hop graph querying.
