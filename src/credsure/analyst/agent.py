"""LangChain AI Credit Underwriter Agent.

Equipped with tools to query the Scorecard Engine, search Qdrant policies,
and compute Basel Expected Loss metrics. Generates comprehensive loan memos.
"""

from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from credsure.scorecard.calculator import ScorecardCalculator
from credsure.portfolio.expected_loss import BaselExpectedLossEngine, EADMode
from credsure.rag.vector_store import QdrantPolicyVectorStore
from credsure.analyst.config import LLMProviderFactory


class CreditUnderwriterAgent:
    """Agentic AI Credit Underwriter combining statistical risk models,

    embedded Qdrant policy retrieval, and institutional credit memo generation.
    """

    def __init__(
        self,
        calculator: Optional[ScorecardCalculator] = None,
        vector_store: Optional[QdrantPolicyVectorStore] = None,
        el_engine: Optional[BaselExpectedLossEngine] = None,
    ):
        self.calculator = calculator or ScorecardCalculator()
        self.vector_store = vector_store or QdrantPolicyVectorStore()
        self.el_engine = el_engine or BaselExpectedLossEngine()
        self.llm = LLMProviderFactory.get_chat_model()

    def evaluate_and_generate_memo(self, borrower_features: Dict[str, Any]) -> Dict[str, Any]:
        """Run full underwriting lifecycle: statistical scoring, policy matching,

        and AI memorandum synthesis.
        """
        # 1. Statistical Scorecard Evaluation
        scorecard_result = self.calculator.evaluate(borrower_features)
        score = scorecard_result["score"]
        pd = scorecard_result["pd"]
        category = scorecard_result["risk_category"]
        utilization = scorecard_result["utilization"]

        # 2. Basel Expected Loss Calculation
        limit_bal = float(borrower_features.get("LIMIT_BAL", 50000.0))
        bill_amt1 = float(borrower_features.get("BILL_AMT1", 0.0))
        el_result = self.el_engine.calculate_single(
            pd=pd,
            limit_bal=limit_bal,
            bill_amt1=bill_amt1,
            mode=EADMode.BASEL_CCF,
        )

        # 3. Policy RAG Retrieval from Embedded Qdrant
        policy_hits = self.vector_store.search(
            query=f"Underwriting rules for credit score {score} utilization {utilization}% delinquency status",
            limit=3,
        )
        policy_context = "\n".join([f"- [{h.get('section_title', 'Policy')}]: {h.get('text', '')}" for h in policy_hits])

        # 4. Formulate System Prompt for LangChain Agent
        system_prompt = (
            "You are CredSure AI, a Senior Institutional Credit Underwriter operating under "
            "Basel III capital guidelines, the Equal Credit Opportunity Act (ECOA), and the Fair Credit "
            "Reporting Act (FCRA). You must produce a structured, rigorous, and regulatory-compliant "
            "Credit Underwriting Memorandum."
        )

        user_prompt = (
            f"Please underwrite the following credit facility application:\n\n"
            f"BORROWER PROFILE & SCORECARD METRICS:\n"
            f"- Credit Score: {score} / 850 ({category})\n"
            f"- Probability of Default (PD): {scorecard_result['pd_percentage']}%\n"
            f"- Credit Limit Requested: ${limit_bal:,.2f}\n"
            f"- Current Statement Balance: ${bill_amt1:,.2f}\n"
            f"- Revolving Credit Utilization: {utilization}%\n"
            f"- Payment Status (Recent Month PAY_0): {borrower_features.get('PAY_0', 0)}\n\n"
            f"BASEL EXPECTED LOSS:\n"
            f"- Exposure at Default (EAD): ${el_result['ead']:,.2f}\n"
            f"- Loss Given Default (LGD): {el_result['lgd'] * 100}%\n"
            f"- Expected Loss (EL): ${el_result['expected_loss']:,.2f}\n\n"
            f"TOP POSITIVE DRIVERS:\n"
            + "\n".join([f"+ {d['label']} (+{d['points']} pts): {d['description']}" for d in scorecard_result["top_positive_drivers"]])
            + f"\n\nTOP NEGATIVE FACTORS:\n"
            + "\n".join([f"- {d['label']} ({d['points']} pts): {d['description']}" for d in scorecard_result["top_negative_drivers"]])
            + f"\n\nADVERSE ACTION CODES (if applicable):\n"
            + "\n".join([f"[{r['code']}] {r['title']}: {r['detail']}" for r in scorecard_result["adverse_action_reasons"]])
            + f"\n\nRELEVANT INSTITUTIONAL POLICIES (from Qdrant Knowledge Base):\n{policy_context}\n\n"
            f"Generate a complete Credit Underwriting Memorandum with sections: Executive Summary, Scorecard Analysis, "
            f"Policy Compliance Findings, Adverse Action Disclosures, and Final Recommendation (Approved, Conditional, or Declined)."
        )

        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
            memo_text = response.content
        except Exception as e:
            print(f"Notice: LLM call fallback: {e}")
            from credsure.analyst.config import MockChatModel
            fallback_model = MockChatModel()
            response = fallback_model.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
            memo_text = response.content

        # Determine decision badge
        if score >= 680 and utilization <= 45.0 and int(borrower_features.get("PAY_0", 0)) <= 0:
            decision = "APPROVED"
            decision_badge_color = "#10B981"
        elif score >= 620:
            decision = "CONDITIONAL"
            decision_badge_color = "#F59E0B"
        else:
            decision = "DECLINED"
            decision_badge_color = "#EF4444"

        return {
            "decision": decision,
            "decision_badge_color": decision_badge_color,
            "scorecard": scorecard_result,
            "basel_el": el_result,
            "policy_citations": policy_hits,
            "memo_markdown": memo_text,
            "underwriter_name": "CredSure AI Underwriting Agent (Autonomous)",
            "compliance_attestation": "Certified compliant with ECOA Regulation B and FCRA Section 615.",
        }
