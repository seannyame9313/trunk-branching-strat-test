import json

"""
High level flow:
Load baseline.json and current.json into memory as dictionaries
Compare the two dictionaries recursively
Record each difference with: key, type, baseline, current, severity
Print a readable report with TYPE, BASELINE, CURRENT, SEVERITY
End programme
"""

def compare_dicts(baseline_dict, current_dict):
    differences = []

    for key in baseline_dict:
        if key not in current_dict:
            differences.append({
                "key": key,
                "type": "missing_in_current",
                "baseline": baseline_dict[key],
                "current": None,
                "severity": determine_severity(key, baseline_dict[key], None)
            })
            continue

        baseline_value = baseline_dict[key]
        current_value = current_dict[key]

        if isinstance(baseline_value, dict) and isinstance(current_value, dict):
            nested = compare_dicts(baseline_value, current_value)
            differences.extend(nested)
            continue

        if baseline_value != current_value:
            differences.append({
                "key": key,
                "type": "value_changed",
                "baseline": baseline_value,
                "current": current_value,
                "severity": determine_severity(key, baseline_value, current_value)
            })

    for key in current_dict:
        if key not in baseline_dict:
            differences.append({
                "key": key,
                "type": "unexpected_in_current",
                "baseline": None,
                "current": current_dict[key],
                "severity": determine_severity(key, None, current_dict[key])
            })

    return differences


def print_differences(differences):
    if not differences:
        print("\nNO DIFFERENCES FOUND\n")
        return

    print("\nDIFFERENCES:\n")

    for i, diff in enumerate(differences, start=1):
        label = diff.get("path") or diff.get("key") or "<unknown>"

        print(f"{i}. {label}")
        print(f"    TYPE     : {diff.get('type')}")
        print(f"    BASELINE : {diff.get('baseline')}")
        print(f"    CURRENT  : {diff.get('current')}")
        print(f"    SEVERITY : {diff.get('severity')}\n")


def determine_severity(key, baseline_value, current_value):
    # CRITICAL RISKS
    if key in ["publicly_accessible", "public_access_blocked"]:
        return "critical risk"
    if key == "allow_ssh_from":
        curr = current_value or []
        if isinstance(curr, list) and "0.0.0.0/0" in curr:
            return "critical risk"
        base = baseline_value or []
        if isinstance(base, list) and "0.0.0.0/0" in base:
            return "critical risk"

    # HIGH RISKS
    if key in ["auto_scaling_enabled", "multi_az", "storage_encrypted"]:
        return "high risk"
    if key == "tls_version":
        return "high risk"
    if key == "public_ip_assigned":
        return "high risk"

    # MEDIUM RISKS
    if key in ["ami_id", "engine_version", "log_retention_days", "instance_count", "deletion_protection"]:
        return "medium risk"

    return "low risk"


# ✅ MAIN FUNCTION (safe for pytest)
def main():
    with open('baseline.json', 'r') as file:
        baseline = json.load(file)

    with open('current.json', 'r') as file:
        current = json.load(file)

    print('\nBaseline:')
    print("\n", baseline)
    print(type(baseline))

    print('\nCurrent:')
    print("\n", current)

    diffs = compare_dicts(baseline, current)
    print_differences(diffs)


# ✅ ONLY RUNS WHEN EXECUTED DIRECTLY (NOT DURING TESTS)
if __name__ == "__main__":
    main()