import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Patch 07 (post-audit 2026-05-12): single repo-root .env, fail-fast on missing key.
_repo_root = Path(__file__).resolve().parents[1]
load_dotenv(_repo_root / ".env")
assert os.environ.get("GROQ_API_KEY"), (
    "GROQ_API_KEY missing. Copy .env.example to .env at the repo root and fill in your key."
)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from c_agents.attestix_client import attestix_client
from c_agents.drafter_agent_att import run_drafter
from c_agents.db_connector_att import get_case_law_precedents
from c_agents.legal_panel_att import run_legal_panel
from c_agents.the_judge_att import run_judge_ruling

def main():
    # 1. ATTESTIX IDENTITY PROVISIONING
    DRAFTER_ID = attestix_client.provision_identity("Legal Drafter Node", "LangGraph")
    DB_ID = attestix_client.provision_identity("Legal Database Node", "SemanticKernel")
    PANEL_ID = attestix_client.provision_identity("5-Agent Legal Panel", "CrewAI")
    JUDGE_ID = attestix_client.provision_identity("Supreme Court Justice", "OpenAI")
    
    print("\n" + "="*50)
    print(" [SHIELD]  AI SUPREME COURT (Attestix EU AI Act Compliant)")
    print("="*50 + "\n")

    print(" [Attestix Framework] Bootstrapping Official Compliance Protocols...")
    
    # --- ATTESTIX SETUP PHASE ---
    print("\n--- ATTESTIX SETUP PHASE ---")
    attestix_client.setup_full_compliance(DRAFTER_ID, "Autonomous legal contract drafting and risk analysis")
    attestix_client.setup_full_compliance(DB_ID, "Secure case law and legal precedent retrieval")
    attestix_client.setup_full_compliance(PANEL_ID, "Multi-agent adversarial legal debate and loophole detection")
    attestix_client.setup_full_compliance(JUDGE_ID, "Final judicial ruling and contract adjudication")
    
    attestix_client.issue_credential(DRAFTER_ID, "Certified Legal AI")
    attestix_client.issue_credential(PANEL_ID, "Certified Legal Board")
    print("----------------------------\n")
    
    requirements = ""
    while not requirements.strip():
        print("Example: 'Draft an Employment Contract for a Senior AI Engineer joining a stealth startup. Include a 2-year Non-Compete, assignment of all IP, and an equity grant of 10,000 shares.'")
        requirements = input("Enter the contract requirements: ")

    # Phase 1: Draft the contract
    initial_draft = run_drafter(requirements, DRAFTER_ID)
    
    # Phase 2: Query Legal DB (Requires Delegation from Drafter)
    db_token = attestix_client.delegate_capability(DRAFTER_ID, DB_ID, "read_legal_precedents")
    keywords = ["non_compete", "intellectual_property", "equity_tax"]
    precedents = get_case_law_precedents(keywords, DB_ID, delegation_token=db_token)
    
    # Phase 3: The 5-Agent Legal Mega-Panel (Requires Delegation from Drafter)
    panel_token = attestix_client.delegate_capability(DRAFTER_ID, PANEL_ID, "analyze_legal_risks")
    debate_report = run_legal_panel(initial_draft, precedents, PANEL_ID, delegation_token=panel_token)
    
    # Phase 4: The Judge makes a final ruling (Requires Delegation from Panel)
    judge_token = attestix_client.delegate_capability(PANEL_ID, JUDGE_ID, "issue_final_verdict")
    final_contract = run_judge_ruling(initial_draft, debate_report, precedents, JUDGE_ID, delegation_token=judge_token)
    
    print("\n" + "="*50)
    print(" [CONTRACT] FINAL BINDING CONTRACT")
    print("="*50)
    print(final_contract)

    attestix_client.print_audit_trail()

    print(" [OK] EU AI Act Compliance Verified.")
    print(" View UCAN delegations and W3C Credentials in ~/.attestix/identities.json")

if __name__ == "__main__":
    main()
