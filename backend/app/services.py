"""Pure business rules (no I/O) so they are trivially unit-testable."""

from sqlalchemy.orm import Session

from .models import AuditLog

# Regional tax rates in percent, by taxpayer category.
RATES = {"hotel": 10, "restoran": 10, "hiburan": 15, "parkir": 10}


def calculate_tax(category: str, amount: int) -> int:
    """Tax in whole rupiah, rounded half up, using integer arithmetic only."""
    if amount <= 0:
        raise ValueError("amount must be positive")
    if category not in RATES:
        raise ValueError(f"unknown category: {category}")
    return (amount * RATES[category] + 50) // 100


def detect_anomaly(amount: int, threshold: int, history: list[int]) -> str | None:
    """Return a flag reason, or None when the transaction looks normal."""
    if amount >= threshold:
        return "above_threshold"
    if len(history) >= 5 and amount > 3 * (sum(history) / len(history)):
        return "spike_vs_average"
    return None


def log_action(
    db: Session,
    actor: str,
    action: str,
    entity: str,
    entity_id: int | None = None,
    detail: str = "",
) -> None:
    """Stage an audit record; the caller commits so it is atomic with the change."""
    db.add(
        AuditLog(
            actor=actor, action=action, entity=entity, entity_id=entity_id, detail=detail[:255]
        )
    )
