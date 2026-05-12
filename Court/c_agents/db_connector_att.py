import json
from pathlib import Path
from c_agents.attestix_client import attestix_client

def get_case_law_precedents(keywords: list, agent_id: str, *, delegation_token: str) -> str:
    """Retrieves legal precedents from the secure case law database based on keywords (Regulated)."""
    print(f"\n [Semantic Kernel - Regulated] Securely querying case law records...")
    
    # --- ATTESTIX DELEGATION GATE ---
    if not delegation_token:
        raise PermissionError("[Attestix] DENIED - delegation_token required for read_legal_precedents")
    attestix_client.verify_token(delegation_token, "read_legal_precedents")

    # --- ATTESTIX CONFORMITY GATE ---
    if not attestix_client.check_conformity(agent_id):
        raise PermissionError("Attestix Gatekeeper blocked execution. Node failed conformity assessment.")
    
    db_path = Path(__file__).parent.parent / "data" / "mock_legal_db.json"
    
    try:
        with open(db_path, "r") as f:
            data = json.load(f)
            
        precedents = data.get("precedents", {})
        found_cases = []
        
        for key in keywords:
            if key in precedents:
                found_cases.append(f"Found Precedent ({key}): {precedents[key]['title']} - {precedents[key]['ruling']}")
                
        if found_cases:
            result = "\n".join(found_cases)
            print(" [Semantic Kernel] Found matching case law precedents.")
        else:
            result = "No matching case law precedents found in database."
            
        # --- ATTESTIX PROVENANCE LOGGING ---
        attestix_client.log_action(
            agent_id=agent_id,
            action_type="DB_QUERY",
            input_data=str(keywords),
            output_data=result,
            delegation_token=delegation_token
        )
            
        return result
            
    except Exception as e:
        return f"Error connecting to legal database: {str(e)}"
