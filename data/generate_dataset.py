"""Generates synthetic baseline UCI credit card dataset (30,000 records)

and a fast representative sample for instant portfolio risk testing.
"""

import os
import json
import numpy as np
import pandas as pd


def generate_credit_dataset(n_samples: int = 5000, seed: int = 42):
    rng = np.random.default_rng(seed)

    # 1. Demographics
    sex = rng.choice([1, 2], size=n_samples, p=[0.40, 0.60])
    education = rng.choice([1, 2, 3, 4], size=n_samples, p=[0.35, 0.47, 0.16, 0.02])
    marriage = rng.choice([1, 2, 3], size=n_samples, p=[0.45, 0.53, 0.02])
    age = np.clip(rng.normal(35, 9, size=n_samples).astype(int), 21, 75)

    # 2. Limit Balance (skewed distribution)
    raw_limits = rng.lognormal(mean=11.5, sigma=0.8, size=n_samples)
    limits = np.round(np.clip(raw_limits, 10000, 800000) / 10000) * 10000

    # 3. Latent creditworthiness factor (-3 to 3, higher = better credit)
    latent_score = (
        0.3 * (age - 35) / 10
        + 0.4 * (limits - 150000) / 100000
        + 0.2 * (education == 1).astype(float)
        + rng.normal(0, 1.0, size=n_samples)
    )

    # Repayment status PAY_0 to PAY_6
    # -1: pay duly, 0: revolving, 1: 1 mo delay, 2: 2 mo delay, etc.
    pay_status = []
    for i in range(6):
        # Noise added per month
        latent_m = latent_score + rng.normal(0, 0.6, size=n_samples)
        p = np.where(
            latent_m > 1.2,
            rng.choice([-1, 0], size=n_samples, p=[0.7, 0.3]),
            np.where(
                latent_m > 0.0,
                rng.choice([-1, 0, 1], size=n_samples, p=[0.4, 0.5, 0.1]),
                np.where(
                    latent_m > -1.2,
                    rng.choice([0, 1, 2], size=n_samples, p=[0.3, 0.4, 0.3]),
                    rng.choice([1, 2, 3, 4], size=n_samples, p=[0.1, 0.4, 0.3, 0.2]),
                ),
            ),
        )
        pay_status.append(p)

    pay_0, pay_2, pay_3, pay_4, pay_5, pay_6 = pay_status

    # 4. Bill Amounts and Payments
    bills = []
    payments = []
    base_utilization = np.clip(rng.beta(2, 5, size=n_samples) * (1.5 - 0.2 * latent_score), 0.02, 1.05)

    for i in range(6):
        monthly_bill = np.round(limits * base_utilization * rng.uniform(0.7, 1.2, size=n_samples))
        bills.append(monthly_bill)
        # Payment amount: good payers pay almost full bill, troubled payers pay minimum or 0
        pay_ratio = np.where(latent_score > 0.5, rng.uniform(0.6, 1.0, size=n_samples), rng.uniform(0.0, 0.4, size=n_samples))
        monthly_pay = np.round(monthly_bill * pay_ratio)
        payments.append(monthly_pay)

    # 5. Default probability and target (22% baseline default rate as in UCI benchmark)
    log_odds = -1.5 - 0.8 * latent_score + 0.6 * np.maximum(pay_0, 0) + 0.4 * np.maximum(pay_2, 0)
    p_default = 1.0 / (1.0 + np.exp(-log_odds))
    default_target = (rng.uniform(0, 1, size=n_samples) < p_default).astype(int)

    data = {
        "ID": np.arange(1, n_samples + 1),
        "LIMIT_BAL": limits,
        "SEX": sex,
        "EDUCATION": education,
        "MARRIAGE": marriage,
        "AGE": age,
        "PAY_0": pay_0,
        "PAY_2": pay_2,
        "PAY_3": pay_3,
        "PAY_4": pay_4,
        "PAY_5": pay_5,
        "PAY_6": pay_6,
        "BILL_AMT1": bills[0],
        "BILL_AMT2": bills[1],
        "BILL_AMT3": bills[2],
        "BILL_AMT4": bills[3],
        "BILL_AMT5": bills[4],
        "BILL_AMT6": bills[5],
        "PAY_AMT1": payments[0],
        "PAY_AMT2": payments[1],
        "PAY_AMT3": payments[2],
        "PAY_AMT4": payments[3],
        "PAY_AMT5": payments[4],
        "PAY_AMT6": payments[5],
        "default": default_target,
    }

    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    print("Generating representative UCI credit dataset (5,000 baseline records)...")
    df = generate_credit_dataset(5000)
    csv_path = "data/raw/credit_card_clients.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved baseline dataset to {csv_path} (Shape: {df.shape})")

    # Sample top 1,000 for ultra-fast real-time portfolio simulations
    sample_records = df.head(1000).to_dict(orient="records")
    json_path = "data/processed/sample_portfolio.json"
    with open(json_path, "w") as f:
        json.dump(sample_records, f)
    print(f"Saved processed portfolio sample to {json_path}")
