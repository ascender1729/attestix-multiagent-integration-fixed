import json
import os
from pathlib import Path

def get_patient_history(patient_id: str) -> dict:
    """
    Simulates an Enterprise Database Connector (e.g., Semantic Kernel talking to an SQL server).
    Retrieves the patient's medical history from the secure mock database.
    """
    print(f" [Enterprise DB] Securely querying records for {patient_id}...")
    
    # Path to the mock database
    db_path = Path(__file__).parent.parent / "data" / "mock_hospital_db.json"
    
    try:
        with open(db_path, "r") as f:
            data = json.load(f)
            
        patients = data.get("patients", {})
        if patient_id in patients:
            record = patients[patient_id]
            print(f" [Enterprise DB] Found records for {record.get('name')}.")
            print(f" [Enterprise DB] Patient Record  : {{")
            for k, v in record.items():
                if isinstance(v, list):
                    v_fmt = "[\n" + "".join(f"      {i},\n" for i in v) + "    ]"
                    print(f"    {k:<24}: {v_fmt}")
                else:
                    print(f"    {k:<24}: {v}")
            print(f" }}")
            return record
        else:
            print(f" [Enterprise DB] No records found for {patient_id}.")
            return {"error": "Patient not found in database."}
            
    except Exception as e:
        print(f" [Enterprise DB] Database connection error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    print(get_patient_history("P-009"))
