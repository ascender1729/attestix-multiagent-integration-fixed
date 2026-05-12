import json
from pathlib import Path

def get_quant_strategy(market_report: str) -> str:
    """Semantic Kernel Node: Queries the internal database for matching quant strategies."""
    print(f"\n--- PHASE 2: SEMANTIC KERNEL QUANT DB ---")
    print(" [Semantic Kernel] Querying proprietary trading algorithms based on live sentiment...")
    
    db_path = Path(__file__).parent.parent / "data" / "quant_strategies_db.json"
    
    try:
        with open(db_path, "r") as f:
            data = json.load(f)
            
        strategies = data.get("strategies", [])
        
        # Dynamic matching based on live sentiment discovered on the web
        report_upper = market_report.upper()
        if "BULLISH" in report_upper:
            match = next((s for s in strategies if s["sentiment_trigger"] == "BULLISH"), None)
        elif "BEARISH" in report_upper:
            match = next((s for s in strategies if s["sentiment_trigger"] == "BEARISH"), None)
        else:
            match = next((s for s in strategies if s["sentiment_trigger"] == "NEUTRAL"), None)
                
        if match:
            result = json.dumps([match], indent=2)
            print(f" [Semantic Kernel] Deployed Strategy: {match['strategy_name']}")
        else:
            result = "No matching historical strategy found. Trade at your own risk."
            
        return result
            
    except Exception as e:
        return f"Error connecting to quant database: {str(e)}"
