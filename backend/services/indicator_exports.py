import csv
import io

from backend.models.indicator import Indicator


FIELDNAMES = [
    "id",
    "indicator_type",
    "value",
    "severity",
    "source",
    "confidence",
    "tags",
    "threat_actor",
    "is_active",
    "created_at",
]


def indicators_to_csv(indicators: list[Indicator]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=FIELDNAMES)
    writer.writeheader()
    for indicator in indicators:
        row = indicator.model_dump()
        row["tags"] = ",".join(row["tags"])
        writer.writerow(row)
    return output.getvalue()
