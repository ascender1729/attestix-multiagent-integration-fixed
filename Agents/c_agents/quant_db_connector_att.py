import json
from pathlib import Path
from c_agents.attestix_client import attestix_client

def get_quant_strategy(market_report: str, agent_id: str, *, delegation_token: str) -> str:
    """Semantic Kernel Node: Queries the internal database for matching quant strategies (Regulated)."""
    print(f"\n--- PHASE 2: SEMANTIC KERNEL QUANT DB ---")
    print(" [Semantic Kernel - Regulated] Securely querying proprietary trading algorithms...")
    
    # --- ATTESTIX DELEGATION GATE ---
    if not delegation_token:
        raise PermissionError("[Attestix] DENIED - delegation_token required for read_trading_algorithms")
    attestix_client.verify_token(delegation_token, "read_trading_algorithms")

    # --- ATTESTIX CONFORMITY GATE ---
    if not attestix_client.check_conformity(agent_id):
        raise PermissionError("Attestix Gatekeeper blocked execution. Node failed conformity assessment.")

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
            
        # --- ATTESTIX PROVENANCE LOGGING ---
        attestix_client.log_action(
            agent_id=agent_id,
            action_type="DB_QUERY",
            input_data=market_report,
            output_data=result,
            delegation_token=delegation_token
        )
            
        return result
            
    except Exception as e:
        return f"Error connecting to quant database: {str(e)}"
