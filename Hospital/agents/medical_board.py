import os
import sys
import re
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.intake_agent import run_intake
from agents.db_connecter import get_patient_history
from agents.specialist_panel import run_specialist_panel
from agents.cheif_mo import run_cmo_ruling

def render(text: str) -> str:
    """Convert markdown formatting to ANSI terminal styling."""
    B, R = "\033[1m", "\033[0m"
    text = re.sub(r'\*\*(.*?)\*\*', fr'{B}\1{R}', text)
    text = re.sub(r'^#{1,3}\s+(.+)$', fr'{B}\1{R}', text, flags=re.MULTILINE)
    text = re.sub(r'^\* ', '  • ', text, flags=re.MULTILINE)
    text = re.sub(r'^- ', '  • ', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\. ', lambda m: f'  {m.group()}', text, flags=re.MULTILINE)
    return text

def main():
    # 1. Load Environment Variables (GROQ_API_KEY)
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    load_dotenv(env_path)
    
    B = "\033[1m"
    C = "\033[96m"
    G = "\033[92m"
    R = "\033[0m"

    print(f"\n{B}{'━'*52}{R}")
    print(f"{B}  AUTONOMOUS HOSPITAL BOARD  —  Unregulated Mode{R}")
    print(f"{B}{'━'*52}{R}\n")

    patient_text = ""
    while not patient_text.strip():
        patient_text = input("Please enter the patient's statement: ")

    print(f"\n{B}{C}  PHASE 1  ›  LANGCHAIN INTAKE{R}")
    print(f"{B}{'─'*52}{R}")
    intake_data = run_intake(patient_text)
    patient_id = intake_data.get("patient_id", "UNKNOWN")
    symptoms = intake_data.get("primary_symptoms", [])
    severity = intake_data.get("severity", "Unknown")

    print(f"\n{B}{C}  PHASE 2  ›  SEMANTIC KERNEL ENTERPRISE DB{R}")
    print(f"{B}{'─'*52}{R}")
    patient_history = get_patient_history(patient_id)

    print(f"\n{B}{C}  PHASE 3  ›  CREWAI 6-AGENT SPECIALIST PANEL{R}")
    print(f"{B}{'─'*52}{R}")
    crew_debate = run_specialist_panel(symptoms, severity, patient_history)

    print(f"\n{B}{C}  PHASE 4  ›  OPENAI CHIEF MEDICAL OFFICER{R}")
    print(f"{B}{'─'*52}{R}")
    final_ruling = run_cmo_ruling(crew_debate, patient_history)

    print(f"\n{B}{'━'*52}{R}")
    print(f"{B}{G}  FINAL DIAGNOSIS & TREATMENT PLAN{R}")
    print(f"{B}{'━'*52}{R}")
    print(render(final_ruling))
    print(f"\n{B}{'━'*52}{R}")

if __name__ == "__main__":
    main()
