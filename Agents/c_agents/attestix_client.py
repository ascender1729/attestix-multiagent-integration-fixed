import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
from attestix_client import make_attestix_client

attestix_client = make_attestix_client(
    issuer_name="Attestix Investment Bank",
    capabilities=["financial_analysis", "investment_decision"],
    credential_type="FinancialAnalystCertification",
    risk_label="Annex III - Financial",
    domain_label="Algorithmic Hedge Fund"
)
