import os
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

class AgentState(TypedDict):
    requirements: str
    draft: str

def draft_contract(state: AgentState):
    """LangGraph Node: Drafts the initial contract."""
    print(" [LangGraph] Junior Corporate Lawyer is drafting the contract...")
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        api_key=os.environ.get("GROQ_API_KEY")
    )
    
    sys_msg = SystemMessage(content="You are a meticulous Junior Corporate Lawyer. Draft a complete, professional legal contract based on the user's requirements. Include standard boilerplate clauses (e.g., Severability, Governing Law) if appropriate. Keep it structured and clear.")
    user_msg = HumanMessage(content=f"Requirements: {state['requirements']}")
    
    response = llm.invoke([sys_msg, user_msg])
    
    return {"draft": response.content}

def run_drafter(requirements: str) -> str:
    """Entry point to run the LangGraph drafter."""
    print("\n--- PHASE 1: LANGGRAPH CONTRACT DRAFTER ---")
    
    # Define the StateGraph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("draft_node", draft_contract)
    
    # Set entry point and edges
    workflow.add_edge(START, "draft_node")
    workflow.add_edge("draft_node", END)
    
    # Compile
    app = workflow.compile()
    
    # Invoke
    result = app.invoke({"requirements": requirements, "draft": ""})
    print(" [LangGraph] Draft Complete.\n")
    return result["draft"]
