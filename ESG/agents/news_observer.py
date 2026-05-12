import os
import json
from pathlib import Path
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

def observe_supply_chain(target_supplier: str) -> str:
    """LangChain Node: Scans internal docs and cross-references with global news."""
    print(f"\n--- PHASE 1: LANGCHAIN REAL-TIME OBSERVER ---")
    print(f" [LangChain] Scanning global news and internal records for: {target_supplier}")
    
    base_dir = Path(__file__).parent.parent / "data"
    
    # Load Internal Docs
    try:
        with open(base_dir / "internal_supplier_docs.json", "r") as f:
            internal_data = json.load(f)
            supplier_info = internal_data.get("suppliers", {}).get(target_supplier, "No internal records found.")
    except Exception as e:
        supplier_info = str(e)
        
    # Load News API
    try:
        with open(base_dir / "mock_news_api.json", "r") as f:
            news_data = json.load(f)
            # Filter news related to the supplier
            relevant_news = [n for n in news_data.get("news_reports", []) if target_supplier in n["headline"] or target_supplier in n["content"]]
    except Exception as e:
        relevant_news = [str(e)]
        
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        api_key=os.environ.get("GROQ_API_KEY")
    )
    
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
    
    print(" [LangChain] Discrepancy Report Generated.\n")
    return response.content
