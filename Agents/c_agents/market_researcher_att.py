import os
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2] / 'shared'))
from llm_factory import get_langchain_llm
from prompt_safety import wrap_untrusted, harden_system_prompt
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.tools import DuckDuckGoSearchRun
from c_agents.attestix_client import attestix_client

def run_market_research(ticker: str, agent_id: str) -> str:
    """LangChain Node: Scans the LIVE internet for breaking news on a ticker (Regulated)."""
    print(f"\n--- PHASE 1: LANGCHAIN MARKET RESEARCHER ---")
    print(f" [LangChain - Regulated] Searching the live internet for: {ticker}...")
    
    # --- ATTESTIX CONFORMITY GATE ---
    if not attestix_client.check_conformity(agent_id):
        raise PermissionError("Attestix Gatekeeper blocked execution. Node failed conformity assessment.")
    
    search_tool = DuckDuckGoSearchRun()
    try:
        search_results = search_tool.run(f"Latest breaking financial news and SEC filings for {ticker}")
        print(" [LangChain] Live web data retrieved successfully.")
    except Exception as e:
        search_results = f"Search failed: {str(e)}"
        print(" [LangChain] Web search failed, falling back.")
        
    llm = get_langchain_llm(temperature=0.2)
    
    sys_msg = SystemMessage(content=harden_system_prompt(
        "You are a High-Frequency Trading Market Researcher. Summarize the raw web search results provided into a dense, highly analytical 'Market Sentiment Report'. You MUST explicitly declare the overall sentiment as BULLISH, BEARISH, or NEUTRAL at the very top of your report."
    ))

    # OWASP LLM01: wrap web-sourced and user-supplied content in spotlighting
    # delimiters so the LLM treats it as DATA, not as new instructions.
    safe_ticker = wrap_untrusted(ticker, label="ticker_symbol")
    safe_search = wrap_untrusted(search_results, label="duckduckgo_search_results")
    user_msg = HumanMessage(content=f"""
    Target Ticker:
    {safe_ticker}

    LIVE WEB SEARCH RESULTS:
    {safe_search}

    Output a concise Market Sentiment Report.
    """)
    
    response = llm.invoke([sys_msg, user_msg])
    report = response.content
    
    print(" [LangChain] Market Sentiment Report Generated.\n")
    
    # --- ATTESTIX PROVENANCE LOGGING ---
    input_payload = f"TICKER: {ticker}\nLIVE WEB SOURCES:\n{search_results}"
    attestix_client.log_action(
        agent_id=agent_id,
        action_type="MARKET_RESEARCH",
        input_data=input_payload,
        output_data=report
    )
    
    return report
