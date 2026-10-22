# CredSure AI 🛡️
### Production-Grade Regulatory Credit Risk Scorecard & Autonomous AI Underwriter

[![Python](https://img.shields.io/badge/Python-3.11--3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14_App_Router-black.svg)](https://nextjs.org/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Embedded_Local_Disk-DC2626.svg)](https://qdrant.tech/)
[![Compliance](https://img.shields.io/badge/Compliance-ECOA_Reg_B_%26_FCRA_615-green.svg)](#regulatory-compliance)

CredSure AI is an institutional credit decisioning platform combining transparent statistical credit scorecards, Basel III Expected Loss analytics, 1,000-path Monte Carlo Value-at-Risk (VaR), embedded local vector search (Qdrant), and an autonomous LangChain credit underwriter agent.

---

## 🏛️ Core Architecture Principles

1. **Interpretable Statistical Models**: Zero black-box neural networks or opaque models. Risk scoring is strictly implemented using auditable statistical formulations:
   - Weight of Evidence (WoE) and Information Value (IV)
   - FICO-scale Points conversion (300 to 850) with transparent score drivers
   - Basel Expected Loss ($EL = PD \times EAD \times LGD$)
   - 1,000-scenario Monte Carlo Tail Risk ($VaR_{95}$, $VaR_{99}$, $CVaR$)
2. **Embedded Local Vector Database**: Qdrant runs directly on disk (`path="./data/qdrant_storage"`, zero external database server required).
3. **Local CPU Embeddings**: `BAAI/bge-small-en-v1.5` dense vectors generated locally via FastEmbed for instant semantic underwriting policy retrieval.
4. **Deterministic Offline Fallback**: LangChain agent supports Groq Llama-3.3-70B, Google Gemini, OpenAI GPT-4o, and automatically falls back to an internal deterministic underwriter model so the platform operates 100% offline without requiring paid API keys.
5. **Warm Minimal Fintech UI**: Production-grade institutional credit underwriting dashboard with a clean warm neutral palette, two-column workspace, semicircular risk gauge, and real-time stress testing controls.

---

## 📐 Mathematical & Statistical Formulations

### 1. Weight of Evidence (WoE) & Information Value (IV)
For each continuous feature split into bins $i \in \{1, \dots, k\}$:

$$
\text{Distr Good}_i = \frac{N_{\text{Good}, i}}{N_{\text{Good, Total}}}, \qquad \text{Distr Bad}_i = \frac{N_{\text{Bad}, i}}{N_{\text{Bad, Total}}}
$$

$$
\text{WoE}_i = \ln \left( \frac{\text{Distr Good}_i}{\text{Distr Bad}_i} \right)
$$

$$
\text{IV} = \sum_{i=1}^{k} \left( \text{Distr Good}_i - \text{Distr Bad}_i \right) \times \text{WoE}_i
$$

*Variables with Information Value $\text{IV} < 0.02$ are discarded as unpredictive, while features with $\text{IV} \ge 0.30$ represent strong predictive drivers.*

---

### 2. Points Scaling & Score Conversion (300 to 850)
Translates borrower log-odds into an industry-standard FICO credit score:

$$
\text{Factor} = \frac{\text{PDO}}{\ln(2)}, \qquad \text{Offset} = \text{Base Score} - \text{Factor} \times \ln(\text{Base Odds})
$$

$$
\text{Score} = \text{Offset} + \text{Factor} \times \ln(\text{Odds}) = \text{Base Score} + \sum_{j} \Delta \text{Points}_j
$$

* **Calibration Parameters**: $\text{Base Score} = 600$ at $\text{Base Odds} = 50:1$, with $20$ Points to Double the Odds ($\text{PDO} = 20$).
* **FICO Clipping**: Bounded strictly to $[\text{Min: } 300, \, \text{Max: } 850]$.

---

### 3. Basel III Standardized Expected Loss (EL)
Quantifies anticipated institutional credit losses over a one-year economic horizon:

$$
\text{Expected Loss (EL)} = \text{PD} \times \text{EAD} \times \text{LGD}
$$

* **Probability of Default ($\text{PD}$)**: Statistically mapped from the scorecard rating tier.
* **Exposure at Default ($\text{EAD}$)**: Incorporates the Credit Conversion Factor ($\text{CCF} = 0.20$) for undrawn limits:

$$
\text{EAD} = \text{Current Balance} + \text{CCF} \times \max\left(0, \, \text{Credit Limit} - \text{Current Balance}\right)
$$

* **Loss Given Default ($\text{LGD}$)**: Calibrated to Basel standardized benchmark ($45\%$ for senior unsecured revolving credit facilities).

---

### 4. 1,000-Scenario Monte Carlo Value-at-Risk (VaR)
Simulates correlated credit default shocks across 1,000 macroeconomic states using the Vasicek Single-Factor model:

$$
Y_i = \sqrt{\rho} \, Z + \sqrt{1 - \rho} \, \epsilon_i
$$

Where $Z \sim \mathcal{N}(0, 1)$ is the systemic economic factor, $\epsilon_i \sim \mathcal{N}(0, 1)$ is the idiosyncratic borrower shock, and asset correlation $\rho = 0.15$.

* **Value-at-Risk ($\text{VaR}_{\alpha}$)**: Maximum portfolio loss at confidence level $\alpha$ (evaluated at $\alpha = 0.95$ and $\alpha = 0.99$):

$$
\text{VaR}_{\alpha} = \inf \left[ l \in \mathbb{R} : P(L \le l) \ge \alpha \right]
$$

* **Conditional Value-at-Risk ($\text{CVaR}_{\alpha}$)**: Expected shortfall in the extreme tail beyond $\text{VaR}_{\alpha}$:

$$
\text{CVaR}_{\alpha} = \mathbb{E}\left[ L \mid L \ge \text{VaR}_{\alpha} \right]
$$

---

## 🗂️ Project Directory Structure

```text
CredSure-AI/
├── src/credsure/
│   ├── scorecard/                # Statistical credit scoring engine
│   │   ├── woe_iv.py             # Binning, WoE transformation, and IV filtering
│   │   ├── points_scaling.py     # 300-850 point mapping & calibration
│   │   └── calculator.py         # 23-feature evaluator & score driver attribution
│   ├── portfolio/                # Macro risk & capital adequacy analytics
│   │   ├── expected_loss.py      # Basel II/III Expected Loss (PD * LGD * EAD)
│   │   ├── monte_carlo_var.py    # 1,000-run Monte Carlo VaR (95%/99%) & CVaR
│   │   └── stress_testing.py     # Macro shock simulator (recession, stagflation)
│   ├── rag/                      # Embedded semantic vector store
│   │   ├── vector_store.py       # Local Qdrant disk-persisted policy collection
│   │   └── policy_loader.py      # Credit underwriting policy text chunker
│   ├── analyst/                  # Autonomous credit underwriter agent
│   │   ├── agent.py              # LangChain decision & policy-checking workflow
│   │   ├── memo_generator.py     # Institutional Credit Memorandum builder
│   │   └── config.py             # LLM provider switcher (Groq/Gemini/OpenAI/Mock)
│   └── api/                      # FastAPI REST service
│       ├── app.py                # Endpoints for scoring, portfolio, and memo
│       └── schemas.py            # Pydantic v2 validation contracts
├── frontend/                     # Next.js 14 App Router dashboard
│   ├── src/app/                  # Layout and main dashboard views
│   ├── src/components/           # Reusable UI components
│   │   ├── AppHeader.tsx         # Top bar with status and navigation
│   │   ├── AppSidebar.tsx        # Navigation sidebar
│   │   ├── BorrowerForm.tsx      # Comprehensive credit application input
│   │   ├── ScoreGauge.tsx        # Semicircular credit risk score gauge
│   │   ├── PortfolioCard.tsx     # Basel Expected Loss, Monte Carlo curve, & stress tests
│   │   └── UnderwriterMemo.tsx   # Structured decision card with policy citations
│   └── src/services/api.ts       # Type-safe client for FastAPI endpoints
├── tests/                        # Automated Pytest suite
│   ├── test_scorecard.py         # Validates WoE, IV, and 300-850 point formulas
│   ├── test_portfolio.py         # Validates Expected Loss and Monte Carlo VaR
│   ├── test_qdrant_rag.py        # Tests vector search and policy retrieval
│   └── test_api.py               # Tests all FastAPI endpoints
├── start_dev.bat                 # 1-click Windows startup script
├── start_dev.ps1                 # PowerShell startup script for both services
├── test_all_services.py          # End-to-end full system verification script
├── requirements.txt              # Python server dependencies
├── .env.example                  # Environment configuration template
└── README.md                     # Project documentation
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
* Python 3.11 – 3.13
* Node.js 18+ or 20+

### 2. Fast 1-Click Launch (Windows)
Run the startup script:
```cmd
start_dev.bat
```
Or via PowerShell:
```powershell
.\start_dev.ps1
```

This will automatically launch:
* **FastAPI Backend**: `http://127.0.0.1:8001` (API Docs at `http://127.0.0.1:8001/docs`)
* **Next.js Dashboard**: `http://localhost:3000`

---

## 🛠️ Manual Installation & Execution

### 1. Backend Service
```bash
# Install dependencies
pip install -r requirements.txt

# Launch FastAPI service
python -m uvicorn --app-dir src credsure.api.app:app --host 127.0.0.1 --port 8001 --reload
```

### 2. Frontend Dashboard
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## 🧪 Running Automated Tests

Run the complete backend unit test suite:
```bash
python -m pytest tests/ -v
```

Run the end-to-end full system test (frontend, backend, portfolio, AI memo):
```bash
python test_all_services.py
```

---

## ⚖️ Regulatory Compliance
* **Equal Credit Opportunity Act (ECOA - Regulation B, 12 CFR Part 1002)**: Strict compliance ensuring protected demographic attributes are excluded from all credit scoring models.
* **Fair Credit Reporting Act (FCRA Section 615)**: Automatically produces key score factors and adverse action notices whenever credit is denied or conditionally approved.
* **Basel Committee on Banking Supervision (BCBS)**: EAD and Expected Loss calculations comply with the internal ratings-based (IRB) standardized approach.
