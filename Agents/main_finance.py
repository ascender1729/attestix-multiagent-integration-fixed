import os
import sys
from dotenv import load_dotenv

# Ensure we can import from the Agents/ directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load the API key from the Hospital directory so we don't have to duplicate it
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Hospital', '.env')
load_dotenv(env_path)

from agents.market_researcher import run_market_research
from agents.quant_db_connector import get_quant_strategy
from agents.investment_committee import run_investment_committee
from agents.the_cio import run_cio_decision

def main():
    print("\n" + "="*50)
    print(" 📈 AUTONOMOUS HEDGE FUND: ALGORITHMIC TRADER")
    print(" (Phase A: Unregulated Mode - No Attestix Compliance)")
    print("="*50 + "\n")
    
    ticker = ""
    while not ticker.strip():
        print("Example: 'TSLA' or 'AAPL'")
        ticker = input("Enter the target Ticker Symbol to analyze: ")

    # Phase 1: LangChain scans market data
    market_report = run_market_research(ticker)
    
    # Phase 2: Semantic Kernel gets historical quant strategy
    quant_strategy = get_quant_strategy(market_report)
    
    # Phase 3: CrewAI Committee debates the trade
    debate_report = run_investment_committee(market_report, quant_strategy)
    
    # Phase 4: OpenAI CIO makes the final trade decision
    final_decision = run_cio_decision(ticker, market_report, debate_report)
    
    print("\n" + "="*50)
    print(" 💰 FINAL TRADE ORDER")
    print("="*50)
    print(final_decision)
    print("\n" + "="*50)
    print(" ⚠️ Warning: This is the Unregulated Mode. No cryptographic provenance was logged.")
    print(" If the SEC investigates this trade, the firm has no proof of the AI's rationale.")

if __name__ == "__main__":
    main()
