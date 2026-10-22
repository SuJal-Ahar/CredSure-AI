import urllib.request
import json
import sys

BASE_BACKEND = "http://127.0.0.1:8001"
BASE_FRONTEND = "http://localhost:3000"

results = []

def record(name, passed, details=""):
    results.append({"name": name, "passed": passed, "details": details})
    tag = "[PASS]" if passed else "[FAIL]"
    print(f"{tag:7} | {name:<32} | {details}")

print("=" * 75)
print("             CREDFORSURE COMPREHENSIVE END-TO-END TEST SUITE              ")
print("=" * 75)

# 1. Frontend Web App (Next.js)
try:
    with urllib.request.urlopen(BASE_FRONTEND, timeout=10) as r:
        code = r.getcode()
        html = r.read().decode('utf-8', errors='ignore')
        if code == 200 and len(html) > 5000:
            record("Frontend Web App (Next.js)", True, f"HTTP {code}, {len(html):,} bytes rendered")
        else:
            record("Frontend Web App (Next.js)", False, f"Code {code}, length {len(html)}")
except Exception as e:
    record("Frontend Web App (Next.js)", False, str(e))

# 2. Backend Health & Qdrant Vector Database
try:
    with urllib.request.urlopen(f"{BASE_BACKEND}/health", timeout=10) as r:
        data = json.loads(r.read())
        if data.get("status") == "healthy":
            record("Backend Health & Vector DB", True, f"Status: {data.get('status')} | Policies: {data.get('policies_indexed')} | Portfolio: {data.get('portfolio_records_loaded')}")
        else:
            record("Backend Health & Vector DB", False, f"Status: {data.get('status')}")
except Exception as e:
    record("Backend Health & Vector DB", False, str(e))

# 3. Borrower Presets API
presets_data = []
try:
    with urllib.request.urlopen(f"{BASE_BACKEND}/scorecard/presets", timeout=10) as r:
        resp = json.loads(r.read())
        presets_data = resp.get("presets", [])
        if len(presets_data) >= 3:
            names = [p.get("name") for p in presets_data]
            record("Borrower Presets API", True, f"{len(presets_data)} profiles ready ({', '.join(names)})")
        else:
            record("Borrower Presets API", False, f"Only found {len(presets_data)} presets")
except Exception as e:
    record("Borrower Presets API", False, str(e))

# 4. Scorecard Prediction Engine (WOE & FICO Points Scaling)
scorecard_res = None
if presets_data:
    sample_borrower = presets_data[0]["features"]
    try:
        req = urllib.request.Request(
            f"{BASE_BACKEND}/scorecard/score",
            data=json.dumps(sample_borrower).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            scorecard_res = json.loads(r.read())
            score = scorecard_res.get("score")
            dec = scorecard_res.get("decision")
            tier = scorecard_res.get("risk_category")
            factors = len(scorecard_res.get("feature_contributions", []))
            record("Scorecard Engine (WOE + Points)", True, f"Score: {score} | Decision: {dec} | Tier: {tier} | Factors: {factors}")
    except Exception as e:
        record("Scorecard Engine (WOE + Points)", False, str(e))
else:
    record("Scorecard Engine (WOE + Points)", False, "Presets not available")

# 5. Portfolio Basel Expected Loss (PD * LGD * EAD) & Monte Carlo VaR
try:
    with urllib.request.urlopen(f"{BASE_BACKEND}/portfolio/metrics", timeout=10) as r:
        port_res = json.loads(r.read())
        ead = port_res.get("total_ead", 0)
        el = port_res.get("total_expected_loss", 0)
        var95 = port_res.get("var_95", 0)
        records_count = port_res.get("total_records", 0)
        record("Basel Portfolio & Monte Carlo", True, f"{records_count} loans | EAD: ${ead:,.0f} | EL: ${el:,.0f} | VaR(95): ${var95:,.0f}")
except Exception as e:
    record("Basel Portfolio & Monte Carlo", False, str(e))

# 6. Macroeconomic Stress Testing Engine
try:
    stress_payload = {
        "scenario_name": "RECESSION_SEVERE",
        "delay_shift": 2,
        "balance_shock_pct": 25.0,
        "pd_multiplier": 2.2,
        "stressed_lgd": 0.60
    }
    req = urllib.request.Request(
        f"{BASE_BACKEND}/portfolio/stress-test",
        data=json.dumps(stress_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        stress_res = json.loads(r.read())
        delta = stress_res.get("impact", {}).get("delta_expected_loss", 0)
        status = stress_res.get("impact", {}).get("capital_strain_status", "")
        record("Macro Stress Testing Simulation", True, f"Delta Loss: +${delta:,.0f} | Capital Strain: {status}")
except Exception as e:
    record("Macro Stress Testing Simulation", False, str(e))

# 7. Qdrant Embedded Vector Policy Retrieval
try:
    with urllib.request.urlopen(f"{BASE_BACKEND}/policies/rules?query=delinquency+tolerance", timeout=10) as r:
        policy_res = json.loads(r.read())
        citations = len(policy_res.get("results", []))
        record("Qdrant Semantic Policy RAG", True, f"{citations} policy citations matched for query")
except Exception as e:
    record("Qdrant Semantic Policy RAG", False, str(e))

# 8. AI Credit Underwriter Memo Generator
if presets_data:
    try:
        memo_payload = {
            "applicant_name": "Rajesh Kumar (Enterprise Test)",
            "features": presets_data[0]["features"]
        }
        req = urllib.request.Request(
            f"{BASE_BACKEND}/analyst/memo",
            data=json.dumps(memo_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            memo_res = json.loads(r.read())
            dec = memo_res.get("decision")
            officer = memo_res.get("underwriter_name")
            text_len = len(memo_res.get("memo_markdown", ""))
            record("AI Underwriter Loan Memo", True, f"Decision: {dec} | Officer: {officer} | Memo: {text_len} chars")
    except Exception as e:
        record("AI Underwriter Loan Memo", False, str(e))

print("=" * 75)
passed_count = sum(1 for r in results if r["passed"])
failed_count = sum(1 for r in results if not r["passed"])
print(f"SUMMARY: {passed_count}/{len(results)} COMPONENTS OPERATIONAL ({failed_count} failures)")
print("=" * 75)

sys.exit(0 if failed_count == 0 else 1)
