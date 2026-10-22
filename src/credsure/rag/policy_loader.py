"""Credit Policy Document Loader and Semantic Section Splitter.

Parses bank underwriting guidelines (.txt, .md, .pdf) into structured chunks
enriched with metadata (rule_category, min_score, section_title) for Qdrant indexing.
"""

import os
from typing import Dict, List, Any, Optional


class PolicyDocumentLoader:
    """Loads and splits institutional credit policy documents into structured chunks."""

    def __init__(self, policy_dir: str = "data/policies"):
        self.policy_dir = policy_dir

    def load_text_file(self, file_path: str) -> str:
        """Read text or markdown policy file."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def load_pdf_file(self, file_path: str) -> str:
        """Extract text from PDF file using pypdf."""
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            return text
        except Exception as e:
            print(f"Warning: Failed to load PDF {file_path}: {e}")
            return ""

    def get_seed_policy_chunks(self) -> List[Dict[str, Any]]:
        """Structured seed policy chunks for instant indexing in Qdrant."""
        return [
            {
                "id": "POL-TIER-01",
                "section_title": "FICO-Equivalent Score Thresholds & Approval Tiers",
                "rule_category": "score_thresholds",
                "min_score": 680,
                "text": (
                    "Underwriting Guidelines POL-CR-2026-V4 Section 1.1: Minimum FICO score for "
                    "instantaneous automated approval is 680 (Tier 2 Prime). Borrowers with scores >= 740 "
                    "qualify for Tier 1 Super Prime with preferential interest margins. Scores between 620 and 679 "
                    "are classified as Tier 3 Near-Prime and strictly require manual Senior Underwriter review and "
                    "at least 6 months verified liquid reserves. Scores below 620 trigger presumptive decline or "
                    "mandatory Adverse Action notices pursuant to FCRA."
                ),
                "metadata": {
                    "rule_category": "score_thresholds",
                    "min_score": 680,
                    "target_action": "Approval / Review Tiers",
                    "authority": "Senior Credit Committee",
                },
            },
            {
                "id": "POL-UTIL-02",
                "section_title": "Revolving Credit Utilization Ceiling",
                "rule_category": "utilization",
                "min_score": 0,
                "text": (
                    "Underwriting Guidelines POL-CR-2026-V4 Section 1.2: Prudential target utilization is "
                    "<= 30.0%. Utilization between 30.1% and 45.0% is acceptable for Prime borrowers. Hard "
                    "regulatory cap is set at 45.0%. Accounts exceeding 45.0% utilization incur a mandatory "
                    "scorecard penalty of -50 points and cannot receive credit line expansions. Utilization >= 85.0% "
                    "is classified as Overextended Distress and flagged for credit line curtailment."
                ),
                "metadata": {
                    "rule_category": "utilization",
                    "min_score": 0,
                    "max_utilization_pct": 45.0,
                    "target_action": "Credit Line Curtailment / Penalty",
                    "authority": "Risk Management Department",
                },
            },
            {
                "id": "POL-DELINQ-03",
                "section_title": "Delinquency Escalation & Adverse Actions",
                "rule_category": "delinquency",
                "min_score": 0,
                "text": (
                    "Underwriting Guidelines POL-CR-2026-V4 Section 1.3: Accounts with 30-day delinquency "
                    "(PAY_0 = 1) undergo credit line expansion freeze for 6 months. Accounts with 60-day "
                    "delinquency (PAY_0 = 2) incur an automatic -70 points credit score deduction, rate "
                    "increases, and mandatory adverse action. 90-day delinquency (PAY_0 >= 3) results in "
                    "immediate revocation of revolving charging privileges and transfer to Institutional Collections."
                ),
                "metadata": {
                    "rule_category": "delinquency",
                    "min_score": 0,
                    "target_action": "Adverse Action / Line Freeze",
                    "authority": "Loss Mitigation",
                },
            },
            {
                "id": "POL-DTI-04",
                "section_title": "Debt-to-Income (DTI) Prudential Limits",
                "rule_category": "dti",
                "min_score": 0,
                "text": (
                    "Underwriting Guidelines POL-CR-2026-V4 Section 1.4: Standard maximum Debt-to-Income (DTI) "
                    "ratio is 43.0% of gross verifiable monthly income. Exceptional maximum DTI of 45.0% is "
                    "permitted only for applicants with credit scores >= 720 and minimum 12 months verified liquid "
                    "assets. Any applicant with DTI exceeding 50.0% is disqualified unconditionally from unsecured facilities."
                ),
                "metadata": {
                    "rule_category": "dti",
                    "min_score": 0,
                    "max_dti_pct": 45.0,
                    "target_action": "DTI Eligibility Verification",
                    "authority": "Credit Underwriting Committee",
                },
            },
            {
                "id": "POL-BASEL-05",
                "section_title": "Basel Expected Loss & Capital Adequacy Framework",
                "rule_category": "basel_capital",
                "min_score": 0,
                "text": (
                    "Underwriting Guidelines POL-CR-2026-V4 Section 2.1: Institutional Expected Loss (EL) is "
                    "calculated pursuant to Basel Committee standards as EL = PD * EAD * LGD. Unused commitments "
                    "are assessed at 20.0% Credit Conversion Factor (CCF), producing EAD = Drawn + (20% * Undrawn). "
                    "Regulatory Loss Given Default (LGD) benchmark is fixed at 45.0% for retail revolving portfolios."
                ),
                "metadata": {
                    "rule_category": "basel_capital",
                    "min_score": 0,
                    "default_lgd": 0.45,
                    "ccf": 0.20,
                    "target_action": "Institutional Capital Reserve Allocation",
                    "authority": "Treasury & Capital Markets",
                },
            },
            {
                "id": "POL-STRESS-06",
                "section_title": "Macroeconomic Perturbation & Capital Stress Testing",
                "rule_category": "stress_testing",
                "min_score": 0,
                "text": (
                    "Underwriting Guidelines POL-CR-2026-V4 Section 2.2: Institutional portfolios must withstand "
                    "a 99.0% Value-at-Risk (VaR) 1-year loss horizon under simulated stress scenarios. Standard scenarios "
                    "include Mild Recession (+1 mo delay shift, +10% balance expansion, +20% PD multiplier) and Severe "
                    "Stagflation (+2 mo delay shift, +15% balance expansion, +50% PD multiplier, LGD 60%)."
                ),
                "metadata": {
                    "rule_category": "stress_testing",
                    "min_score": 0,
                    "target_action": "CCAR / DFAST Stress Testing",
                    "authority": "Enterprise Risk Management",
                },
            },
            {
                "id": "POL-FAIR-07",
                "section_title": "Equal Credit Opportunity Act (ECOA) & FCRA Disclosures",
                "rule_category": "regulatory_compliance",
                "min_score": 0,
                "text": (
                    "Underwriting Guidelines POL-CR-2026-V4 Section 3: In compliance with Regulation B (ECOA), "
                    "all credit decisions are made strictly on financial and behavioral risk factors without regard "
                    "to protected demographic attributes. FCRA Section 615 mandates that whenever adverse action is "
                    "taken, the applicant must receive written notice detailing their numerical credit score, the 300-850 "
                    "range, and the top 4 score factors that contributed negatively to the decision."
                ),
                "metadata": {
                    "rule_category": "regulatory_compliance",
                    "min_score": 0,
                    "target_action": "FCRA Adverse Action Notice",
                    "authority": "Compliance & Legal",
                },
            },
        ]

    def load_all_chunks(self) -> List[Dict[str, Any]]:
        """Load seed chunks plus any additional files present in the policy directory."""
        chunks = self.get_seed_policy_chunks()

        if os.path.exists(self.policy_dir):
            for file_name in os.listdir(self.policy_dir):
                file_path = os.path.join(self.policy_dir, file_name)
                if file_name.endswith(".txt") or file_name.endswith(".md"):
                    content = self.load_text_file(file_path)
                    if content and not any(c["id"] in file_name for c in chunks):
                        chunks.append({
                            "id": f"FILE-{file_name}",
                            "section_title": file_name.replace(".txt", "").replace("_", " ").title(),
                            "rule_category": "general_policy",
                            "min_score": 0,
                            "text": content[:1500],
                            "metadata": {"source_file": file_name, "rule_category": "general_policy"},
                        })
                elif file_name.endswith(".pdf"):
                    content = self.load_pdf_file(file_path)
                    if content:
                        chunks.append({
                            "id": f"PDF-{file_name}",
                            "section_title": file_name.replace(".pdf", "").replace("_", " ").title(),
                            "rule_category": "pdf_policy",
                            "min_score": 0,
                            "text": content[:1500],
                            "metadata": {"source_file": file_name, "rule_category": "pdf_policy"},
                        })

        return chunks
