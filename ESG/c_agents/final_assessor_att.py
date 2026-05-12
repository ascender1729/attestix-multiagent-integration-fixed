import os
from openai import OpenAI
from c_agents.attestix_client import attestix_client

def run_final_assessment(target_supplier: str, discrepancy_report: str, debate_report: str, agent_id: str, *, delegation_token: str) -> str:
    """OpenAI Node: The Chief Compliance Officer makes the final call (Regulated)."""
    print("\n--- PHASE 3: OPENAI CHIEF COMPLIANCE OFFICER ---")
    print(" [OpenAI - Regulated] The CCO is reviewing the audit...")
    
    # --- ATTESTIX DELEGATION GATE ---
    if not delegation_token:
        raise PermissionError("[Attestix] DENIED - delegation_token required for issue_final_audit_decision")
    attestix_client.verify_token(delegation_token, "issue_final_audit_decision")

    # --- ATTESTIX CONFORMITY GATE ---
    if not attestix_client.check_conformity(agent_id):
        raise PermissionError("Attestix Gatekeeper blocked execution. Node failed conformity assessment.")
    
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
    
    # --- ATTESTIX PROVENANCE LOGGING ---
    input_payload = f"TARGET: {target_supplier}\n\nDISCREPANCY:\n{discrepancy_report}\n\nDEBATE:\n{debate_report}"
    attestix_client.log_action(
        agent_id=agent_id,
        action_type="FINAL_DIAGNOSIS",
        input_data=input_payload,
        output_data=decision,
        delegation_token=delegation_token
    )
    
    return decision
