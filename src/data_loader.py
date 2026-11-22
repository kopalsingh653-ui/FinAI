# src/data_loader.py

from pathlib import Path
import pandas as pd
import re

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

DATA_PATH = RAW_DIR / "uci_credit_card.csv"

COLUMN_MAPPING = {
    "X1": "LIMIT_BAL",
    "X2": "SEX",
    "X3": "EDUCATION",
    "X4": "MARRIAGE",
    "X5": "AGE",
    "X6": "PAY_0",
    "X7": "PAY_2",
    "X8": "PAY_3",
    "X9": "PAY_4",
    "X10": "PAY_5",
    "X11": "PAY_6",
    "X12": "BILL_AMT1",
    "X13": "BILL_AMT2",
    "X14": "BILL_AMT3",
    "X15": "BILL_AMT4",
    "X16": "BILL_AMT5",
    "X17": "BILL_AMT6",
    "X18": "PAY_AMT1",
    "X19": "PAY_AMT2",
    "X20": "PAY_AMT3",
    "X21": "PAY_AMT4",
    "X22": "PAY_AMT5",
    "X23": "PAY_AMT6",
    "Y": "default"
}


def clean_column_name(name):
    """Standardise column names."""

    name = str(name).strip().replace("\ufeff", "")
    return name


def normalise_columns(df):
    """Standardise dataset column names and target."""

    df = df.copy()

    df.columns = [
        clean_column_name(col)
        for col in df.columns
    ]

    # Remove duplicate header/index columns
    df = df.loc[:, ~df.columns.duplicated()]

    # Rename original UCI X1-X23 columns
    df = df.rename(columns=COLUMN_MAPPING)

    # Normalise column names for target detection
    def normalise_name(name):
        return re.sub(
            r"[^a-z0-9]",
            "",
            str(name).lower()
        )

    target_aliases = {
        "default",
        "y",
        "defaultpaymentnextmonth",
        "defaultnextmonth",
        "defaultpayment",
        "defaultpaymentnextmonthy"
    }

    target = None

    for col in df.columns:
        if normalise_name(col) in target_aliases:
            target = col
            break

    if target is None:
        raise ValueError(
            "Target column not found.\n"
            f"Available columns: {list(df.columns)}"
        )

    if target != "default":
        df = df.rename(
            columns={target: "default"}
        )

    # Remove identifier columns
    df = df.drop(
        columns=[
            "ID",
            "id",
            "Unnamed: 0"
        ],
        errors="ignore"
    )

    # Convert target values
    original_target = df["default"].copy()

    converted_target = pd.to_numeric(
        original_target.astype(str).str.strip(),
        errors="coerce"
    )

    # Detect repeated header rows accidentally included in CSV
    repeated_header = (
        original_target.astype(str)
        .str.strip()
        .str.lower()
        .isin([
            "default",
            "y",
            "default payment next month",
            "default.payment.next.month"
        ])
    )

    if repeated_header.any():
        print(
            f"Removing {repeated_header.sum()} repeated header row(s)."
        )

        df = df.loc[~repeated_header].copy()
        converted_target = converted_target.loc[
            ~repeated_header
        ]

    # Check for invalid target values
    invalid_mask = (
        converted_target.isna()
        | ~converted_target.isin([0, 1])
    )

    if invalid_mask.any():

        invalid_values = (
            original_target.loc[invalid_mask]
            .astype(str)
            .value_counts()
            .head(10)
        )

        raise ValueError(
            "\nInvalid or missing target values detected.\n"
            f"Number of invalid rows: {invalid_mask.sum()}\n"
            f"Examples:\n{invalid_values}\n\n"
            "Check your CSV target column before proceeding."
        )

    df["default"] = converted_target.astype(int)

    # Reset index
    df = df.reset_index(drop=True)

    return df


def download_uci_dataset():

    try:
        from ucimlrepo import fetch_ucirepo

        print("Downloading UCI dataset...")

        dataset = fetch_ucirepo(id=350)

        X = dataset.data.features.copy()
        y = dataset.data.targets.copy()

        df = X.copy()
        df["default"] = y.iloc[:, 0]

        return df

    except Exception as error:

        raise RuntimeError(
            "Could not download UCI dataset. "
            "Please check internet access or provide "
            "data/raw/uci_credit_card.csv."
        ) from error


def load_credit_data():

    if DATA_PATH.exists():

        print("Loading local UCI dataset...")

        try:
            df = pd.read_csv(
                DATA_PATH,
                encoding="utf-8-sig",
                skipinitialspace=True
            )

        except UnicodeDecodeError:
            df = pd.read_csv(
                DATA_PATH,
                encoding="latin1",
                skipinitialspace=True
            )

    else:
        df = download_uci_dataset()

    print("\nOriginal dataset shape:", df.shape)
    print("Original columns:", list(df.columns))

    df = normalise_columns(df)

    # Dataset validation
    if df.empty:
        raise ValueError("Dataset is empty.")

    if "default" not in df.columns:
        raise ValueError("Default target is missing.")

    # Check missing feature values
    missing = df.isnull().sum()

    if missing.sum() > 0:
        print("\nMissing feature values:")
        print(missing[missing > 0])

    # Check duplicate records
    duplicate_count = df.duplicated().sum()

    print("\nDuplicate rows:", duplicate_count)

    # Do not automatically remove duplicates:
    # inspect them before deciding whether they are genuine.

    # Validate target
    print("\nTarget distribution:")
    print(df["default"].value_counts().sort_index())

    print("\nDefault percentage:")
    print(
        round(df["default"].mean() * 100, 2),
        "%"
    )

    print("\nFinal dataset shape:", df.shape)

    # Save clean dataset
    df.to_csv(DATA_PATH, index=False)

    print("\nDataset loaded and validated successfully.")

    return df


if __name__ == "__main__":

    data = load_credit_data()

    print("\nFirst five rows:")
    print(data.head())

    print("\nDataset information:")
    print(data.info())