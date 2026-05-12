import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Patch 07 (post-audit 2026-05-12): single repo-root .env, fail-fast on missing key.
_repo_root = Path(__file__).resolve().parents[1]
load_dotenv(_repo_root / ".env")
# LLM provider: groq (default) or bedrock. groq needs GROQ_API_KEY; bedrock uses AWS creds.
if os.environ.get("LLM_PROVIDER", "groq").lower() != "bedrock":
    assert os.environ.get("GROQ_API_KEY"), (
        "GROQ_API_KEY missing. Copy .env.example to .env at the repo root and fill in your key, "
        "or set LLM_PROVIDER=bedrock to route via AWS Bedrock."
    )
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from c_agents.attestix_client import attestix_client
from c_agents.news_observer_att import observe_supply_chain
from c_agents.audit_panel_att import run_audit_panel
from c_agents.final_assessor_att import run_final_assessment

def main():
    # 1. ATTESTIX IDENTITY PROVISIONING
    OBSERVER_ID = attestix_client.provision_identity("Global News Observer", "LangChain")
    PANEL_ID = attestix_client.provision_identity("ESG Audit Panel", "CrewAI")
    CCO_ID = attestix_client.provision_identity("Chief Compliance Officer", "OpenAI")
    
    print("\n" + "="*50)
    print(" [GLOBAL] GLOBAL ESG & SUPPLY CHAIN AUDITOR")
    print(" (Phase B: Attestix EU AI Act Compliant)")
    print("="*50 + "\n")

    print(" [Attestix Framework] Bootstrapping Official Compliance Protocols...")
    
    # --- ATTESTIX SETUP PHASE ---
    print("\n--- ATTESTIX SETUP PHASE ---")
    attestix_client.setup_full_compliance(OBSERVER_ID, "Supply chain monitoring and ESG violation detection")
    attestix_client.setup_full_compliance(PANEL_ID, "Multi-agent audit debate and risk mitigation")
    attestix_client.setup_full_compliance(CCO_ID, "Final ESG compliance ruling and supplier decision")
    
    attestix_client.issue_credential(OBSERVER_ID, "Certified ESG Auditor")
    attestix_client.issue_credential(PANEL_ID, "Certified Compliance Board")
    print("----------------------------\n")
    
    target_supplier = ""
    while not target_supplier.strip():
        print("Example: 'Vietnam Factory 04'")
        target_supplier = input("Enter the Target Supplier to Audit: ")

    # Phase 1: LangChain scans the news vs internal docs (Regulated)
    discrepancy_report = observe_supply_chain(target_supplier, OBSERVER_ID)
    
    # Phase 2: CrewAI Audit Panel debates what to do (Requires Delegation from Observer)
    panel_token = attestix_client.delegate_capability(OBSERVER_ID, PANEL_ID, "review_discrepancies")
    debate_report = run_audit_panel(discrepancy_report, PANEL_ID, delegation_token=panel_token)
    
    # Phase 3: OpenAI CCO makes the final ruling (Requires Delegation from Panel)
    cco_token = attestix_client.delegate_capability(PANEL_ID, CCO_ID, "issue_final_audit_decision")
    final_decision = run_final_assessment(target_supplier, discrepancy_report, debate_report, CCO_ID, delegation_token=cco_token)
    
    print("\n" + "="*50)
    print(" [ESG] FINAL ESG COMPLIANCE DECISION")
    print("="*50)
    print(final_decision)

    attestix_client.print_audit_trail()

    print(" [OK] EU AI Act Compliance Verified.")
    print(" View UCAN delegations and W3C Credentials in ~/.attestix/identities.json")

if __name__ == "__main__":
    main()
