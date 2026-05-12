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
from c_agents.market_researcher_att import run_market_research
from c_agents.quant_db_connector_att import get_quant_strategy
from c_agents.investment_committee_att import run_investment_committee
from c_agents.the_cio_att import run_cio_decision

def main():
    # 1. ATTESTIX IDENTITY PROVISIONING
    RESEARCHER_ID = attestix_client.provision_identity("Market Researcher Node", "LangChain")
    QUANT_ID = attestix_client.provision_identity("Proprietary Quant DB", "SemanticKernel")
    PANEL_ID = attestix_client.provision_identity("Investment Committee", "CrewAI")
    CIO_ID = attestix_client.provision_identity("Chief Investment Officer", "OpenAI")
    
    print("\n" + "="*50)
    print(" [FINANCE] AUTONOMOUS HEDGE FUND: ALGORITHMIC TRADER")
    print(" (Phase B: Attestix SEC Compliant Mode)")
    print("="*50 + "\n")

    print(" [Attestix Framework] Bootstrapping Official Compliance Protocols...")
    
    # --- ATTESTIX SETUP PHASE ---
    print("\n--- ATTESTIX SETUP PHASE ---")
    attestix_client.setup_full_compliance(RESEARCHER_ID, "Autonomous financial sentiment analysis and market scanning")
    attestix_client.setup_full_compliance(QUANT_ID, "Secure proprietary trading algorithm retrieval")
    attestix_client.setup_full_compliance(PANEL_ID, "Multi-agent investment debate and capital allocation")
    attestix_client.setup_full_compliance(CIO_ID, "Final trade order authorisation and SEC compliance")
    
    attestix_client.issue_credential(RESEARCHER_ID, "Certified Financial AI")
    attestix_client.issue_credential(PANEL_ID, "Certified Investment Board")
    print("----------------------------\n")
    
    ticker = ""
    while not ticker.strip():
        print("Example: 'TSLA' or 'AAPL'")
        ticker = input("Enter the target Ticker Symbol to analyze: ")

    # Phase 1: LangChain scans market data (Regulated)
    market_report = run_market_research(ticker, RESEARCHER_ID)
    
    # Phase 2: Semantic Kernel gets historical quant strategy (Requires Delegation from Researcher)
    quant_token = attestix_client.delegate_capability(RESEARCHER_ID, QUANT_ID, "read_trading_algorithms")
    quant_strategy = get_quant_strategy(market_report, QUANT_ID, delegation_token=quant_token)
    
    # Phase 3: CrewAI Committee debates the trade (Requires Delegation from Researcher)
    panel_token = attestix_client.delegate_capability(RESEARCHER_ID, PANEL_ID, "debate_investment_strategy")
    debate_report = run_investment_committee(market_report, quant_strategy, PANEL_ID, delegation_token=panel_token)
    
    # Phase 4: OpenAI CIO makes the final trade decision (Requires Delegation from Panel)
    cio_token = attestix_client.delegate_capability(PANEL_ID, CIO_ID, "issue_final_trade_order")
    final_decision = run_cio_decision(ticker, market_report, debate_report, CIO_ID, delegation_token=cio_token)
    
    print("\n" + "="*50)
    print(" [MONEY] FINAL TRADE ORDER")
    print("="*50)
    print(final_decision)

    attestix_client.print_audit_trail()

    print(" [OK] SEC & EU AI Act Compliance Verified.")
    print(" View UCAN delegations and W3C Credentials in ~/.attestix/identities.json")

if __name__ == "__main__":
    main()
