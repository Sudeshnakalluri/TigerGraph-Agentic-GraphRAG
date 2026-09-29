"""Autonomous Agent Orchestrator: Dynamic Plan, Execute, Reflect Loop."""
import time
import re
from typing import Dict, List, Any, Optional
from backend.agents.router import QueryComplexityRouter
from backend.agents.tools import SpecializedTools
from backend.agents.agent_harness import AgentHarness

class AgentOrchestrator:
    """Orchestrates dynamic inquiry loop with specialized tool dispatch."""

    def __init__(self, tools: Optional[SpecializedTools] = None):
        self.tools = tools or SpecializedTools()
        self.router = QueryComplexityRouter()

    def run(self, query: str) -> Dict[str, Any]:
        """Executes full agentic investigation on user query."""
        # Step 1: Query Complexity Routing
        routing = self.router.route(query)
        qtype = routing["query_type"]
        agent_req = routing["agent_required"]

        harness = AgentHarness(query=query, query_type=qtype, agent_required=agent_req)
        harness.add_step(
            action="query_classification",
            description=f"Query classified as: {qtype} (Agent Required: {agent_req})",
            details={"reason": routing["reason"], "recommended_pipeline": routing["recommended_pipeline"]}
        )

        collected_facts: List[Dict[str, Any]] = []
        citations: List[Dict[str, Any]] = []
        final_answer = ""

        # Step 2: Tool Selection based on classified archetype
        if qtype == "aggregation":
            harness.add_step("tool_selection", "Selected tools: [AggregationReasonerTool, EntityLinkerTool]")
            harness.record_tool_call("AggregationReasonerTool")
            
            # Extract games and sport filters
            games_match = re.search(r"(\d{4}\s+(?:Summer|Winter))", query, re.IGNORECASE)
            games_filter = games_match.group(1) if games_match else None
            
            # Extract threshold (e.g. more than 73)
            num_match = re.search(r"(?:more than|fewer than|greater than|>)\s*(\d+)", query, re.IGNORECASE)
            threshold = int(num_match.group(1)) if num_match else 0

            # Extract sport
            sport_match = re.search(r"\b(biathlon|athletics|swimming|shooting|canoeing|cycling|gymnastics|skiing)\b", query, re.IGNORECASE)
            sport_filter = sport_match.group(1) if sport_match else None

            harness.record_graph_query(hops=1)
            matched_events = self.tools.aggregation_reasoner(
                games_filter=games_filter,
                sport_filter=sport_filter,
                min_competitors=threshold,
                operator=">"
            )
            count = len(matched_events)
            harness.add_step("graph_aggregation", f"Discovered {count} matching event vertices in graph", details={"count": count, "events": [e["name"] for e in matched_events[:5]]})
            
            for ev in matched_events:
                collected_facts.append({"event": ev["name"], "competitors": ev.get("competitors")})
                if ev.get("doc_id"):
                    citations.append({"doc_id": ev["doc_id"], "title": ev["name"]})

            final_answer = f"{count}"

        elif qtype == "temporal":
            harness.add_step("tool_selection", "Selected tools: [TemporalReasonerTool, GraphTraversalTool, VectorSearchTool]")
            harness.record_tool_call("TemporalReasonerTool")
            
            yr_match = re.search(r"(\d{4})", query)
            ref_year = int(yr_match.group(1)) if yr_match else 2016
            direction = "previous" if "before" in query.lower() or "prior" in query.lower() else "next"
            
            season = "Winter" if "winter" in query.lower() else "Summer"
            ref_games_str = f"{ref_year} {season}"
            
            harness.record_graph_query(hops=1)
            target_games = self.tools.temporal_reasoner(ref_games_str, direction=direction)
            if target_games:
                harness.add_step("temporal_navigation", f"Traversed {direction.upper()}_EDITION edge to: {target_games.get('name')}")
                target_year = target_games.get("year")

                # Find event in that year
                sport_match = re.search(r"\b(walk|marathon|sprint|biathlon|hurdles|slalom|canoe|speed skating)\b", query, re.IGNORECASE)
                sub_query = f"{sport_match.group(1) if sport_match else ''} {target_year} {season}"
                harness.record_tool_call("VectorSearchTool")
                chunks = self.tools.vector_search(sub_query, top_k=3)
                harness.add_step("vector_retrieval", f"Retrieved {len(chunks)} supporting documents for {target_games.get('name')}")
                
                # Check for gold winner in chunks or graph
                for ch in chunks:
                    citations.append({"doc_id": ch["doc_id"], "title": ch["title"]})
                    text = ch["text"]
                    gold_m = re.search(r"gold:\s*([A-Za-z\s\u00C0-\u024F]+)", text, re.IGNORECASE)
                    if gold_m:
                        winner = gold_m.group(1).split("\n")[0].strip()
                        final_answer = winner
                        collected_facts.append({"event": ch["title"], "gold_winner": winner})
                        break

            if not final_answer and chunks:
                final_answer = chunks[0]["title"]

        elif qtype == "superlative":
            harness.add_step("tool_selection", "Selected tools: [SuperlativeReasonerTool, GraphTraversalTool]")
            harness.record_tool_call("SuperlativeReasonerTool")
            
            games_match = re.search(r"(\d{4}\s+(?:Summer|Winter))", query, re.IGNORECASE)
            games_filter = games_match.group(1) if games_match else None
            sport_match = re.search(r"\b(athletics|swimming|cycling|biathlon|shooting|gymnastics)\b", query, re.IGNORECASE)
            sport_filter = sport_match.group(1) if sport_match else None

            harness.record_graph_query(hops=1)
            sup = self.tools.superlative_reasoner(games_filter=games_filter, sport_filter=sport_filter, metric="competitors", order="DESC")
            if sup:
                harness.add_step("superlative_comparison", f"Found maximum competitors event: {sup['name']} ({sup.get('competitors')} competitors)")
                final_answer = sup["name"]
                collected_facts.append(sup)
                if sup.get("doc_id"):
                    citations.append({"doc_id": sup["doc_id"], "title": sup["name"]})

        elif qtype == "multi_hop":
            harness.add_step("tool_selection", "Selected tools: [EntityLinkerTool, GraphTraversalTool, DocumentChunkTool]")
            harness.record_tool_call("EntityLinkerTool")
            
            # Extract venue and date
            venue_match = re.search(r"(?:held at|venue:?)\s*([A-Za-z\s]+(?:Gymnasium|Stadium|Centre|Center|Oval|Hall|Arena))", query, re.IGNORECASE)
            date_match = re.search(r"(\d{1,2}\s+[A-Za-z]+\s+\d{4}|\d{1,2}\s+to\s+\d{1,2}\s+[A-Za-z]+\s+\d{4})", query, re.IGNORECASE)
            
            venue_str = venue_match.group(1).strip() if venue_match else "Olympic"
            date_str = date_match.group(1).strip() if date_match else ""

            harness.record_graph_query(hops=2)
            evs = self.tools.venue_date_search(venue_str, date_str)
            harness.add_step("graph_path_search", f"Traversed HELD_AT_VENUE edges: found {len(evs)} matching events", details={"events": [e["name"] for e in evs]})

            if evs:
                target_ev = evs[0]
                citations.append({"doc_id": target_ev.get("doc_id"), "title": target_ev["name"]})
                # get gold medalist
                gold_edges = self.tools.graph.get_1hop(target_ev["id"], relation_type="WON_GOLD")
                winners = [e["node"].get("name") for e in gold_edges if e["direction"] == "in"]
                if winners:
                    final_answer = winners[0]
                    collected_facts.append({"event": target_ev["name"], "winner": winners[0]})
                else:
                    final_answer = target_ev["name"]
            else:
                # Fallback to vector search
                chunks = self.tools.vector_search(query, top_k=2)
                for ch in chunks:
                    citations.append({"doc_id": ch["doc_id"], "title": ch["title"]})
                final_answer = chunks[0]["title"] if chunks else "Not found"

        else: # Lookup
            harness.add_step("tool_selection", "Selected tool: [VectorSearchTool] (Fast Lookup Path)")
            harness.record_tool_call("VectorSearchTool")
            chunks = self.tools.vector_search(query, top_k=3)
            harness.add_step("vector_retrieval", f"Retrieved top {len(chunks)} chunks")
            for ch in chunks:
                citations.append({"doc_id": ch["doc_id"], "title": ch["title"]})
                collected_facts.append({"title": ch["title"], "text_snippet": ch["text"][:200]})
            final_answer = chunks[0]["title"] if chunks else "No relevant document found."

        # Step 3: Evidence Grounding & Validation
        harness.record_tool_call("EvidenceValidatorTool")
        val_res = self.tools.evidence_validator(query, collected_facts, final_answer)
        harness.add_step("evidence_validation", f"Grounding Validation: {val_res['status']}", details=val_res)

        # Context Tokens accounting
        harness.context_tokens = sum(len(str(f).split()) for f in collected_facts)
        harness.record_llm_call(in_tokens=len(query.split()) + harness.context_tokens, out_tokens=len(final_answer.split()))

        trace = harness.get_trace()
        return {
            "query": query,
            "answer": final_answer,
            "query_type": qtype,
            "agent_required": agent_req,
            "citations": citations,
            "evidence": collected_facts,
            "validation": val_res,
            "trace": trace
        }