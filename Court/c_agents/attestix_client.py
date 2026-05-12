import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
from attestix_client import make_attestix_client

attestix_client = make_attestix_client(
    issuer_name="Attestix Supreme Court",
    capabilities=["legal_analysis", "contract_drafting"],
    credential_type="LegalBarCertification",
    risk_label="Annex III - Legal/Justice",
    domain_label="Autonomous Court"
)
