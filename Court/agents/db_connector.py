import json
from pathlib import Path

def get_case_law_precedents(keywords: list) -> str:
    """Retrieves legal precedents from the secure case law database based on keywords."""
    print(f"\n [Semantic Kernel] Querying secure legal database for {keywords}...")
    
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
            print(" [Semantic Kernel] Found matching case law precedents.")
            return "\n".join(found_cases)
        else:
            return "No matching case law precedents found in database."
            
    except Exception as e:
        return f"Error connecting to legal database: {str(e)}"
