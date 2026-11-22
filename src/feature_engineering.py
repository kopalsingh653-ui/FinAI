# src/feature_engineering.py

import numpy as np
import pandas as pd


TARGET = "default"

PAY_COLUMNS = [
    "PAY_0",
    "PAY_2",
    "PAY_3",
    "PAY_4",
    "PAY_5",
    "PAY_6"
]

BILL_COLUMNS = [
    "BILL_AMT1",
    "BILL_AMT2",
    "BILL_AMT3",
    "BILL_AMT4",
    "BILL_AMT5",
    "BILL_AMT6"
]

PAYMENT_COLUMNS = [
    "PAY_AMT1",
    "PAY_AMT2",
    "PAY_AMT3",
    "PAY_AMT4",
    "PAY_AMT5",
    "PAY_AMT6"
]


def add_financial_features(df):
    """
    Add financial behaviour features.

    This function performs row-level transformations only.
    It does not learn statistics from the complete dataset.
    """

    df = df.copy()

    required_columns = (
        PAY_COLUMNS +
        BILL_COLUMNS +
        PAYMENT_COLUMNS +
        ["LIMIT_BAL"]
    )

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    # Convert financial columns to numeric
    for col in required_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # -----------------------------------
    # 1. Repayment behaviour
    # -----------------------------------

    df["avg_repayment_status"] = (
        df[PAY_COLUMNS].mean(axis=1)
    )

    df["max_delinquency"] = (
        df[PAY_COLUMNS].max(axis=1)
    )

    df["min_repayment_status"] = (
        df[PAY_COLUMNS].min(axis=1)
    )

    # Positive repayment status indicates delayed payment
    df["late_payment_months"] = (
        df[PAY_COLUMNS] > 0
    ).sum(axis=1)

    # More than one month overdue
    df["severe_delinquency_months"] = (
        df[PAY_COLUMNS] > 1
    ).sum(axis=1)

    # Recent repayment status
    df["recent_delinquency"] = (
        df["PAY_0"] > 0
    ).astype(int)

    # -----------------------------------
    # 2. Billing behaviour
    # -----------------------------------

    df["average_bill"] = (
        df[BILL_COLUMNS].mean(axis=1)
    )

    df["total_bill"] = (
        df[BILL_COLUMNS].sum(axis=1)
    )

    df["maximum_bill"] = (
        df[BILL_COLUMNS].max(axis=1)
    )

    df["minimum_bill"] = (
        df[BILL_COLUMNS].min(axis=1)
    )

    # Recent bill compared with previous month
    df["bill_change_recent"] = (
        df["BILL_AMT1"] - df["BILL_AMT2"]
    )

    # -----------------------------------
    # 3. Previous payment behaviour
    # -----------------------------------

    df["average_payment"] = (
        df[PAYMENT_COLUMNS].mean(axis=1)
    )

    df["total_payment"] = (
        df[PAYMENT_COLUMNS].sum(axis=1)
    )

    df["maximum_payment"] = (
        df[PAYMENT_COLUMNS].max(axis=1)
    )

    # -----------------------------------
    # 4. Payment-to-bill ratio
    # -----------------------------------

    bill_denominator = (
        df[BILL_COLUMNS].abs().sum(axis=1)
    )

    df["payment_to_bill_ratio"] = (
        df["total_payment"]
        / bill_denominator.replace(0, np.nan)
    )

    # -----------------------------------
    # 5. Credit utilisation proxy
    # -----------------------------------

    df["credit_utilisation"] = (
        df["average_bill"]
        / df["LIMIT_BAL"].replace(0, np.nan)
    )

    # -----------------------------------
    # 6. Payment trend
    # -----------------------------------

    # Compare recent payment with older payment
    df["payment_trend"] = (
        df["PAY_AMT1"] - df["PAY_AMT6"]
    )

    # -----------------------------------
    # 7. Numerical safety
    # -----------------------------------

    df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    return df


def process_split_files():

    from pathlib import Path

    processed_dir = Path("data/processed")

    split_files = [
        "train.csv",
        "validation.csv",
        "test.csv"
    ]

    for filename in split_files:

        path = processed_dir / filename

        if not path.exists():
            raise FileNotFoundError(
                f"{path} not found. "
                "Run preprocessing.py first."
            )

        df = pd.read_csv(path)

        original_rows = len(df)

        engineered_df = add_financial_features(df)

        if len(engineered_df) != original_rows:
            raise ValueError(
                f"Row count changed while processing {filename}."
            )

        engineered_df.to_csv(
            path,
            index=False
        )

        print(
            f"Processed {filename}: "
            f"{engineered_df.shape}"
        )


if __name__ == "__main__":

    process_split_files()

    print(
        "\nFinancial feature engineering completed."
    )