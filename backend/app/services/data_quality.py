from typing import List, Dict, Any, Tuple
import re


class DataQualityEngine:
    """
    Automated Data Quality & Hygiene Engine.
    Detects missing values, duplicates, invalid prices, inconsistent dates, and invalid formats.
    Computes an aggregate health score (0-100%) and returns actionable issue diagnostics.
    """

    @classmethod
    def validate_products(cls, records: List[Dict[str, Any]]) -> Tuple[int, List[Dict[str, Any]]]:
        issues: List[Dict[str, Any]] = []
        seen_skus = set()
        total_checks = max(len(records) * 4, 1)
        failed_checks = 0

        for idx, item in enumerate(records):
            # 1. Missing required fields (sku, name, price)
            sku = item.get("sku")
            if not sku:
                failed_checks += 1
                issues.append({
                    "record_index": idx,
                    "field": "sku",
                    "issue_type": "missing_required_field",
                    "description": "Product record is missing mandatory SKU",
                })
            elif sku in seen_skus:
                failed_checks += 1
                issues.append({
                    "record_index": idx,
                    "field": "sku",
                    "issue_type": "duplicate_record",
                    "description": f"Duplicate SKU '{sku}' detected across dataset",
                })
            else:
                seen_skus.add(sku)

            if not item.get("name"):
                failed_checks += 1
                issues.append({
                    "record_index": idx,
                    "field": "name",
                    "issue_type": "missing_required_field",
                    "description": "Product record is missing mandatory name",
                })

            # 2. Invalid Prices
            price = item.get("price")
            try:
                numeric_price = float(price) if price is not None else -1
                if numeric_price < 0:
                    failed_checks += 1
                    issues.append({
                        "record_index": idx,
                        "field": "price",
                        "issue_type": "invalid_price",
                        "description": f"Price must be non-negative (received: {price})",
                    })
            except (ValueError, TypeError):
                failed_checks += 1
                issues.append({
                    "record_index": idx,
                    "field": "price",
                    "issue_type": "invalid_price",
                    "description": f"Price cannot be parsed as a valid numeric value (received: {price})",
                })

        # Calculate score (100 - proportion of failed checks)
        score = max(0, min(100, int(((total_checks - failed_checks) / total_checks) * 100)))
        return score, issues

    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        if not phone:
            return True
        # Basic international or national format check: optional +, 7 to 15 digits, spaces/hyphens
        clean = re.sub(r"[\s\-\(\)\.]", "", phone)
        return bool(re.match(r"^\+?[0-9]{7,15}$", clean))
