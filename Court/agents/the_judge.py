import os
from openai import OpenAI

def run_judge_ruling(draft: str, debate_report: str, precedents: str) -> str:
    """OpenAI Node: The Judge reviews the debate and case law, then issues the final contract."""
    print("\n--- PHASE 4: OPENAI SUPREME COURT JUSTICE ---")
    print(" [OpenAI] The Judge is reviewing the case...")
    
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.environ.get("GROQ_API_KEY")
    )
    
    system_prompt = """
    You are an impartial Supreme Court Justice and expert in Corporate Law.
    You have been presented with an initial Contract Draft, a 'Disputed Clauses & Loophole Report' from the 5-Agent Legal Panel, and a set of Case Law Precedents.
    Review the arguments and the precedents. Resolve the disputes fairly, ensuring the contract is legally binding, fair, and compliant with corporate law.
    Output the FINAL, fully-revised contract. Provide a brief "Judge's Rationale" at the top explaining why you ruled the way you did on the IP, Non-Compete, and Equity clauses.
    """
    
    user_prompt = f"""
    --- ORIGINAL DRAFT ---
    {draft}
    
    --- CASE LAW PRECEDENTS ---
    {precedents}
    
    --- LEGAL PANEL DEBATE REPORT ---
    {debate_report}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )
    
    final_contract = response.choices[0].message.content
    print(" [OpenAI] Final Contract Issued.\n")
    return final_contract
