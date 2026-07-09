"""Dataframe serialization utilities for ord-plan analytics."""

import json
from pathlib import Path
from typing import Any, Optional

import pandas as pd  # type: ignore[import-untyped]


class DataFrameSerializer:
    """Utility class for serializing pandas DataFrames."""

    @staticmethod
    def serialize(
        df: pd.DataFrame,
        output_path: str,
        format: str = "pickle",
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Serialize DataFrame to file.

        Args:
            df: DataFrame to serialize
            output_path: Path to output file
            format: Output format (pickle, json, csv)
            metadata: Optional metadata to include
        """
        output = Path(output_path)

        if format == "pickle":
            DataFrameSerializer._serialize_pickle(df, output, metadata)
        elif format == "json":
            DataFrameSerializer._serialize_json(df, output, metadata)
        elif format == "csv":
            DataFrameSerializer._serialize_csv(df, output, metadata)
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def _serialize_pickle(
        df: pd.DataFrame, output_path: Path, metadata: Optional[dict[str, Any]]
    ) -> None:
        """Serialize DataFrame to pickle format."""
        import pickle  # nosec B403

        data = {"df": df, "metadata": metadata or {}}
        with open(output_path, "wb") as f:
            pickle.dump(data, f)  # nosec B301

    @staticmethod
    def _serialize_json(
        df: pd.DataFrame, output_path: Path, metadata: Optional[dict[str, Any]]
    ) -> None:
        """Serialize DataFrame to JSON format."""
        data = {
            "data": df.to_dict(orient="records"),
            "metadata": metadata or {},
        }
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    @staticmethod
    def _serialize_csv(
        df: pd.DataFrame,
        output_path: Path,
        metadata: Optional[dict[str, Any]],  # noqa: ARG004
    ) -> None:
        """Serialize DataFrame to CSV format."""
        df.to_csv(output_path, index=False)

    @staticmethod
    def load(
        input_path: str, format: str = "pickle"
    ) -> tuple[pd.DataFrame, dict[str, Any]]:
        """Load serialized DataFrame from file.

        Args:
            input_path: Path to input file
            format: Input format (pickle, json)

        Returns:
            Tuple of (DataFrame, metadata)
        """
        input_p = Path(input_path)

        if format == "pickle":
            return DataFrameSerializer._load_pickle(input_p)
        elif format == "json":
            return DataFrameSerializer._load_json(input_p)
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def _load_pickle(input_path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
        """Load DataFrame from pickle format."""
        import pickle  # nosec B403

        with open(input_path, "rb") as f:
            data = pickle.load(f)  # nosec B301

        if isinstance(data, dict) and "df" in data:
            return data["df"], data.get("metadata", {})
        elif isinstance(data, pd.DataFrame):
            return data, {}
        else:
            raise ValueError("Invalid pickle format")

    @staticmethod
    def _load_json(input_path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
        """Load DataFrame from JSON format."""
        with open(input_path) as f:
            data = json.load(f)

        if isinstance(data, dict) and "data" in data:
            df = pd.DataFrame(data["data"])
            return df, data.get("metadata", {})
        else:
            raise ValueError("Invalid JSON format")
