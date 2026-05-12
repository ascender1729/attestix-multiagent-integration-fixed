import os
from openai import OpenAI

def run_cio_decision(ticker: str, market_report: str, debate_report: str) -> str:
    """OpenAI Node: The Chief Investment Officer makes the final trade decision."""
    print("\n--- PHASE 4: OPENAI CHIEF INVESTMENT OFFICER ---")
    print(" [OpenAI] The CIO is reviewing the trade proposal...")
    
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
    return decision
