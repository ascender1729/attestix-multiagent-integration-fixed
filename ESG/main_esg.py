import os
import sys
from dotenv import load_dotenv

# Ensure we can import from the ESG/ directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load the API key from the Hospital directory so we don't have to duplicate it
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Hospital', '.env')
load_dotenv(env_path)

from agents.news_observer import observe_supply_chain
from agents.audit_panel import run_audit_panel
from agents.final_assessor import run_final_assessment

def main():
    print("\n" + "="*50)
    print(" 🌍 GLOBAL ESG & SUPPLY CHAIN AUDITOR")
    print(" (Phase A: Unregulated Mode - No Attestix Compliance)")
    print("="*50 + "\n")
    
    target_supplier = ""
    while not target_supplier.strip():
        print("Example: 'Vietnam Factory 04'")
        target_supplier = input("Enter the Target Supplier to Audit: ")

    # Phase 1: LangChain scans the news vs internal docs
    discrepancy_report = observe_supply_chain(target_supplier)
    
    # Phase 2: CrewAI Audit Panel debates what to do
    debate_report = run_audit_panel(discrepancy_report)
    
    # Phase 3: OpenAI CCO makes the final ruling
    final_decision = run_final_assessment(target_supplier, discrepancy_report, debate_report)
    
    print("\n" + "="*50)
    print(" ⚖️ FINAL ESG COMPLIANCE DECISION")
    print("="*50)
    print(final_decision)
    print("\n" + "="*50)
    print(" ⚠️ Warning: This is the Unregulated Mode. No cryptographic provenance was logged.")

if __name__ == "__main__":
    main()
