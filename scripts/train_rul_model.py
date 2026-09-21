from pathlib import Path
import json

import pandas as pd

from predictive_maintenance.rul_model import (
    prepare_rul_dataset,
    train_rul_model,
    evaluate_rul_model,
    save_rul_model,
)


SOURCE_FILE = Path(
    "data/processed/test2_features.csv"
)

MODEL_FILE = Path(
    "models/test2_b1_rul_xgb.joblib"
)

METRICS_FILE = Path(
    "data/processed/test2_b1_rul_metrics.json"
)


def main() -> None:

    print("Loading feature dataset...")

    df = pd.read_csv(
        SOURCE_FILE,
        parse_dates=["Timestamp"],
    )

    rul_df, feature_columns = prepare_rul_dataset(
        df,
        bearing_id=1,
    )

    rul_df = rul_df.sort_values(
        "Timestamp"
    ).reset_index(drop=True)

    split_index = int(
        len(rul_df) * 0.80
    )

    train_df = rul_df.iloc[
        :split_index
    ].copy()

    test_df = rul_df.iloc[
        split_index:
    ].copy()

    print()
    print("RUL dataset:")
    print(f"Rows: {len(rul_df)}")
    print(f"Features: {feature_columns}")

    print()
    print(
        f"Training rows: {len(train_df)}"
    )
    print(
        f"Test rows: {len(test_df)}"
    )

    print()
    print(
        "Training RUL range:"
        f" {train_df['RUL_Hours'].min():.2f}"
        f" - {train_df['RUL_Hours'].max():.2f} hours"
    )

    print(
        "Test RUL range:"
        f" {test_df['RUL_Hours'].min():.2f}"
        f" - {test_df['RUL_Hours'].max():.2f} hours"
    )

    print()
    print("Training XGBoost RUL model...")

    model = train_rul_model(
        train_df,
        feature_columns,
    )

    metrics = evaluate_rul_model(
        model,
        test_df,
        feature_columns,
    )

    print()
    print("Evaluation:")
    print(
        f"MAE:  {metrics['mae_hours']:.3f} hours"
    )
    print(
        f"RMSE: {metrics['rmse_hours']:.3f} hours"
    )
    print(
        f"R²:   {metrics['r2']:.4f}"
    )

    print()
    print("Feature importance:")

    importance = dict(
        zip(
            feature_columns,
            model.feature_importances_,
        )
    )

    for feature, value in sorted(
        importance.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        print(
            f"{feature}: {value:.4f}"
        )

    save_rul_model(
        model,
        feature_columns,
        MODEL_FILE,
    )

    METRICS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    METRICS_FILE.write_text(
        json.dumps(
            metrics,
            indent=4,
        )
    )

    predictions = model.predict(
        test_df[feature_columns]
    )

    predictions = predictions.clip(0)

    preview = test_df[
        [
            "Timestamp",
            "RUL_Hours",
        ]
    ].copy()

    preview["Predicted_RUL_Hours"] = predictions

    print()
    print("Final test observations:")
    print(
        preview.tail(10).to_string(
            index=False
        )
    )

    print()
    print(
        f"Model saved to: {MODEL_FILE}"
    )

    print(
        f"Metrics saved to: {METRICS_FILE}"
    )


if __name__ == "__main__":
    main()