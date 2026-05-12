import os
import sys
from dotenv import load_dotenv

# Ensure we can import from the Court/ directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load the API key from the Hospital directory so we don't have to duplicate it
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Hospital', '.env')
load_dotenv(env_path)

from Court.agents.drafter_agent import run_drafter
from Court.agents.db_connector import get_case_law_precedents
from Court.agents.legal_panel import run_legal_panel
from Court.agents.the_judge import run_judge_ruling

def main():
    print("\n" + "="*50)
    print(" 🏛️  AI SUPREME COURT (Upgraded Unregulated Baseline)")
    print("="*50 + "\n")
    
    requirements = ""
    while not requirements.strip():
        print("Example: 'Draft an Employment Contract for a Senior AI Engineer joining a stealth startup. Include a 2-year Non-Compete, assignment of all IP, and an equity grant of 10,000 shares.'")
        requirements = input("Enter the contract requirements: ")

    # Phase 1: Draft the contract
    initial_draft = run_drafter(requirements)
    
    # Phase 2: Query Legal DB
    # We will search the database for precedents on the core issues.
    keywords = ["non_compete", "intellectual_property", "equity_tax"]
    precedents = get_case_law_precedents(keywords)
    
    # Phase 3: The 5-Agent Legal Mega-Panel
    debate_report = run_legal_panel(initial_draft, precedents)
    
    # Phase 4: The Judge makes a final ruling
    final_contract = run_judge_ruling(initial_draft, debate_report, precedents)
    
    print("\n" + "="*50)
    print(" 📜 FINAL BINDING CONTRACT")
    print("="*50)
    print(final_contract)
    print("\n" + "="*50)
    print(" ⚠️ Warning: This is the Unregulated Mode. No cryptographic provenance was logged.")

if __name__ == "__main__":
    main()
