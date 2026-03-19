# test_compare.py
from config_drift import compare_dicts

def test_value_changed():
    baseline = {"a": 1}
    current = {"a": 2}
    result = compare_dicts(baseline, current)
    assert result[0]["type"] == "value_changed"