import os
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from c_agents.attestix_client import attestix_client

class AgentState(TypedDict):
    requirements: str
    draft: str

# Agent ID mapped in orchestrator, but we pass it down
AGENT_ID = ""

def draft_contract(state: AgentState):
    """LangGraph Node: Drafts the initial contract."""
    print(" [LangGraph - Regulated] Junior Corporate Lawyer is drafting the contract...")
    
    # --- ATTESTIX CONFORMITY GATE ---
    if not attestix_client.check_conformity(AGENT_ID):
        raise PermissionError("Attestix Gatekeeper blocked execution. Node failed conformity assessment.")
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        api_key=os.environ.get("GROQ_API_KEY")
    )
    
    sys_msg = SystemMessage(content="You are a meticulous Junior Corporate Lawyer. Draft a complete, professional legal contract based on the user's requirements. Include standard boilerplate clauses if appropriate. Keep it structured and clear.")
    user_msg = HumanMessage(content=f"Requirements: {state['requirements']}")
    
    response = llm.invoke([sys_msg, user_msg])
    
    return {"draft": response.content}

def run_drafter(requirements: str, agent_id: str) -> str:
    """Entry point to run the Compliant LangGraph drafter."""
    global AGENT_ID
    AGENT_ID = agent_id
    
    print("\n--- PHASE 1: LANGGRAPH CONTRACT DRAFTER ---")
    
    workflow = StateGraph(AgentState)
    workflow.add_node("draft_node", draft_contract)
    workflow.add_edge(START, "draft_node")
    workflow.add_edge("draft_node", END)
    
    app = workflow.compile()
    
    result = app.invoke({"requirements": requirements, "draft": ""})
    final_draft = result["draft"]
    
    print(" [LangGraph] Draft Complete.")
    
    # --- ATTESTIX PROVENANCE LOGGING ---
    attestix_client.log_action(
        agent_id=AGENT_ID,
        action_type="DRAFT_CONTRACT",
        input_data=requirements,
        output_data=final_draft
    )
    
    return final_draft
