import os
from openai import OpenAI
from c_agents.attestix_client import attestix_client

def run_cio_decision(ticker: str, market_report: str, debate_report: str, agent_id: str, *, delegation_token: str) -> str:
    """OpenAI Node: The Chief Investment Officer makes the final trade decision (Regulated)."""
    print("\n--- PHASE 4: OPENAI CHIEF INVESTMENT OFFICER ---")
    print(" [OpenAI - Regulated] The CIO is reviewing the trade proposal...")
    
    # --- ATTESTIX DELEGATION GATE ---
    if not delegation_token:
        raise PermissionError("[Attestix] DENIED - delegation_token required for issue_final_trade_order")
    attestix_client.verify_token(delegation_token, "issue_final_trade_order")

    # --- ATTESTIX CONFORMITY GATE ---
    if not attestix_client.check_conformity(agent_id):
        raise PermissionError("Attestix Gatekeeper blocked execution. Node failed conformity assessment.")
    
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.environ.get("GROQ_API_KEY")
    )
    
    system_prompt = """
    You are the Chief Investment Officer (CIO) of a multi-billion dollar quantitative hedge fund.
    Review the LangChain Market Sentiment Report and the CrewAI Investment Committee Debate Report.
    Your goal is to issue a FINAL TRADE ORDER for the requested ticker.
    You must decide:
    1. EXECUTE AGGRESSIVE LONG
    2. EXECUTE AGGRESSIVE SHORT
    3. ABORT TRADE (Too much risk)
    Provide a robust, highly analytical rationale for your decision, citing the exact data points that convinced you.
    """
    
    user_prompt = f"""
    TARGET TICKER: {ticker}
    
    --- MARKET SENTIMENT REPORT ---
    {market_report}
    
    --- INVESTMENT COMMITTEE DEBATE ---
    {debate_report}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1
    )
    
    decision = response.choices[0].message.content
    print(" [OpenAI] Final Trade Order Issued.\n")
    
    # --- ATTESTIX PROVENANCE LOGGING ---
    input_payload = f"TICKER: {ticker}\n\nREPORT:\n{market_report}\n\nDEBATE:\n{debate_report}"
    attestix_client.log_action(
        agent_id=agent_id,
        action_type="FINAL_DIAGNOSIS",
        input_data=input_payload,
        output_data=decision,
        delegation_token=delegation_token
    )
    
    return decision
