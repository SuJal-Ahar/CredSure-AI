"""Credit Underwriting Memorandum Formatter.

Produces institutional-grade, audit-ready credit memos compliant with Basel III,
Equal Credit Opportunity Act (ECOA - Reg B), and Fair Credit Reporting Act (FCRA).
"""

from typing import Dict, List, Any
from datetime import datetime, timezone


class CreditMemoGenerator:
    """Formats structured Credit Underwriting Memos from scorecard and policy findings."""

    @staticmethod
    def format_memo(
        borrower_features: Dict[str, Any],
        scorecard_result: Dict[str, Any],
        basel_el: Dict[str, Any],
        policy_citations: List[Dict[str, Any]],
        ai_memo_text: str,
        applicant_name: str = "Borrower Application #78421",
    ) -> Dict[str, Any]:
        """Synthesize all underwriting analytical vectors into an institutional loan package."""
        score = scorecard_result["score"]
        category = scorecard_result["risk_category"]
        pd = scorecard_result["pd_percentage"]
        limit = float(borrower_features.get("LIMIT_BAL", 50000.0))
        drawn = float(borrower_features.get("BILL_AMT1", 0.0))
        util = scorecard_result["utilization"]
        recent_delinq = int(borrower_features.get("PAY_0", 0))

        # Initial determination
        if score >= 680 and util <= 45.0 and recent_delinq <= 0:
            rec_status = "APPROVED"
            rec_badge = "Automated Prime Facility Approval"
        elif score >= 620:
            rec_status = "CONDITIONAL"
            rec_badge = "Conditional Senior Review Tier"
        else:
            rec_status = "DECLINED"
            rec_badge = "Presumptive Decline (Adverse Action)"

        timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y - %H:%M UTC")

        memo_sections = {
            "header": {
                "applicant_id": applicant_name,
                "assessment_date": timestamp,
                "facility_type": "Unsecured Revolving Consumer Credit Line",
                "authorized_limit": f"${limit:,.2f}",
                "drawn_statement_balance": f"${drawn:,.2f}",
                "revolving_utilization": f"{util}%",
                "determination": rec_status,
                "tier_badge": rec_badge,
            },
            "scorecard_summary": {
                "credit_score": score,
                "score_scale": "300 to 850 (FICO-Equivalent)",
                "default_probability": f"{pd}%",
                "risk_category": category,
                "risk_color": scorecard_result["risk_color"],
                "positive_drivers": scorecard_result["top_positive_drivers"],
                "negative_drivers": scorecard_result["top_negative_drivers"],
            },
            "basel_exposure": {
                "ead": f"${basel_el['ead']:,.2f}",
                "lgd": f"{round(basel_el['lgd'] * 100, 1)}%",
                "expected_loss": f"${basel_el['expected_loss']:,.2f}",
                "el_rate_bps": f"{round(basel_el.get('el_rate_percent', 0.0) * 100, 0)} bps",
            },
            "adverse_action": {
                "reasons": scorecard_result["adverse_action_reasons"],
                "notice_required": len(scorecard_result["adverse_action_reasons"]) > 0 or score < 680,
                "statutory_notice": (
                    "In compliance with Section 615 of the Fair Credit Reporting Act (15 U.S.C. § 1681m), "
                    "if adverse action is taken or terms are modified, the applicant is entitled to a written "
                    "statement of specific reasons and a free disclosure of their credit file."
                ),
            },
            "policy_audit": policy_citations,
            "ai_underwriter_memo": ai_memo_text,
            "regulatory_disclaimer": (
                "CredSure AI complies with the Equal Credit Opportunity Act (ECOA - Regulation B, 12 CFR Part 1002). "
                "Credit evaluation models operate without regard to race, color, religion, national origin, "
                "sex, marital status, age, or public assistance status."
            ),
        }

        return memo_sections
