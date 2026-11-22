import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap

warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = ROOT / "models" / "best_credit_model.joblib"
METADATA_PATH = ROOT / "models" / "model_metadata.json"

TRAIN_PATH = ROOT / "data" / "processed" / "train.csv"
TEST_PATH = ROOT / "data" / "processed" / "test.csv"

PLOTS_DIR = ROOT / "results" / "plots"
REPORTS_DIR = ROOT / "results" / "reports"

TARGET = "default"

BACKGROUND_SIZE = 100
EXPLANATION_SIZE = 100
RANDOM_STATE = 42


# ============================================================
# DIRECTORY SETUP
# ============================================================

def create_directories():

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD MODEL AND FEATURES
# ============================================================

def load_model():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Trained model not found. Run credit_risk.py first."
        )

    model = joblib.load(MODEL_PATH)

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            "Model metadata not found."
        )

    with open(METADATA_PATH, "r") as file:
        metadata = json.load(file)

    feature_names = metadata.get("feature_names")

    if not feature_names:
        feature_names = metadata.get("features")

    if not feature_names:
        feature_names = getattr(model, "feature_names_in_", None)

    if feature_names is None:
        raise ValueError(
            "Feature names could not be recovered from metadata."
        )

    return model, list(feature_names)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    if not TRAIN_PATH.exists() or not TEST_PATH.exists():
        raise FileNotFoundError(
            "Train or test dataset missing. Run preprocessing first."
        )

    train_df = pd.read_csv(TRAIN_PATH)
    test_df = pd.read_csv(TEST_PATH)

    return train_df, test_df


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
# SAMPLE DATA
# ============================================================

def sample_data(X, size):

    return X.sample(
        n=min(size, len(X)),
        random_state=RANDOM_STATE
    ).copy()


# ============================================================
# SHAP EXPLANATION
# ============================================================

def explain_model(model, X_background, X_explain):

    print("\nCreating SHAP explainer...")

    # KernelExplainer works with general prediction functions,
    # including sklearn pipelines containing preprocessing.
    def prediction_function(data):

        if isinstance(data, pd.DataFrame):
            input_df = data.copy()
        else:
            input_df = pd.DataFrame(
                data,
                columns=X_background.columns
            )

        probabilities = model.predict_proba(input_df)[:, 1]

        return probabilities

    background = shap.sample(
        X_background,
        min(50, len(X_background)),
        random_state=RANDOM_STATE
    )

    explainer = shap.KernelExplainer(
        prediction_function,
        background
    )

    print("Calculating SHAP values...")

    shap_values = explainer.shap_values(
        X_explain,
        nsamples=100
    )

    # Handle different SHAP output formats.
    if isinstance(shap_values, list):
        shap_values = shap_values[-1]

    shap_values = np.asarray(shap_values)

    # Some SHAP versions return an extra output dimension.
    if shap_values.ndim == 3:
        shap_values = shap_values[:, :, -1]

    if shap_values.ndim != 2:
        raise ValueError(
            f"Unexpected SHAP output shape: {shap_values.shape}"
        )

    return shap_values


# ============================================================
# GLOBAL FEATURE IMPORTANCE
# ============================================================

def calculate_global_importance(shap_values, X_explain):

    importance = np.abs(shap_values).mean(axis=0)

    importance_df = pd.DataFrame({
        "Feature": X_explain.columns,
        "Mean_Absolute_SHAP": importance
    })

    importance_df = importance_df.sort_values(
        "Mean_Absolute_SHAP",
        ascending=False
    )

    importance_df.to_csv(
        REPORTS_DIR / "shap_feature_importance.csv",
        index=False
    )

    return importance_df


# ============================================================
# GLOBAL IMPORTANCE PLOT
# ============================================================

def plot_global_importance(importance_df):

    top_features = importance_df.head(15).sort_values(
        "Mean_Absolute_SHAP"
    )

    plt.figure(figsize=(10, 7))

    plt.barh(
        top_features["Feature"],
        top_features["Mean_Absolute_SHAP"]
    )

    plt.xlabel("Mean Absolute SHAP Value")
    plt.ylabel("Feature")
    plt.title("Top 15 Features Influencing Credit Default Risk")

    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "shap_global_importance.png",
        dpi=300
    )

    plt.close()


# ============================================================
# SHAP SUMMARY PLOT
# ============================================================

def plot_shap_summary(shap_values, X_explain):

    plt.figure(figsize=(11, 7))

    shap.summary_plot(
        shap_values,
        X_explain,
        show=False,
        max_display=15
    )

    plt.title("SHAP Summary - Credit Risk Model")
    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "shap_summary.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


# ============================================================
# INDIVIDUAL BORROWER EXPLANATIONS
# ============================================================

def generate_individual_explanations(
    model,
    shap_values,
    X_explain
):

    probabilities = model.predict_proba(X_explain)[:, 1]

    individual_results = []

    for index in range(len(X_explain)):

        row_shap = shap_values[index]

        top_indices = np.argsort(
            np.abs(row_shap)
        )[::-1][:5]

        explanation = []

        for feature_index in top_indices:

            feature = X_explain.columns[feature_index]

            explanation.append({
                "feature": feature,
                "feature_value": float(
                    X_explain.iloc[index, feature_index]
                ) if pd.notna(
                    X_explain.iloc[index, feature_index]
                ) else None,
                "shap_value": float(
                    row_shap[feature_index]
                ),
                "impact": (
                    "Increases predicted default probability"
                    if row_shap[feature_index] > 0
                    else "Decreases predicted default probability"
                )
            })

        individual_results.append({
            "borrower_sample": index + 1,
            "predicted_default_probability": float(
                probabilities[index]
            ),
            "top_feature_explanations": explanation
        })

    with open(
        REPORTS_DIR / "individual_shap_explanations.json",
        "w"
    ) as file:
        json.dump(
            individual_results,
            file,
            indent=4
        )

    return individual_results


# ============================================================
# MAIN
# ============================================================

def main():

    create_directories()

    print("=" * 60)
    print("FINAI MODEL EXPLAINABILITY - SHAP")
    print("=" * 60)

    model, feature_names = load_model()

    train_df, test_df = load_data()

    X_train = prepare_features(
        train_df,
        feature_names
    )

    X_test = prepare_features(
        test_df,
        feature_names
    )

    X_background = sample_data(
        X_train,
        BACKGROUND_SIZE
    )

    X_explain = sample_data(
        X_test,
        EXPLANATION_SIZE
    )

    print("\nBackground sample:", len(X_background))
    print("Explanation sample:", len(X_explain))
    print("Number of features:", len(feature_names))

    shap_values = explain_model(
        model,
        X_background,
        X_explain
    )

    importance_df = calculate_global_importance(
        shap_values,
        X_explain
    )

    plot_global_importance(importance_df)

    plot_shap_summary(
        shap_values,
        X_explain
    )

    generate_individual_explanations(
        model,
        shap_values,
        X_explain
    )

    print("\nTOP 15 IMPORTANT FEATURES")
    print("-" * 60)

    print(importance_df.head(15).to_string(index=False))

    print("\nGenerated files:")
    print("1. results/reports/shap_feature_importance.csv")
    print("2. results/reports/individual_shap_explanations.json")
    print("3. results/plots/shap_global_importance.png")
    print("4. results/plots/shap_summary.png")

    print("\nSHAP explainability completed successfully.")


if __name__ == "__main__":
    main()