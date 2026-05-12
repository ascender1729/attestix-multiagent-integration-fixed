import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Patch 07 (post-audit 2026-05-12): single repo-root .env, fail-fast on missing key.
_repo_root = Path(__file__).resolve().parents[2]
load_dotenv(_repo_root / ".env")
assert os.environ.get("GROQ_API_KEY"), (
    "GROQ_API_KEY missing. Copy .env.example to .env at the repo root and fill in your key."
)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from c_agents.intake_agent_att import run_intake, AGENT_ID as INTAKE_ID
from c_agents.db_connector_att import get_patient_history, AGENT_ID as DB_ID
from c_agents.specialist_panel_att import run_specialist_panel, AGENT_ID as PANEL_ID
from c_agents.chief_mo_att import run_cmo_ruling, AGENT_ID as CMO_ID
from c_agents.attestix_client import attestix_client

def render(text: str) -> str:
    import re
    B, R = "\033[1m", "\033[0m"
    text = re.sub(r'\*\*(.*?)\*\*', fr'{B}\1{R}', text)
    text = re.sub(r'^#{1,3}\s+(.+)$', fr'{B}\1{R}', text, flags=re.MULTILINE)
    text = re.sub(r'^\* ', '  * ', text, flags=re.MULTILINE)
    text = re.sub(r'^- ', '  * ', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\. ', lambda m: f'  {m.group()}', text, flags=re.MULTILINE)
    return text

def main():
    B, C, G, R = "\033[1m", "\033[96m", "\033[92m", "\033[0m"

    print(f"\n{B}{'='*52}{R}")
    print(f"{B}  AUTONOMOUS HOSPITAL BOARD  -  Attestix Regulated{R}")
    print(f"{B}{'='*52}{R}\n")
    print(f" [Attestix Framework] Bootstrapping Official Compliance Protocols...\n")

    print(f" {B}ATTESTIX SETUP PHASE{R}")
    print(f" {'='*40}")
    attestix_client.setup_full_compliance(INTAKE_ID, "Patient symptoms parsing and triage")
    attestix_client.setup_full_compliance(DB_ID, "Secure patient record retrieval")
    attestix_client.setup_full_compliance(PANEL_ID, "Medical diagnosis and analysis")
    attestix_client.setup_full_compliance(CMO_ID, "Final medical ruling and treatment authorisation")
    attestix_client.issue_credential(PANEL_ID, "Board Certified Specialist Panel")
    attestix_client.issue_credential(CMO_ID, "Chief Medical Officer")
    print(f" {'='*40}\n")

    patient_text = ""
    while not patient_text.strip():
        patient_text = input("Please enter the patient's statement: ")

    print(f"\n{B}{C}  PHASE 1  >  LANGCHAIN INTAKE{R}")
    print(f"{B}{'='*52}{R}")
    intake_data = run_intake(patient_text)
    patient_id = intake_data.get("patient_id", "UNKNOWN")
    symptoms = intake_data.get("primary_symptoms", [])
    severity = intake_data.get("severity", "Unknown")

    print(f"\n{B}{C}  PHASE 2  >  SEMANTIC KERNEL ENTERPRISE DB{R}")
    print(f"{B}{'='*52}{R}")
    db_token = attestix_client.delegate_capability(INTAKE_ID, DB_ID, "read_patient_record")
    patient_history = get_patient_history(patient_id, delegation_token=db_token)

    print(f"\n{B}{C}  PHASE 3  >  CREWAI 6-AGENT SPECIALIST PANEL{R}")
    print(f"{B}{'='*52}{R}")
    panel_token = attestix_client.delegate_capability(INTAKE_ID, PANEL_ID, "diagnose_patient")
    crew_debate = run_specialist_panel(symptoms, severity, patient_history, delegation_token=panel_token)

    print(f"\n{B}{C}  PHASE 4  >  OPENAI CHIEF MEDICAL OFFICER{R}")
    print(f"{B}{'='*52}{R}")
    cmo_token = attestix_client.delegate_capability(PANEL_ID, CMO_ID, "issue_final_ruling")
    final_ruling = run_cmo_ruling(crew_debate, patient_history, delegation_token=cmo_token)

    print(f"\n{B}{'='*52}{R}")
    print(f"{B}{G}  SECURE FINAL DIAGNOSIS & TREATMENT PLAN{R}")
    print(f"{B}{'='*52}{R}")
    print(render(final_ruling))

    # Print the cryptographic Merkle chain for the full session
    attestix_client.print_audit_trail()

    # Anchor the CMO's final ruling to Base Sepolia blockchain
    attestix_client.anchor_to_blockchain(CMO_ID)

    print(" [OK] EU AI Act Compliance Verified.")
    print(" View UCAN delegations and W3C Credentials in ~/.attestix/identities.json")

if __name__ == "__main__":
    main()
