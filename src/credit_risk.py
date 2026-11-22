# src/credit_risk.py

from pathlib import Path
import json
import warnings

import joblib
import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import (
    StratifiedKFold,
    RandomizedSearchCV
)

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score
)

from xgboost import XGBClassifier


warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------
# DIRECTORIES AND CONFIGURATION
# ---------------------------------------

PROCESSED_DIR = Path("data/processed")
MODEL_DIR = Path("models")
RESULT_DIR = Path("results/metrics")

MODEL_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "default"
RANDOM_STATE = 42

# Excluded from model training but retained in original data
AUDIT_COLUMNS = ["SEX"]


# ---------------------------------------
# LOAD TRAINING AND VALIDATION DATA
# ---------------------------------------

def load_partitions():

    train_path = PROCESSED_DIR / "train.csv"
    val_path = PROCESSED_DIR / "validation.csv"

    if not train_path.exists() or not val_path.exists():
        raise FileNotFoundError(
            "Training or validation data missing. "
            "Run preprocessing.py and feature_engineering.py first."
        )

    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)

    return train_df, val_df


# ---------------------------------------
# PREPARE FEATURES
# ---------------------------------------

def prepare_features(train_df, val_df):

    X_train = train_df.drop(columns=[TARGET]).copy()
    y_train = train_df[TARGET].astype(int).copy()

    X_val = val_df.drop(columns=[TARGET]).copy()
    y_val = val_df[TARGET].astype(int).copy()

    # Exclude identifiers and selected audit variables
    excluded = [
        "ID",
        "id",
        "Unnamed: 0"
    ] + AUDIT_COLUMNS

    X_train = X_train.drop(
        columns=excluded,
        errors="ignore"
    )

    X_val = X_val.drop(
        columns=excluded,
        errors="ignore"
    )

    # Ensure validation features match training features
    X_val = X_val.reindex(
        columns=X_train.columns
    )

    # Model requires numeric features
    X_train = X_train.apply(
        pd.to_numeric,
        errors="coerce"
    )

    X_val = X_val.apply(
        pd.to_numeric,
        errors="coerce"
    )

    # Replace infinite values with missing values
    X_train = X_train.replace(
        [np.inf, -np.inf],
        np.nan
    )

    X_val = X_val.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # Remove columns that contain no usable training information
    unusable = X_train.columns[
        X_train.notna().sum() == 0
    ].tolist()

    if unusable:
        print("Dropping completely missing features:", unusable)

        X_train = X_train.drop(columns=unusable)
        X_val = X_val.drop(columns=unusable)

    return X_train, X_val, y_train, y_val


# ---------------------------------------
# METRIC CALCULATION
# ---------------------------------------

def calculate_metrics(y_true, predictions, probabilities):

    return {
        "accuracy": accuracy_score(
            y_true, predictions
        ),

        "precision": precision_score(
            y_true,
            predictions,
            zero_division=0
        ),

        "recall": recall_score(
            y_true,
            predictions,
            zero_division=0
        ),

        "f1": f1_score(
            y_true,
            predictions,
            zero_division=0
        ),

        "roc_auc": roc_auc_score(
            y_true,
            probabilities
        ),

        "pr_auc": average_precision_score(
            y_true,
            probabilities
        )
    }


# ---------------------------------------
# LOGISTIC REGRESSION
# ---------------------------------------

def train_logistic_regression(X_train, y_train):

    print("\nTraining Logistic Regression...")

    pipeline = Pipeline([
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        ),
        (
            "model",
            LogisticRegression(
                max_iter=3000,
                solver="lbfgs",
                C=1.0,
                class_weight=None,
                random_state=RANDOM_STATE
            )
        )
    ])

    return pipeline.fit(X_train, y_train)


# ---------------------------------------
# RANDOM FOREST
# ---------------------------------------

def train_random_forest(X_train, y_train):

    print("\nTuning Random Forest...")

    pipeline = Pipeline([
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "model",
            RandomForestClassifier(
                random_state=RANDOM_STATE,
                n_jobs=1
            )
        )
    ])

    parameters = {
        "model__n_estimators": [
            300, 400, 500, 700
        ],

        "model__max_depth": [
            8, 12, 16, 20, None
        ],

        "model__min_samples_split": [
            2, 5, 10, 15
        ],

        "model__min_samples_leaf": [
            1, 2, 4, 6
        ],

        "model__max_features": [
            "sqrt", 0.7, 0.9
        ],

        "model__class_weight": [
            None,
            "balanced",
            "balanced_subsample"
        ]
    }

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE
    )

    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=parameters,
        n_iter=20,
        scoring="roc_auc",
        cv=cv,
        n_jobs=-1,
        random_state=RANDOM_STATE,
        verbose=1,
        refit=True
    )

    search.fit(X_train, y_train)

    print("\nBest Random Forest parameters:")
    print(search.best_params_)

    print(
        "Best cross-validation ROC-AUC:",
        round(search.best_score_, 4)
    )

    return search.best_estimator_


# ---------------------------------------
# XGBOOST
# ---------------------------------------

def train_xgboost(X_train, y_train):

    print("\nTuning XGBoost...")

    negative_count = int((y_train == 0).sum())
    positive_count = int((y_train == 1).sum())

    imbalance_ratio = negative_count / positive_count

    pipeline = Pipeline([
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "model",
            XGBClassifier(
                objective="binary:logistic",
                eval_metric="logloss",
                tree_method="hist",
                random_state=RANDOM_STATE,
                n_jobs=1,
                verbosity=0
            )
        )
    ])

    parameters = {
        "model__n_estimators": [
            200, 300, 400, 500, 600
        ],

        "model__max_depth": [
            2, 3, 4, 5, 6
        ],

        "model__learning_rate": [
            0.01, 0.02, 0.03, 0.05, 0.08
        ],

        "model__subsample": [
            0.7, 0.8, 0.9, 1.0
        ],

        "model__colsample_bytree": [
            0.7, 0.8, 0.9, 1.0
        ],

        "model__min_child_weight": [
            1, 3, 5, 7
        ],

        "model__gamma": [
            0, 0.1, 0.3, 0.5
        ],

        "model__reg_alpha": [
            0, 0.01, 0.1, 1
        ],

        "model__reg_lambda": [
            1, 2, 5, 10
        ],

        "model__scale_pos_weight": [
            1.0,
            0.75 * imbalance_ratio,
            imbalance_ratio
        ]
    }

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE
    )

    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=parameters,
        n_iter=25,
        scoring="roc_auc",
        cv=cv,
        n_jobs=-1,
        random_state=RANDOM_STATE,
        verbose=1,
        refit=True
    )

    search.fit(X_train, y_train)

    print("\nBest XGBoost parameters:")
    print(search.best_params_)

    print(
        "Best cross-validation ROC-AUC:",
        round(search.best_score_, 4)
    )

    return search.best_estimator_


# ---------------------------------------
# VALIDATION COMPARISON
# ---------------------------------------

def compare_models(models, X_val, y_val):

    results = []

    for name, model in models.items():

        probabilities = model.predict_proba(X_val)[:, 1]

        predictions = (
            probabilities >= 0.50
        ).astype(int)

        metrics = calculate_metrics(
            y_val,
            predictions,
            probabilities
        )

        metrics["model"] = name

        results.append(metrics)

        print(f"\n{name} validation results:")

        for metric, value in metrics.items():

            if metric != "model":
                print(
                    f"{metric}: {value:.4f}"
                )

    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values(
        by="roc_auc",
        ascending=False
    )

    results_df.to_csv(
        RESULT_DIR / "model_comparison.csv",
        index=False
    )

    return results_df


# ---------------------------------------
# MAIN TRAINING FUNCTION
# ---------------------------------------

def main():

    print("=" * 60)
    print("FINAI CREDIT RISK MODEL TRAINING")
    print("=" * 60)

    train_df, val_df = load_partitions()

    X_train, X_val, y_train, y_val = prepare_features(
        train_df,
        val_df
    )

    print("\nTraining shape:", X_train.shape)
    print("Validation shape:", X_val.shape)

    print(
        "\nTraining default rate:",
        round(y_train.mean() * 100, 2),
        "%"
    )

    print(
        "Validation default rate:",
        round(y_val.mean() * 100, 2),
        "%"
    )

    models = {}

    # Baseline model
    models["Logistic Regression"] = (
        train_logistic_regression(
            X_train,
            y_train
        )
    )

    # Random Forest
    models["Random Forest"] = (
        train_random_forest(
            X_train,
            y_train
        )
    )

    # XGBoost
    models["XGBoost"] = (
        train_xgboost(
            X_train,
            y_train
        )
    )

    # Compare validation results
    results = compare_models(
        models,
        X_val,
        y_val
    )

    print("\nMODEL COMPARISON")
    print(results.to_string(index=False))

    # Select based on validation ROC-AUC
    best_name = results.iloc[0]["model"]
    best_model = models[best_name]

    print("\nSelected model:", best_name)

    # Save selected model
    joblib.dump(
        best_model,
        MODEL_DIR / "best_credit_model.joblib"
    )

    # Save feature names and model metadata
    metadata = {
        "model_name": best_name,
        "target": TARGET,
        "features": list(X_train.columns),
        "excluded_audit_columns": AUDIT_COLUMNS,
        "random_state": RANDOM_STATE,
        "selection_metric": "roc_auc"
    }

    with open(
        MODEL_DIR / "model_metadata.json",
        "w"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4
        )

    print("\nSaved model:")
    print(MODEL_DIR / "best_credit_model.joblib")

    print("\nTraining completed successfully.")


if __name__ == "__main__":
    main()