"""LLM Provider Factory & Deterministic MockChatModel for CredSure AI Underwriter.

Seamlessly supports Groq Llama-3.3-70B, Google Gemini, OpenAI GPT-4o,
and a deterministic MockChatModel ensuring 100% offline capability without API keys.
"""

import os
from typing import Any, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration


class MockChatModel(BaseChatModel):
    """Deterministic fallback chat model for offline, zero-API-key execution."""

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        # Generate an institutional-grade credit memo based on prompt content
        last_message = messages[-1].content if messages else ""

        # Parse context keywords
        is_subprime = "subprime" in last_message.lower() or "delinquent" in last_message.lower()
        is_nearprime = "near-prime" in last_message.lower() or "conditional" in last_message.lower()

        if is_subprime:
            decision = "DECLINED (Adverse Action Notice Required)"
            summary = (
                "The applicant presents elevated default risk driven by severe delinquency and/or excessive "
                "revolving utilization. In accordance with Institutional Underwriting Policy POL-CR-2026-V4 "
                "and FCRA adverse action rules, this facility is declined."
            )
            conditions = [
                "Issue FCRA Notice of Adverse Action citing top score penalty factors.",
                "Mandatory 6-month seasoning period required prior to re-application.",
                "Applicant may re-apply under secured credit facility with 100% cash collateral.",
            ]
        elif is_nearprime:
            decision = "CONDITIONAL APPROVAL"
            summary = (
                "The applicant exhibits acceptable credit characteristics but falls within the Tier 3 "
                "Near-Prime boundary (FICO 620-679). In accordance with Policy POL-CR-2026-V4 Section 1.1, "
                "manual underwriter approval is granted subject to compensatory underwriting covenants."
            )
            conditions = [
                "Borrower must furnish 6 months documented liquid cash reserves.",
                "Initial credit limit capped at $15,000 pending 12 consecutive on-time billing cycles.",
                "Maximum permissible utilization strictly capped at 35% on this account.",
            ]
        else:
            decision = "APPROVED (Tier 1/2 Prime Facility)"
            summary = (
                "The borrower demonstrates exemplary creditworthiness, robust debt service coverage, and "
                "pristine payment records. Fully compliant with Institutional Underwriting Standards POL-CR-2026-V4. "
                "Instant automated underwriting clearance granted."
            )
            conditions = [
                "Full requested credit limit authorized at prime margin.",
                "Qualifies for preferential Tier 1 interest rate pricing.",
                "Eligible for annual automatic credit line review.",
            ]

        response_text = (
            f"### CREDIT COMMITTEE UNDERWRITING MEMORANDUM\n\n"
            f"**Decision Status**: {decision}\n\n"
            f"**Executive Underwriting Summary**:\n{summary}\n\n"
            f"**Underwriting Conditions & Covenants**:\n"
            + "\n".join([f"- {c}" for c in conditions])
            + f"\n\n**Regulatory Fair Lending Attestation**:\n"
            f"This underwriting assessment strictly adheres to the Equal Credit Opportunity Act (ECOA - Regulation B) "
            f"and the Fair Credit Reporting Act (FCRA). Protected demographic attributes are excluded from all "
            f"credit scoring and decisioning algorithms."
        )

        generation = ChatGeneration(message=AIMessage(content=response_text))
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "credsure-mock-chat"


class LLMProviderFactory:
    """Factory for initializing LLM instances based on environment configuration."""

    @staticmethod
    def get_chat_model() -> BaseChatModel:
        provider = os.getenv("LLM_PROVIDER", "").lower()
        groq_key = os.getenv("GROQ_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        # 1. Groq Provider
        if provider == "groq" or (not provider and groq_key):
            try:
                from langchain_groq import ChatGroq
                model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
                return ChatGroq(model_name=model_name, temperature=0.2, groq_api_key=groq_key)
            except Exception as e:
                print(f"Notice: Failed to initialize ChatGroq: {e}. Falling back.")

        # 2. Google Gemini Provider
        if provider in ["gemini", "google"] or (not provider and gemini_key):
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
                return ChatGoogleGenerativeAI(model=model_name, temperature=0.2, google_api_key=gemini_key)
            except Exception as e:
                print(f"Notice: Failed to initialize ChatGoogleGenerativeAI: {e}. Falling back.")

        # 3. OpenAI Provider
        if provider == "openai" or (not provider and openai_key):
            try:
                from langchain_openai import ChatOpenAI
                model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
                return ChatOpenAI(model_name=model_name, temperature=0.2, openai_api_key=openai_key)
            except Exception as e:
                print(f"Notice: Failed to initialize ChatOpenAI: {e}. Falling back.")

        # Default: MockChatModel
        return MockChatModel()
