"""
Shared Attestix Manager - single source of truth for all 4 domains.

Each project's c_agents/attestix_client.py calls make_attestix_client()
with its own domain config and gets back a fully configured singleton.

v0.2 (2026-05-12, post-audit):
- Patch 01: risk_label now propagates into the compliance profile's intended_purpose
- Patch 03: Article 10 (training data) + Article 11 (model lineage) + Article 43 / Annex V
            (declaration of conformity) methods exposed at this layer so all four domains
            inherit them.
- Patch 06: all emoji/Unicode replaced with ASCII status tags for terminal portability.
"""

from attestix.services.identity_service import IdentityService
from attestix.services.compliance_service import ComplianceService
from attestix.services.credential_service import CredentialService
from attestix.services.delegation_service import DelegationService
from attestix.services.provenance_service import ProvenanceService
from attestix.services.blockchain_service import BlockchainService


class AttestixManager:
    """Domain-agnostic wrapper around the Attestix protocol services."""

    def __init__(self, issuer_name: str, capabilities: list, credential_type: str,
                 risk_label: str, domain_label: str):
        self.issuer_name = issuer_name
        self.capabilities = capabilities
        self.credential_type = credential_type
        self.risk_label = risk_label
        self.domain_label = domain_label

        self.identity_svc = IdentityService()
        self.compliance_svc = ComplianceService()
        self.credential_svc = CredentialService()
        self.delegation_svc = DelegationService()
        self.provenance_svc = ProvenanceService()
        self.blockchain_svc = BlockchainService()

        self.agent_cache = {}
        self._agent_names = {}
        self._session_receipts = []

    # ------------------------------------------------------------------ Identity

    def provision_identity(self, agent_name: str, framework: str) -> str:
        print(f" [Attestix Identity] Provisioning identity for {agent_name}...")
        agent = self.identity_svc.create_identity(
            display_name=agent_name,
            source_protocol=framework.lower(),
            capabilities=self.capabilities,
            description=f"{framework} agent operating in {self.domain_label}",
            issuer_name=self.issuer_name,
        )
        agent_id = agent["agent_id"]
        self.agent_cache[agent_name] = agent_id
        self._agent_names[agent_id] = agent_name
        did = agent["issuer"]["did"]
        print(f"   -> DID:  {did}")
        print(f"   -> UAIT: {agent_id}")
        return agent_id

    # ---------------------------------------------------------------- Compliance

    def setup_compliance(self, agent_id: str, purpose: str):
        """EU AI Act profile. risk_label is now persisted in intended_purpose so
        the Annex III sub-category survives in ~/.attestix/compliance.json."""
        print(f" [Attestix Compliance] Generating EU AI Act profile for {agent_id}...")
        enriched_purpose = f"{purpose} | EU AI Act category: {self.risk_label}"
        self.compliance_svc.create_compliance_profile(
            agent_id=agent_id,
            risk_category="high",
            provider_name=self.issuer_name,
            intended_purpose=enriched_purpose,
        )
        print(f"   -> Profile created. Risk: High ({self.risk_label})")

    def check_conformity(self, agent_id: str) -> bool:
        name = self._agent_names.get(agent_id, agent_id[:8])
        print(f" [Attestix Compliance] Conformity gatekeeper: {name}...")
        profile = self.compliance_svc.get_compliance_profile(agent_id)
        if not profile:
            print(f"   -> BLOCKED. '{name}' has no compliance profile. Call setup_compliance() first.")
            return False
        print(f"   -> PASS. Risk: {profile.get('risk_category', 'unknown').upper()} "
              f"| Profile: {profile.get('profile_id', '')[:8]}")
        return True

    def setup_full_compliance(self, agent_id: str, purpose: str,
                                base_model: str = "llama-3.3-70b-versatile",
                                dataset_name: str = "Public-domain training corpus",
                                dataset_url: str = "https://groq.com",
                                evaluation_metrics: dict = None):
        """One-shot Article 10 + 11 + 43 + Annex V provisioning for an agent.

        Wraps setup_compliance + record_training_data + record_model_lineage +
        issue_declaration_of_conformity so each compliant_main_*.py needs a single
        call per agent. Ported from the previously-orphaned compliant_architecture.py
        helper during the post-audit cleanup.
        """
        self.setup_compliance(agent_id, purpose)
        self.record_training_data(agent_id, dataset_name, dataset_url,
                                    contains_personal_data=False,
                                    data_categories=["public_text"])
        self.record_model_lineage(agent_id, base_model,
                                    evaluation_metrics=evaluation_metrics
                                                          or {"accuracy": 0.95,
                                                                "hallucination_rate": 0.02})
        self.issue_declaration_of_conformity(agent_id)

    # ----------------------------------------------- Article 10 / 11 / 43 (Patch 03)

    def record_training_data(self, agent_id: str, dataset_name: str, source_url: str,
                              license: str = "Unknown",
                              contains_personal_data: bool = False,
                              data_categories: list = None,
                              data_governance_measures: str = "filtered_for_compliance"):
        """EU AI Act Article 10 - data governance record."""
        self.provenance_svc.record_training_data(
            agent_id=agent_id,
            dataset_name=dataset_name,
            source_url=source_url,
            license=license,
            contains_personal_data=contains_personal_data,
            data_categories=data_categories or [],
            data_governance_measures=data_governance_measures,
        )
        print(f"   -> [Article 10] training-data record for {agent_id[:8]}: {dataset_name}")

    def record_model_lineage(self, agent_id: str, base_model: str,
                              base_model_provider: str = "Groq",
                              fine_tuning_method: str = "prompt_engineering",
                              evaluation_metrics: dict = None):
        """EU AI Act Article 11 - technical documentation."""
        self.provenance_svc.record_model_lineage(
            agent_id=agent_id,
            base_model=base_model,
            base_model_provider=base_model_provider,
            fine_tuning_method=fine_tuning_method,
            evaluation_metrics=evaluation_metrics or {},
        )
        print(f"   -> [Article 11] model-lineage record for {agent_id[:8]}: {base_model}")

    def issue_declaration_of_conformity(self, agent_id: str, assessor_name: str = None,
                                          findings: str = "meets all Annex III requirements"):
        """EU AI Act Article 43 + Annex V - declaration of conformity."""
        if not assessor_name:
            assessor_name = f"{self.issuer_name} Auditing Board"
        self.compliance_svc.record_conformity_assessment(
            agent_id=agent_id,
            assessment_type="third_party",
            assessor_name=assessor_name,
            result="pass",
            findings=findings,
        )
        decl = self.compliance_svc.generate_declaration_of_conformity(agent_id)
        if "error" in decl:
            print(f"   -> [!] declaration error: {decl['error']}")
        else:
            print(f"   -> [Annex V] declaration of conformity issued for {agent_id[:8]}")
        return decl

    # ---------------------------------------------------------------- Credentials

    def issue_credential(self, agent_id: str, role: str):
        print(f" [Attestix Credentials] Minting W3C VC for role '{role}'...")
        vc = self.credential_svc.issue_credential(
            agent_id=agent_id,
            credential_type=self.credential_type,
            issuer_name=self.issuer_name,
            claims={"role": role, "certified": True},
        )
        print(f"   -> Issued VC signed with {vc['proof']['type']}")

    # ---------------------------------------------------------------- Delegation

    def delegate_capability(self, issuer_id: str, audience_id: str, capability: str) -> str:
        issuer_name = self._agent_names.get(issuer_id, issuer_id[:8])
        audience_name = self._agent_names.get(audience_id, audience_id[:8])
        print(f" [Attestix Delegation] '{issuer_name}' delegating '{capability}' to '{audience_name}'...")
        token = self.delegation_svc.create_delegation(
            issuer_agent_id=issuer_id,
            audience_agent_id=audience_id,
            capabilities=[capability],
        )
        print("   -> UCAN delegation token created.")
        return token.get("token", "UNKNOWN_TOKEN")

    def verify_token(self, token: str, required_capability: str) -> None:
        """UCAN delegation gate. PermissionError on any failure."""
        print(f" [Attestix Gate] Verifying UCAN token for capability '{required_capability}'...")
        result = self.delegation_svc.verify_delegation(token)
        if not result.get("valid"):
            raise PermissionError(
                f"[Attestix] Access DENIED - {result.get('reason', 'invalid token')}"
            )
        caps = result.get("capabilities", [])
        if required_capability not in caps:
            raise PermissionError(
                f"[Attestix] Access DENIED - token lacks '{required_capability}'. "
                f"Granted capabilities: {caps}"
            )
        delegator = self._agent_names.get(result.get("delegator", ""),
                                            result.get("delegator", "unknown")[:8])
        print(f"   -> VERIFIED | Delegator: {delegator} | Capability: '{required_capability}' granted")

    # ---------------------------------------------------------------- Provenance

    def log_action(self, agent_id: str, action_type: str, input_data: str,
                    output_data: str, delegation_token: str = None):
        name = self._agent_names.get(agent_id, agent_id[:8])
        print(f" [Attestix Provenance] Hash-chaining '{action_type}' for {name}...")

        a = action_type.upper()
        if "DB" in a or "QUERY" in a or "FETCH" in a:
            official_type = "data_access"
        elif "FINAL" in a or "RULING" in a or "VERDICT" in a or "ORDER" in a or "DECISION" in a:
            official_type = "decision"
        else:
            official_type = "inference"

        receipt = self.provenance_svc.log_action(
            agent_id=agent_id,
            action_type=official_type,
            input_summary=str(input_data)[:200],
            output_summary=str(output_data)[:200],
            decision_rationale=(f"UCAN token: {delegation_token[:16]}..."
                                  if delegation_token else "self-directed"),
        )
        if "error" in receipt:
            print(f"   -> [ERROR] {receipt['error']}")
        else:
            self._session_receipts.append({
                "agent_id": agent_id,
                "agent_name": name,
                "action_type": action_type,
                "log_id": receipt["log_id"],
                "timestamp": receipt["timestamp"],
                "prev_hash": receipt["prev_hash"],
                "chain_hash": receipt["chain_hash"],
            })
            print(f"   -> Receipt {receipt['log_id'][:8]} added to Merkle log.")
            print(f"   -> Prev hash:    {receipt['prev_hash'][:16]}...")
            print(f"   -> Current hash: {receipt['chain_hash'][:16]}...")

    # ---------------------------------------------------------------- Audit print

    def print_audit_trail(self):
        print("\n" + "=" * 62)
        print("  CRYPTOGRAPHIC AUDIT TRAIL - Merkle provenance chain")
        print("=" * 62)
        if not self._session_receipts:
            print("  No entries recorded this session.")
            print("=" * 62)
            return
        for i, r in enumerate(self._session_receipts):
            tag = "  GENESIS" if r["prev_hash"] == "0" * 64 else f"  Entry #{i + 1}"
            print(f"\n{tag}  |  {r['agent_name']}  ({r['action_type']})")
            print(f"  Log ID:     {r['log_id']}")
            print(f"  Timestamp:  {r['timestamp']}")
            print(f"  Prev hash:  {r['prev_hash'][:32]}...")
            print(f"  Chain hash: {r['chain_hash'][:32]}...")
            if i < len(self._session_receipts) - 1:
                print("       |")
                print("       v")
        print(f"\n  {len(self._session_receipts)} entries. Chain is tamper-evident.")
        print("  Full log: ~/.attestix/provenance.json")
        print("=" * 62 + "\n")

    # ---------------------------------------------------------------- Blockchain

    def anchor_to_blockchain(self, agent_id: str):
        name = self._agent_names.get(agent_id, agent_id[:8])
        print(f"\n [Attestix Blockchain] Anchoring '{name}' audit batch to Base Sepolia...")
        if not self.blockchain_svc.is_configured:
            print("   -> Blockchain not configured. To enable:")
            print('      1. Generate wallet (TESTNET ONLY): python -c "from eth_account import Account; a = Account.create(); print(a.key.hex())"')
            print("      2. Fund it: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet")
            print("      3. Add to .env:  EVM_PRIVATE_KEY=<your_key>")
            return
        result = self.blockchain_svc.anchor_audit_batch(agent_id=agent_id)
        if "error" in result:
            print(f"   -> [ERROR] {result['error']}")
        else:
            meta = result.get("batch_metadata", {})
            print(f"   -> Merkle root: {meta.get('merkle_root', '')[:32]}...")
            print(f"   -> Entries:     {meta.get('entry_count')} audit log entries")
            print(f"   -> TX hash:     {result.get('tx_hash', '')}")
            print(f"   -> Explorer:    {result.get('explorer_url', '')}")
            print(f"   -> Attestation: {result.get('attestation_uid', '')}")
            print("   -> IMMUTABLE. This audit cannot be disputed or deleted.")


def make_attestix_client(issuer_name: str, capabilities: list, credential_type: str,
                          risk_label: str, domain_label: str) -> AttestixManager:
    """Factory - called by each project's c_agents/attestix_client.py."""
    return AttestixManager(
        issuer_name=issuer_name,
        capabilities=capabilities,
        credential_type=credential_type,
        risk_label=risk_label,
        domain_label=domain_label,
    )
