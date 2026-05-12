import os
from openai import OpenAI

def run_final_assessment(target_supplier: str, discrepancy_report: str, debate_report: str) -> str:
    """OpenAI Node: The Chief Compliance Officer makes the final call."""
    print("\n--- PHASE 3: OPENAI CHIEF COMPLIANCE OFFICER ---")
    print(" [OpenAI] The CCO is reviewing the audit...")
    
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.environ.get("GROQ_API_KEY")
    )
    
    system_prompt = """
    You are the Chief Compliance Officer (CCO) for a major multinational corporation.
    You must review the LangChain 'Discrepancy Report' (comparing internal promises to global news) and the CrewAI 'Internal Audit Debate Report' (between your ESG officers and Supply Chain Manager).
    Your goal is to issue a Final ESG Compliance Decision regarding the supplier.
    You must decide: 
    1. PASS (keep the supplier)
    2. PROBATION (keep them but enforce an immediate on-site audit)
    3. FAIL (immediately terminate the contract).
    Provide a robust rationale for your decision.
    """
    
    user_prompt = f"""
    TARGET SUPPLIER: {target_supplier}
    
    --- DISCREPANCY REPORT ---
    {discrepancy_report}
    
    --- AUDIT DEBATE REPORT ---
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
    print(" [OpenAI] Final Decision Issued.\n")
    return decision
