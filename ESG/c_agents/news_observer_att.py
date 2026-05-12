import os
import json
from pathlib import Path
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2] / 'shared'))
from llm_factory import get_langchain_llm
from langchain_core.messages import SystemMessage, HumanMessage
from c_agents.attestix_client import attestix_client

def observe_supply_chain(target_supplier: str, agent_id: str) -> str:
    """LangChain Node: Scans internal docs and cross-references with global news (Regulated)."""
    print(f"\n--- PHASE 1: LANGCHAIN REAL-TIME OBSERVER ---")
    print(f" [LangChain - Regulated] Scanning global news and internal records for: {target_supplier}")
    
    # --- ATTESTIX CONFORMITY GATE ---
    if not attestix_client.check_conformity(agent_id):
        raise PermissionError("Attestix Gatekeeper blocked execution. Node failed conformity assessment.")
    
    base_dir = Path(__file__).parent.parent / "data"
    
    try:
        with open(base_dir / "internal_supplier_docs.json", "r") as f:
            internal_data = json.load(f)
            supplier_info = internal_data.get("suppliers", {}).get(target_supplier, "No internal records found.")
    except Exception as e:
        supplier_info = str(e)
        
    try:
        with open(base_dir / "mock_news_api.json", "r") as f:
            news_data = json.load(f)
            relevant_news = [n for n in news_data.get("news_reports", []) if target_supplier in n["headline"] or target_supplier in n["content"]]
    except Exception as e:
        relevant_news = [str(e)]
        
    llm = get_langchain_llm(temperature=0.2)
    
    sys_msg = SystemMessage(content="You are a Corporate Intelligence Observer. Your job is to compare a company's internal supplier commitments against real-time global news. Generate a 'Discrepancy Report' highlighting any severe ESG (Environmental, Social, Governance) violations.")
    
    user_msg = HumanMessage(content=f"""
    Target Supplier: {target_supplier}
    
    INTERNAL COMPANY COMMITMENTS:
    {json.dumps(supplier_info, indent=2)}
    
    REAL-TIME GLOBAL NEWS:
    {json.dumps(relevant_news, indent=2)}
    
    Analyze the data and list all discrepancies between what the company promised and what is actually happening on the ground.
    """)
    
    response = llm.invoke([sys_msg, user_msg])
    report = response.content
    
    print(" [LangChain] Discrepancy Report Generated.\n")
    
    # --- ATTESTIX PROVENANCE LOGGING ---
    input_payload = f"INTERNAL:\n{json.dumps(supplier_info)}\n\nNEWS:\n{json.dumps(relevant_news)}"
    attestix_client.log_action(
        agent_id=agent_id,
        action_type="SUPPLY_CHAIN_AUDIT",
        input_data=input_payload,
        output_data=report
    )
    
    return report
