import os
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2] / 'shared'))
from llm_factory import get_openai_client
from c_agents.attestix_client import attestix_client

# 1. Identity Provisioning
AGENT_ID = attestix_client.provision_identity("Chief Medical Officer", "OpenAI")

def run_cmo_ruling(crew_debate_output: str, patient_history: dict, *, delegation_token: str) -> str:
    """The CMO reviews the CrewAI debate and makes a final ruling with Attestix Compliance."""
    print("\n [OpenAI - Regulated] Chief Medical Officer reviewing the case...")

    # 2. UCAN Delegation Gate — must hold 'issue_final_ruling' capability
    if not delegation_token:
        raise PermissionError("[Attestix] DENIED - delegation_token required for issue_final_ruling")
    attestix_client.verify_token(delegation_token, "issue_final_ruling")

    # 3. Conformity Gatekeeper
    if not attestix_client.check_conformity(AGENT_ID):
        raise PermissionError("Attestix Conformity Assessment Failed.")
        
    client = get_openai_client()
    
    system_prompt = """
    You are the Chief Medical Officer of a highly regulated hospital.
    Review the panel's differential diagnosis and the patient's secure medical history.
    Cross-reference it with the patient's known allergies and medications to ensure no fatal drug interactions.
    Issue a FINAL, authoritative diagnosis and a recommended treatment plan.
    Keep the final report professional, concise, and structured.
    Do NOT include a signature line or placeholder like [Your Name]. End the report after the recommendations.
    """
    
    user_prompt = f"""
    --- PATIENT HISTORY ---
    {patient_history}
    
    --- SPECIALIST PANEL DEBATE ---
    {crew_debate_output}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )
    
    final_ruling = response.choices[0].message.content
    
    # 4. Provenance Logging
    input_payload = {"history": patient_history, "debate": crew_debate_output}
    attestix_client.log_action(AGENT_ID, "FINAL_DIAGNOSIS", str(input_payload), final_ruling, delegation_token=delegation_token)
    
    print(" [OpenAI] Final Medical Ruling Issued.")
    return final_ruling
