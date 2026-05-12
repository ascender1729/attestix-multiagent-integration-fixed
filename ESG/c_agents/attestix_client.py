import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
from attestix_client import make_attestix_client

attestix_client = make_attestix_client(
    issuer_name="Attestix ESG Board",
    capabilities=["esg_auditing", "risk_assessment"],
    credential_type="ESGAuditCertification",
    risk_label="Annex III - Financial/ESG",
    domain_label="ESG Audit"
)
