import json
import joblib
import numpy as np
import pandas as pd

from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = ROOT / "models" / "best_credit_model.joblib"
METADATA_PATH = ROOT / "models" / "model_metadata.json"

TEST_PATH = ROOT / "data" / "processed" / "test.csv"

OUTPUT_DIR = ROOT / "results" / "reports"
METRICS_DIR = ROOT / "results" / "metrics"

TARGET = "default"

# Illustrative assumptions.
# Replace these with institution-specific estimates when available.
DEFAULT_LGD = 0.45
DEFAULT_EAD_MULTIPLIER = 1.0

# Illustrative annual discount rate.
ANNUAL_DISCOUNT_RATE = 0.10


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Trained model not found. Run credit_risk.py first."
        )

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            "Model metadata not found."
        )

    model = joblib.load(MODEL_PATH)

    with open(METADATA_PATH, "r") as file:
        metadata = json.load(file)

    feature_names = metadata.get("feature_names")

    if not feature_names:
        feature_names = metadata.get("features")

    if not feature_names:
        feature_names = getattr(model, "feature_names_in_", None)

    if feature_names is None:
        raise ValueError(
            "Feature names are missing from model metadata."
        )

    return model, list(feature_names)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    if not TEST_PATH.exists():
        raise FileNotFoundError(
            "Test dataset not found. Run preprocessing first."
        )

    df = pd.read_csv(TEST_PATH)

    if TARGET not in df.columns:
        raise ValueError("Target column not found in test data.")

    return df


# ============================================================
# PREPARE FEATURES
# ============================================================

def prepare_features(df, feature_names):

    X = df.copy()

    for column in feature_names:
        if column not in X.columns:
            X[column] = np.nan

    X = X[feature_names].copy()

    for column in X.columns:
        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )

    X = X.replace([np.inf, -np.inf], np.nan)

    return X


# ============================================================
# EXPECTED LOSS CALCULATION
# ============================================================

def calculate_expected_loss(
    pd_values,
    ead_values,
    lgd_values
):

    pd_values = np.clip(
        np.asarray(pd_values, dtype=float),
        0,
        1
    )

    ead_values = np.maximum(
        np.asarray(ead_values, dtype=float),
        0
    )

    lgd_values = np.clip(
        np.asarray(lgd_values, dtype=float),
        0,
        1
    )

    ecl = pd_values * lgd_values * ead_values

    return ecl


# ============================================================
# BORROWER-LEVEL ECL
# ============================================================

def generate_borrower_ecl(df, probabilities):

    results = df.copy()

    # The dataset provides credit limit, not actual outstanding
    # exposure at default. Credit limit is therefore used only
    # as an illustrative EAD proxy.
    if "LIMIT_BAL" not in results.columns:
        raise ValueError(
            "LIMIT_BAL column is missing. Cannot create EAD proxy."
        )

    results["PD"] = probabilities

    results["EAD_Illustrative"] = (
        pd.to_numeric(
            results["LIMIT_BAL"],
            errors="coerce"
        ).fillna(0).clip(lower=0)
        * DEFAULT_EAD_MULTIPLIER
    )

    results["LGD_Illustrative"] = DEFAULT_LGD

    results["ECL_Illustrative"] = calculate_expected_loss(
        results["PD"],
        results["EAD_Illustrative"],
        results["LGD_Illustrative"]
    )

    # Discounted ECL for a one-year illustrative horizon.
    results["Discounted_ECL_Illustrative"] = (
        results["ECL_Illustrative"]
        / (1 + ANNUAL_DISCOUNT_RATE)
    )

    return results


# ============================================================
# PORTFOLIO RISK SUMMARY
# ============================================================

def portfolio_summary(results):

    summary = {
        "borrower_count": int(len(results)),
        "average_pd": float(results["PD"].mean()),
        "average_lgd_assumption": float(
            results["LGD_Illustrative"].mean()
        ),
        "total_illustrative_ead": float(
            results["EAD_Illustrative"].sum()
        ),
        "total_illustrative_ecl": float(
            results["ECL_Illustrative"].sum()
        ),
        "total_discounted_illustrative_ecl": float(
            results["Discounted_ECL_Illustrative"].sum()
        ),
        "average_illustrative_ecl_per_borrower": float(
            results["ECL_Illustrative"].mean()
        ),
        "annual_discount_rate_assumption": ANNUAL_DISCOUNT_RATE,
        "lgd_assumption": DEFAULT_LGD,
        "ead_multiplier_assumption": DEFAULT_EAD_MULTIPLIER,
        "methodology_note": (
            "Illustrative ECL. PD is model-estimated; LGD is assumed; "
            "EAD uses credit limit as a proxy. These are not "
            "institution-calibrated accounting provisions."
        )
    }

    return summary


# ============================================================
# RISK SEGMENTATION
# ============================================================

def create_risk_segments(results):

    results["Risk_Category"] = pd.cut(
        results["PD"],
        bins=[-0.001, 0.10, 0.25, 0.50, 1.00],
        labels=[
            "Low Risk",
            "Moderate Risk",
            "High Risk",
            "Very High Risk"
        ]
    )

    segment_summary = (
        results.groupby(
            "Risk_Category",
            observed=False
        )
        .agg(
            Borrower_Count=("PD", "count"),
            Average_PD=("PD", "mean"),
            Total_EAD=("EAD_Illustrative", "sum"),
            Total_ECL=("ECL_Illustrative", "sum")
        )
        .reset_index()
    )

    return results, segment_summary


# ============================================================
# MAIN
# ============================================================

def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("FINAI EXPECTED CREDIT LOSS ANALYSIS")
    print("=" * 60)

    model, feature_names = load_model()

    df = load_data()

    X = prepare_features(df, feature_names)

    print("\nGenerating default probabilities...")

    probabilities = model.predict_proba(X)[:, 1]

    results = generate_borrower_ecl(
        df,
        probabilities
    )

    results, segment_summary = create_risk_segments(
        results
    )

    # Save borrower-level ECL results.
    borrower_path = OUTPUT_DIR / "borrower_expected_loss.csv"

    results.to_csv(
        borrower_path,
        index=False
    )

    # Save risk segment analysis.
    segment_path = OUTPUT_DIR / "risk_segment_analysis.csv"

    segment_summary.to_csv(
        segment_path,
        index=False
    )

    # Portfolio-level summary.
    summary = portfolio_summary(results)

    with open(
        METRICS_DIR / "expected_loss_summary.json",
        "w"
    ) as file:
        json.dump(summary, file, indent=4)

    print("\nPORTFOLIO RISK SUMMARY")
    print("-" * 60)

    for key, value in summary.items():
        if isinstance(value, float):
            print(f"{key}: {value:,.4f}")
        else:
            print(f"{key}: {value}")

    print("\nRISK SEGMENT SUMMARY")
    print("-" * 60)

    print(segment_summary.to_string(index=False))

    print("\nGenerated files:")
    print("1. results/reports/borrower_expected_loss.csv")
    print("2. results/reports/risk_segment_analysis.csv")
    print("3. results/metrics/expected_loss_summary.json")

    print("\nExpected loss analysis completed successfully.")


if __name__ == "__main__":
    main()