import csv
import io
from typing import List, Dict, Any, Tuple


class CSVConnector:
    """
    Parses and sanitizes CSV / tabular data.
    Provides schema inference, row normalization, and mapping translation.
    """

    @classmethod
    def parse_csv_content(cls, content: str) -> Tuple[List[str], List[Dict[str, Any]]]:
        f = io.StringIO(content.strip())
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = [dict(row) for row in reader]
        return list(headers), rows

    @classmethod
    def apply_column_mapping(
        cls,
        rows: List[Dict[str, Any]],
        mapping: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        """
        Translates raw CSV column names into target BankingAIPlatform entity schema fields.
        Example mapping: {"Item Number": "sku", "Product Description": "name", "Cost": "price"}
        """
        normalized = []
        for row in rows:
            record: Dict[str, Any] = {}
            for source_col, target_field in mapping.items():
                if source_col in row:
                    record[target_field] = row[source_col]
            normalized.append(record)
        return normalized
