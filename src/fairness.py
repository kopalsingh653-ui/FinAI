import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = ROOT / "models" / "best_credit_model.joblib"
METADATA_PATH = ROOT / "models" / "model_metadata.json"

TEST_PATH = ROOT / "data" / "processed" / "test.csv"
THRESHOLD_PATH = ROOT / "results" / "metrics" / "selected_threshold.json"

REPORTS_DIR = ROOT / "results" / "reports"
METRICS_DIR = ROOT / "results" / "metrics"

TARGET = "default"
GROUP_COLUMN = "SEX"

# UCI dataset encoding:
# 1 = Male, 2 = Female
GROUP_LABELS = {
    1: "Male",
    2: "Female"
}


# ============================================================
# DIRECTORY SETUP
# ============================================================

def create_directories():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD MODEL AND METADATA
# ============================================================

def load_model():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Trained model not found. Run python -m src.credit_risk first."
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
# LOAD TEST DATA
# ============================================================

def load_test_data():

    if not TEST_PATH.exists():
        raise FileNotFoundError(
            "Test dataset not found. Run preprocessing first."
        )

    df = pd.read_csv(TEST_PATH)

    required_columns = [TARGET, GROUP_COLUMN]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"Required column '{column}' is missing."
            )

    df[TARGET] = pd.to_numeric(
        df[TARGET],
        errors="coerce"
    )

    df[GROUP_COLUMN] = pd.to_numeric(
        df[GROUP_COLUMN],
        errors="coerce"
    )

    if df[TARGET].isna().any():
        raise ValueError("Invalid target values found.")

    if df[GROUP_COLUMN].isna().any():
        raise ValueError("Missing demographic group values found.")

    if not set(df[TARGET].unique()).issubset({0, 1}):
        raise ValueError("Target must contain only 0 and 1.")

    return df


# ============================================================
# LOAD SELECTED THRESHOLD
# ============================================================

def load_threshold():

    if not THRESHOLD_PATH.exists():
        print(
            "Threshold file not found. Using default threshold 0.50."
        )
        return 0.50

    with open(THRESHOLD_PATH, "r") as file:
        threshold_data = json.load(file)

    return float(
        threshold_data.get("selected_threshold", 0.50)
    )


# ============================================================
# PREPARE MODEL FEATURES
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
# GROUP-LEVEL METRICS
# ============================================================

def calculate_group_metrics(
    group_df,
    probabilities,
    threshold
):

    y_true = group_df[TARGET].astype(int).to_numpy()

    y_pred = (
        probabilities >= threshold
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1]
    ).ravel()

    total = len(y_true)

    selection_rate = float(y_pred.mean())

    tpr = tp / (tp + fn) if (tp + fn) > 0 else np.nan

    fpr = fp / (fp + tn) if (fp + tn) > 0 else np.nan

    metrics = {
        "sample_count": int(total),
        "actual_default_rate": float(y_true.mean()),
        "predicted_default_rate": selection_rate,
        "accuracy": float(
            accuracy_score(y_true, y_pred)
        ),
        "precision": float(
            precision_score(
                y_true,
                y_pred,
                zero_division=0
            )
        ),
        "recall_tpr": float(tpr),
        "false_positive_rate": float(fpr),
        "f1_score": float(
            f1_score(
                y_true,
                y_pred,
                zero_division=0
            )
        ),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn)
    }

    return metrics


# ============================================================
# FAIRNESS COMPARISON
# ============================================================

def calculate_fairness_differences(group_metrics):

    if len(group_metrics) < 2:
        raise ValueError(
            "At least two demographic groups are required."
        )

    groups = list(group_metrics.keys())

    reference = groups[0]
    comparison = groups[1]

    ref = group_metrics[reference]
    comp = group_metrics[comparison]

    def difference(metric):

        a = ref[metric]
        b = comp[metric]

        if pd.isna(a) or pd.isna(b):
            return None

        return float(b - a)

    def ratio(metric):

        a = ref[metric]
        b = comp[metric]

        if pd.isna(a) or pd.isna(b) or a == 0:
            return None

        return float(b / a)

    return {
        "reference_group": reference,
        "comparison_group": comparison,

        # Difference in predicted default rates.
        "demographic_parity_difference": difference(
            "predicted_default_rate"
        ),

        # Difference in true positive rates.
        # In this project, a positive case means actual default.
        "equal_opportunity_difference": difference(
            "recall_tpr"
        ),

        # Difference in false positive rates.
        "false_positive_rate_difference": difference(
            "false_positive_rate"
        ),

        # Ratio of predicted default rates.
        "predicted_default_rate_ratio": ratio(
            "predicted_default_rate"
        ),

        "accuracy_difference": difference("accuracy")
    }


# ============================================================
# MAIN FAIRNESS AUDIT
# ============================================================

def main():

    create_directories()

    print("=" * 60)
    print("FINAI FAIRNESS AUDIT")
    print("=" * 60)

    model, feature_names = load_model()

    df = load_test_data()

    threshold = load_threshold()

    X_test = prepare_features(
        df,
        feature_names
    )

    y_test = df[TARGET].astype(int)

    # Generate predictions using the saved model.
    probabilities = model.predict_proba(X_test)[:, 1]

    df = df.copy()
    df["predicted_probability"] = probabilities

    print("\nUsing threshold:", threshold)
    print("Test records:", len(df))

    # --------------------------------------------------------
    # GROUP ANALYSIS
    # --------------------------------------------------------

    group_metrics = {}

    for group_value, group_name in GROUP_LABELS.items():

        group_df = df[
            df[GROUP_COLUMN] == group_value
        ].copy()

        if group_df.empty:
            print(
                f"\nSkipping {group_name}: no records available."
            )
            continue

        group_probabilities = (
            group_df["predicted_probability"].to_numpy()
        )

        metrics = calculate_group_metrics(
            group_df,
            group_probabilities,
            threshold
        )

        group_metrics[group_name] = metrics

        print("\n" + "-" * 60)
        print(f"{group_name.upper()} GROUP")
        print("-" * 60)

        for key, value in metrics.items():

            if isinstance(value, float):
                print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")

    if len(group_metrics) < 2:
        raise ValueError(
            "Could not compare both demographic groups."
        )

    # --------------------------------------------------------
    # FAIRNESS DIFFERENCES
    # --------------------------------------------------------

    fairness_differences = calculate_fairness_differences(
        group_metrics
    )

    print("\n" + "=" * 60)
    print("FAIRNESS COMPARISON")
    print("=" * 60)

    for key, value in fairness_differences.items():

        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")

    # --------------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------------

    group_df = pd.DataFrame.from_dict(
        group_metrics,
        orient="index"
    )

    group_df.index.name = "Demographic_Group"

    group_df.to_csv(
        REPORTS_DIR / "fairness_group_metrics.csv"
    )

    fairness_df = pd.DataFrame([
        fairness_differences
    ])

    fairness_df.to_csv(
        METRICS_DIR / "fairness_comparison.csv",
        index=False
    )

    output = {
        "audit_dataset": "Held-out test dataset",
        "protected_attribute": GROUP_COLUMN,
        "threshold": threshold,
        "group_metrics": group_metrics,
        "fairness_differences": fairness_differences,
        "interpretation_note": (
            "These are descriptive group-level diagnostics. "
            "They do not establish legal compliance or prove "
            "the absence of discrimination. Results may be "
            "affected by sample composition, historical labels "
            "and proxy variables."
        )
    }

    with open(
        REPORTS_DIR / "fairness_audit.json",
        "w"
    ) as file:
        json.dump(output, file, indent=4)

    print("\nGenerated files:")
    print("1. results/reports/fairness_group_metrics.csv")
    print("2. results/metrics/fairness_comparison.csv")
    print("3. results/reports/fairness_audit.json")

    print("\nFairness audit completed successfully.")


if __name__ == "__main__":
    main()