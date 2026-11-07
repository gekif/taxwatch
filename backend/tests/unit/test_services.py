import pytest

from app.config import DEFAULT_SECRET, Settings, validate_settings
from app.services import calculate_tax, detect_anomaly

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("category", "amount", "expected"),
    [
        ("hotel", 1_000_000, 100_000),
        ("restoran", 500_000, 50_000),
        ("hiburan", 1_000_000, 150_000),
        ("parkir", 20_000, 2_000),
    ],
)
def test_calculate_tax_by_category(category, amount, expected):
    assert calculate_tax(category, amount) == expected


def test_calculate_tax_rounds_half_up():
    assert calculate_tax("hotel", 1_005) == 101  # 100.5 -> 101
    assert calculate_tax("hotel", 1_004) == 100  # 100.4 -> 100


@pytest.mark.parametrize("amount", [0, -1])
def test_calculate_tax_rejects_non_positive(amount):
    with pytest.raises(ValueError):
        calculate_tax("hotel", amount)


def test_calculate_tax_rejects_unknown_category():
    with pytest.raises(ValueError):
        calculate_tax("casino", 1000)


def test_anomaly_above_threshold():
    assert detect_anomaly(50_000_000, 50_000_000, []) == "above_threshold"


def test_anomaly_spike_vs_average():
    assert detect_anomaly(4_000_000, 50_000_000, [1_000_000] * 5) == "spike_vs_average"


def test_no_spike_flag_with_short_history():
    assert detect_anomaly(4_000_000, 50_000_000, [1_000_000] * 4) is None


def test_normal_transaction_not_flagged():
    assert detect_anomaly(1_200_000, 50_000_000, [1_000_000] * 10) is None


def test_production_rejects_default_secret():
    with pytest.raises(RuntimeError):
        validate_settings(Settings(env="production", secret_key=DEFAULT_SECRET))


def test_production_accepts_strong_secret():
    validate_settings(Settings(env="production", secret_key="x" * 40))
