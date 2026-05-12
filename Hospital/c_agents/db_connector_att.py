import json
from pathlib import Path
from c_agents.attestix_client import attestix_client

# 1. Identity Provisioning
AGENT_ID = attestix_client.provision_identity("Enterprise DB Node", "Semantic Kernel")

def get_patient_history(patient_id: str, *, delegation_token: str) -> dict:
    """Retrieves patient history with Attestix Compliance."""
    print(f"\n [Enterprise DB - Regulated] Securely querying records for {patient_id}...")

    # 2. UCAN Delegation Gate — must hold 'read_patient_record' capability
    if not delegation_token:
        raise PermissionError("[Attestix] DENIED - delegation_token required for read_patient_record")
    attestix_client.verify_token(delegation_token, "read_patient_record")
    
    # 3. Conformity Gatekeeper
    if not attestix_client.check_conformity(AGENT_ID):
        raise PermissionError("Attestix Conformity Assessment Failed.")
        
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
            output = record
        else:
            output = {"error": "Patient not found in database."}
            
    except Exception as e:
        output = {"error": str(e)}

    # 4. Provenance Logging
    attestix_client.log_action(AGENT_ID, "DB_QUERY", patient_id, str(output), delegation_token=delegation_token)
    return output
