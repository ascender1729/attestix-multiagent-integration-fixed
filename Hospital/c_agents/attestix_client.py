import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
from attestix_client import make_attestix_client

attestix_client = make_attestix_client(
    issuer_name="Attestix General Hospital",
    capabilities=["medical_diagnosis", "patient_intake"],
    credential_type="MedicalBoardCertification",
    risk_label="Annex III - Health",
    domain_label="Hospital"
)
