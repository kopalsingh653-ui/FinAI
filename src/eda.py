# src/eda.py

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


PLOT_DIR = Path("results/plots")
PLOT_DIR.mkdir(parents=True, exist_ok=True)

DATA_PATH = Path("data/processed/train.csv")


def load_data():

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "Training dataset not found. "
            "Run preprocessing.py and feature_engineering.py first."
        )

    return pd.read_csv(DATA_PATH)


# ---------------------------------------
# 1. Default Distribution
# ---------------------------------------

def plot_default_distribution(df):

    plt.figure(figsize=(8, 5))

    sns.countplot(
        data=df,
        x="default"
    )

    plt.title("Credit Default Distribution")
    plt.xlabel("Default (0 = No, 1 = Yes)")
    plt.ylabel("Number of Customers")

    plt.tight_layout()

    plt.savefig(
        PLOT_DIR / "default_distribution.png",
        dpi=300
    )

    plt.close()


# ---------------------------------------
# 2. Age Distribution
# ---------------------------------------

def plot_age_distribution(df):

    plt.figure(figsize=(9, 5))

    sns.histplot(
        data=df,
        x="AGE",
        hue="default",
        bins=30,
        kde=True,
        element="step"
    )

    plt.title("Age Distribution by Default Status")
    plt.xlabel("Age")
    plt.ylabel("Number of Customers")

    plt.tight_layout()

    plt.savefig(
        PLOT_DIR / "age_distribution.png",
        dpi=300
    )

    plt.close()


# ---------------------------------------
# 3. Credit Limit Distribution
# ---------------------------------------

def plot_credit_limit(df):

    plt.figure(figsize=(9, 5))

    sns.boxplot(
        data=df,
        x="default",
        y="LIMIT_BAL"
    )

    plt.title("Credit Limit vs Default Status")
    plt.xlabel("Default (0 = No, 1 = Yes)")
    plt.ylabel("Credit Limit")

    plt.tight_layout()

    plt.savefig(
        PLOT_DIR / "credit_limit_distribution.png",
        dpi=300
    )

    plt.close()


# ---------------------------------------
# 4. Repayment Status Analysis
# ---------------------------------------

def plot_repayment_status(df):

    repayment = (
        df.groupby("PAY_0", observed=True)["default"]
        .mean()
        .reset_index(name="default_rate")
    )

    repayment["default_rate"] = (
        repayment["default_rate"] * 100
    )

    plt.figure(figsize=(9, 5))

    sns.barplot(
        data=repayment,
        x="PAY_0",
        y="default_rate"
    )

    plt.title(
        "Default Rate by Most Recent Repayment Status"
    )

    plt.xlabel("Repayment Status")
    plt.ylabel("Default Rate (%)")

    plt.tight_layout()

    plt.savefig(
        PLOT_DIR / "repayment_default_rate.png",
        dpi=300
    )

    plt.close()


# ---------------------------------------
# 5. Correlation Heatmap
# ---------------------------------------

def plot_correlation(df):

    numeric_df = df.select_dtypes(
        include="number"
    )

    correlation = numeric_df.corr()

    plt.figure(figsize=(17, 13))

    sns.heatmap(
        correlation,
        cmap="coolwarm",
        center=0,
        annot=False
    )

    plt.title("Financial Feature Correlation Heatmap")

    plt.tight_layout()

    plt.savefig(
        PLOT_DIR / "correlation_heatmap.png",
        dpi=300
    )

    plt.close()


# ---------------------------------------
# 6. Credit Limit Groups
# ---------------------------------------

def plot_credit_limit_groups(df):

    data = df.copy()

    data["credit_limit_group"] = pd.qcut(
        data["LIMIT_BAL"],
        q=5,
        duplicates="drop"
    )

    grouped = (
        data.groupby(
            "credit_limit_group",
            observed=True
        )["default"]
        .mean()
        .reset_index(name="default_rate")
    )

    grouped["default_rate"] *= 100

    plt.figure(figsize=(11, 5))

    sns.barplot(
        data=grouped,
        x="credit_limit_group",
        y="default_rate"
    )

    plt.title("Default Rate by Credit Limit Group")
    plt.xlabel("Credit Limit Group")
    plt.ylabel("Default Rate (%)")

    plt.xticks(rotation=20)

    plt.tight_layout()

    plt.savefig(
        PLOT_DIR / "credit_limit_groups.png",
        dpi=300
    )

    plt.close()


# ---------------------------------------
# 7. Missing Value Analysis
# ---------------------------------------

def plot_missing_values(df):

    missing = (
        df.isnull()
        .sum()
        .sort_values(ascending=False)
    )

    missing = missing[missing > 0]

    if missing.empty:
        print("No missing values found.")
        return

    plt.figure(figsize=(11, 6))

    sns.barplot(
        x=missing.values,
        y=missing.index
    )

    plt.title("Missing Values by Feature")
    plt.xlabel("Number of Missing Values")
    plt.ylabel("Features")

    plt.tight_layout()

    plt.savefig(
        PLOT_DIR / "missing_values.png",
        dpi=300
    )

    plt.close()


# ---------------------------------------
# 8. Financial Behaviour Analysis
# ---------------------------------------

def plot_financial_behaviour(df):

    required = [
        "average_bill",
        "average_payment"
    ]

    if not all(col in df.columns for col in required):
        print("Financial behaviour features unavailable.")
        return

    plt.figure(figsize=(9, 6))

    sns.scatterplot(
        data=df,
        x="average_bill",
        y="average_payment",
        hue="default",
        alpha=0.5
    )

    plt.title("Average Bill vs Average Payment")
    plt.xlabel("Average Bill Amount")
    plt.ylabel("Average Payment Amount")

    plt.tight_layout()

    plt.savefig(
        PLOT_DIR / "financial_behaviour.png",
        dpi=300
    )

    plt.close()


# ---------------------------------------
# 9. Run Complete EDA
# ---------------------------------------

def run_eda():

    df = load_data()

    print("\n" + "=" * 50)
    print("FINAI EXPLORATORY DATA ANALYSIS")
    print("=" * 50)

    print("\nDataset shape:", df.shape)

    print("\nMissing values:", df.isnull().sum().sum())

    print("\nMissing values by column:")

    print(
        df.isnull().sum()[
            df.isnull().sum() > 0
        ]
    )

    print("\nDefault distribution:")

    print(df["default"].value_counts())

    print("\nDefault rate:")

    print(
        round(df["default"].mean() * 100, 2),
        "%"
    )

    # Generate plots
    plot_default_distribution(df)

    plot_age_distribution(df)

    plot_credit_limit(df)

    plot_repayment_status(df)

    plot_correlation(df)

    plot_credit_limit_groups(df)

    plot_missing_values(df)

    plot_financial_behaviour(df)

    print("\n" + "=" * 50)

    print("EDA COMPLETED SUCCESSFULLY")

    print("Plots saved in:", PLOT_DIR)

    print("=" * 50)


if __name__ == "__main__":

    run_eda()