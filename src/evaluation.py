import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report,
    roc_curve,
    precision_recall_curve
)

warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = ROOT / "models" / "best_credit_model.joblib"
METADATA_PATH = ROOT / "models" / "model_metadata.json"

VALIDATION_PATH = ROOT / "data" / "processed" / "validation.csv"
TEST_PATH = ROOT / "data" / "processed" / "test.csv"

METRICS_DIR = ROOT / "results" / "metrics"
PLOTS_DIR = ROOT / "results" / "plots"
REPORTS_DIR = ROOT / "results" / "reports"

TARGET = "default"

# Minimum recall constraint for validation threshold selection.
# This helps avoid choosing a threshold that misses too many defaults.
MIN_VALIDATION_RECALL = 0.50

DEFAULT_THRESHOLD = 0.50


# ============================================================
# DIRECTORY SETUP
# ============================================================

def create_directories():
    for directory in [METRICS_DIR, PLOTS_DIR, REPORTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD MODEL AND METADATA
# ============================================================

def load_model_and_metadata():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}\n"
            "Run python -m src.credit_risk first."
        )

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Model metadata not found: {METADATA_PATH}"
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
            "Could not identify model feature names. "
            "Check model_metadata.json."
        )

    return model, metadata, list(feature_names)


# ============================================================
# LOAD DATA
# ============================================================

def load_dataset(path):

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}\n"
            "Run preprocessing and feature engineering first."
        )

    df = pd.read_csv(path)

    if TARGET not in df.columns:
        raise ValueError(
            f"Target column '{TARGET}' not found in {path.name}"
        )

    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")

    if df[TARGET].isna().any():
        raise ValueError(
            f"Missing or invalid target values in {path.name}"
        )

    if not set(df[TARGET].unique()).issubset({0, 1}):
        raise ValueError(
            f"Target in {path.name} must contain only 0 and 1."
        )

    return df


# ============================================================
# PREPARE MODEL INPUT
# ============================================================

def prepare_features(df, feature_names):

    X = df.copy()

    # Keep only the features used during model training.
    # Add missing columns as NaN so the pipeline imputer can handle them.
    for column in feature_names:
        if column not in X.columns:
            X[column] = np.nan

    X = X[feature_names].copy()

    for column in X.columns:
        X[column] = pd.to_numeric(X[column], errors="coerce")

    X = X.replace([np.inf, -np.inf], np.nan)

    return X


# ============================================================
# METRIC CALCULATION
# ============================================================

def calculate_metrics(y_true, probabilities, threshold):

    predictions = (probabilities >= threshold).astype(int)

    metrics = {
        "threshold": float(threshold),
        "accuracy": float(
            accuracy_score(y_true, predictions)
        ),
        "precision": float(
            precision_score(y_true, predictions, zero_division=0)
        ),
        "recall": float(
            recall_score(y_true, predictions, zero_division=0)
        ),
        "f1_score": float(
            f1_score(y_true, predictions, zero_division=0)
        ),
        "roc_auc": float(
            roc_auc_score(y_true, probabilities)
        ),
        "pr_auc": float(
            average_precision_score(y_true, probabilities)
        )
    }

    return metrics, predictions


# ============================================================
# VALIDATION THRESHOLD OPTIMISATION
# ============================================================

def optimise_threshold(y_true, probabilities):

    thresholds = np.arange(0.10, 0.91, 0.01)

    best_threshold = DEFAULT_THRESHOLD
    best_f1 = -1

    threshold_results = []

    for threshold in thresholds:

        predictions = (probabilities >= threshold).astype(int)

        precision = precision_score(
            y_true, predictions, zero_division=0
        )

        recall = recall_score(
            y_true, predictions, zero_division=0
        )

        f1 = f1_score(
            y_true, predictions, zero_division=0
        )

        accuracy = accuracy_score(y_true, predictions)

        threshold_results.append({
            "threshold": float(threshold),
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1)
        })

        # Select the best F1 threshold while respecting
        # the minimum validation recall constraint.
        if recall >= MIN_VALIDATION_RECALL and f1 > best_f1:
            best_f1 = f1
            best_threshold = float(threshold)

    # If no threshold satisfies the recall constraint,
    # fall back to the threshold with the highest F1.
    if best_f1 < 0:

        best_result = max(
            threshold_results,
            key=lambda item: item["f1_score"]
        )

        best_threshold = best_result["threshold"]

        print(
            "\nWARNING: No threshold met the minimum recall "
            "constraint. Using the threshold with the highest F1."
        )

    threshold_df = pd.DataFrame(threshold_results)

    threshold_df.to_csv(
        METRICS_DIR / "threshold_analysis.csv",
        index=False
    )

    print("\nSelected validation threshold:", best_threshold)

    return best_threshold


# ============================================================
# CONFUSION MATRIX
# ============================================================

def save_confusion_matrix(y_true, predictions, filename, title):

    cm = confusion_matrix(y_true, predictions)

    plt.figure(figsize=(7, 5))

    plt.imshow(cm, interpolation="nearest")
    plt.title(title)
    plt.colorbar()

    plt.xticks([0, 1], ["Non-default", "Default"])
    plt.yticks([0, 1], ["Non-default", "Default"])

    plt.xlabel("Predicted")
    plt.ylabel("Actual")

    for i in range(2):
        for j in range(2):
            plt.text(
                j,
                i,
                str(cm[i, j]),
                ha="center",
                va="center",
                fontsize=12
            )

    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


# ============================================================
# ROC CURVE
# ============================================================

def save_roc_curve(y_true, probabilities):

    fpr, tpr, _ = roc_curve(y_true, probabilities)

    auc_value = roc_auc_score(y_true, probabilities)

    plt.figure(figsize=(7, 5))

    plt.plot(
        fpr,
        tpr,
        label=f"ROC-AUC = {auc_value:.4f}"
    )

    plt.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        label="Random Classifier"
    )

    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve - Final Test Set")

    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "test_roc_curve.png",
        dpi=300
    )

    plt.close()


# ============================================================
# PRECISION-RECALL CURVE
# ============================================================

def save_precision_recall_curve(y_true, probabilities):

    precision, recall, _ = precision_recall_curve(
        y_true,
        probabilities
    )

    ap = average_precision_score(y_true, probabilities)

    plt.figure(figsize=(7, 5))

    plt.plot(
        recall,
        precision,
        label=f"PR-AUC = {ap:.4f}"
    )

    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve - Final Test Set")

    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "test_precision_recall_curve.png",
        dpi=300
    )

    plt.close()


# ============================================================
# SAVE CLASSIFICATION REPORT
# ============================================================

def save_classification_report(y_true, predictions):

    report = classification_report(
        y_true,
        predictions,
        target_names=["Non-default", "Default"],
        zero_division=0
    )

    report_path = REPORTS_DIR / "classification_report.txt"

    with open(report_path, "w") as file:
        file.write("FINAI CLASSIFICATION REPORT\n")
        file.write("=" * 50 + "\n\n")
        file.write(report)

    print("\nClassification Report:")
    print(report)


# ============================================================
# MAIN EVALUATION
# ============================================================

def main():

    create_directories()

    print("=" * 60)
    print("FINAI MODEL EVALUATION")
    print("=" * 60)

    # Load selected model.
    model, metadata, feature_names = load_model_and_metadata()

    print("\nSelected model:", metadata.get("best_model", "Saved model"))
    print("Number of features:", len(feature_names))

    # Load validation and test datasets.
    validation_df = load_dataset(VALIDATION_PATH)
    test_df = load_dataset(TEST_PATH)

    X_val = prepare_features(validation_df, feature_names)
    y_val = validation_df[TARGET].astype(int)

    X_test = prepare_features(test_df, feature_names)
    y_test = test_df[TARGET].astype(int)

    # --------------------------------------------------------
    # VALIDATION PREDICTIONS
    # --------------------------------------------------------

    print("\nGenerating validation predictions...")

    val_probabilities = model.predict_proba(X_val)[:, 1]

    # Compare standard threshold and optimised threshold.
    default_metrics, _ = calculate_metrics(
        y_val,
        val_probabilities,
        DEFAULT_THRESHOLD
    )

    selected_threshold = optimise_threshold(
        y_val,
        val_probabilities
    )

    optimised_metrics, _ = calculate_metrics(
        y_val,
        val_probabilities,
        selected_threshold
    )

    validation_comparison = pd.DataFrame([
        {"model_threshold": "Default 0.50", **default_metrics},
        {"model_threshold": "Optimised", **optimised_metrics}
    ])

    validation_comparison.to_csv(
        METRICS_DIR / "validation_threshold_comparison.csv",
        index=False
    )

    print("\nVALIDATION RESULTS")
    print("-" * 60)
    print(validation_comparison.to_string(index=False))

    # Save selected threshold.
    threshold_data = {
        "default_threshold": DEFAULT_THRESHOLD,
        "selected_threshold": selected_threshold,
        "minimum_validation_recall": MIN_VALIDATION_RECALL,
        "selection_method": (
            "Maximum validation F1 subject to minimum recall constraint"
        )
    }

    with open(
        METRICS_DIR / "selected_threshold.json",
        "w"
    ) as file:
        json.dump(threshold_data, file, indent=4)

    # --------------------------------------------------------
    # FINAL TEST EVALUATION
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL TEST SET EVALUATION")
    print("=" * 60)

    print("\nGenerating test predictions...")

    test_probabilities = model.predict_proba(X_test)[:, 1]

    # Evaluate standard threshold.
    test_default_metrics, test_default_predictions = calculate_metrics(
        y_test,
        test_probabilities,
        DEFAULT_THRESHOLD
    )

    # Evaluate threshold selected using validation data.
    test_optimised_metrics, test_optimised_predictions = calculate_metrics(
        y_test,
        test_probabilities,
        selected_threshold
    )

    print("\nTEST RESULTS - DEFAULT THRESHOLD (0.50)")
    print("-" * 60)

    for key, value in test_default_metrics.items():
        print(f"{key}: {value:.4f}")

    print("\nTEST RESULTS - VALIDATION-OPTIMISED THRESHOLD")
    print("-" * 60)

    for key, value in test_optimised_metrics.items():
        print(f"{key}: {value:.4f}")

    # Save test metrics.
    test_comparison = pd.DataFrame([
        {
            "model_threshold": "Default 0.50",
            **test_default_metrics
        },
        {
            "model_threshold": "Validation Optimised",
            **test_optimised_metrics
        }
    ])

    test_comparison.to_csv(
        METRICS_DIR / "final_test_metrics.csv",
        index=False
    )

    # Save detailed test metrics as JSON.
    with open(
        METRICS_DIR / "final_test_metrics.json",
        "w"
    ) as file:
        json.dump({
            "default_threshold": test_default_metrics,
            "optimised_threshold": test_optimised_metrics
        }, file, indent=4)

    # --------------------------------------------------------
    # PLOTS AND REPORTS
    # --------------------------------------------------------

    save_confusion_matrix(
        y_test,
        test_optimised_predictions,
        "test_confusion_matrix.png",
        "Confusion Matrix - Optimised Threshold"
    )

    save_roc_curve(y_test, test_probabilities)

    save_precision_recall_curve(y_test, test_probabilities)

    save_classification_report(
        y_test,
        test_optimised_predictions
    )

    print("\n" + "=" * 60)
    print("EVALUATION COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print("\nGenerated files:")

    print("1. results/metrics/validation_threshold_comparison.csv")
    print("2. results/metrics/threshold_analysis.csv")
    print("3. results/metrics/selected_threshold.json")
    print("4. results/metrics/final_test_metrics.csv")
    print("5. results/metrics/final_test_metrics.json")
    print("6. results/plots/test_confusion_matrix.png")
    print("7. results/plots/test_roc_curve.png")
    print("8. results/plots/test_precision_recall_curve.png")
    print("9. results/reports/classification_report.txt")


if __name__ == "__main__":
    main()