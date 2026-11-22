# src/preprocessing.py

from pathlib import Path
import pandas as pd

from sklearn.model_selection import train_test_split

from src.data_loader import load_credit_data


# Directories
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "default"
RANDOM_STATE = 42


def create_data_split(df):
    """
    Create stratified 70:15:15 train-validation-test split.
    """

    if TARGET not in df.columns:
        raise ValueError("Target column 'default' is missing.")

    X = df.drop(columns=[TARGET]).copy()
    y = df[TARGET].copy()

    # Remove identifiers if any remain
    X = X.drop(
        columns=["ID", "id", "Unnamed: 0"],
        errors="ignore"
    )

    # 15% reserved for final testing
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X,
        y,
        test_size=0.15,
        stratify=y,
        random_state=RANDOM_STATE
    )

    # 15% of the complete dataset reserved for validation
    validation_fraction = 0.15 / 0.85

    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val,
        y_train_val,
        test_size=validation_fraction,
        stratify=y_train_val,
        random_state=RANDOM_STATE
    )

    # Reconstruct complete partitions
    train_df = X_train.copy()
    train_df[TARGET] = y_train

    val_df = X_val.copy()
    val_df[TARGET] = y_val

    test_df = X_test.copy()
    test_df[TARGET] = y_test

    return train_df, val_df, test_df


def save_splits(train_df, val_df, test_df):
    """Save all partitions separately."""

    train_path = PROCESSED_DIR / "train.csv"
    val_path = PROCESSED_DIR / "validation.csv"
    test_path = PROCESSED_DIR / "test.csv"

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)

    print("\nSaved datasets:")
    print(train_path)
    print(val_path)
    print(test_path)


def print_split_report(train_df, val_df, test_df):
    """Display split sizes and target distribution."""

    datasets = {
        "Training": train_df,
        "Validation": val_df,
        "Testing": test_df
    }

    print("\n" + "=" * 55)
    print("FINAI DATA SPLIT REPORT")
    print("=" * 55)

    total = sum(len(df) for df in datasets.values())

    for name, data in datasets.items():

        print(f"\n{name} Dataset")
        print("-" * 35)

        print("Records:", len(data))
        print(
            "Percentage:",
            round(len(data) / total * 100, 2),
            "%"
        )

        print(
            "Non-default:",
            int((data[TARGET] == 0).sum())
        )

        print(
            "Default:",
            int((data[TARGET] == 1).sum())
        )

        print(
            "Default rate:",
            round(data[TARGET].mean() * 100, 2),
            "%"
        )


def main():

    print("Loading credit dataset...")

    df = load_credit_data()

    print("\nCreating stratified data splits...")

    train_df, val_df, test_df = create_data_split(df)

    print_split_report(
        train_df,
        val_df,
        test_df
    )

    save_splits(
        train_df,
        val_df,
        test_df
    )

    print("\nPreprocessing split completed successfully.")


if __name__ == "__main__":
    main()