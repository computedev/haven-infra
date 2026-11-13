"""
B2, part 2 — implement the cost-tagging check.

Read fixtures/plan.json for the shape of a `terraform show -json` plan: a `resource_changes`
list, where each entry has a `type`, an `address`, and `change.after.tags`.

Implement check_plan() so it:
  - Looks at every resource being created or updated (skip anything whose change.actions
    isn't "create" or "update" — a "no-op"/"read" change, or a "delete" with no `after`
    block at all).
  - Fails (returns a non-zero exit code) if the resource is missing the tag that identifies
    the real billing unit, per README.md's domain model — not whatever tag the resource
    happens to already carry.
  - Is idempotent: running this twice against the same plan file produces the same result,
    with no duplicate output and no flipped pass/fail. This is about a single run being
    stable and repeatable — it does not require remembering anything between runs.
  - Prints which specific resource address(es) are missing the tag.

Run manually: python scripts/cost_tag_check.py fixtures/plan.json
"""
import json
import sys


def check_plan(plan_path: str) -> int:
    """
    Returns an exit code: 0 if every resource being created or updated has
    `landlord_account_id`, non-zero otherwise.
    """
    with open(plan_path, encoding="utf-8") as plan_file:
        plan = json.load(plan_file)

    missing_addresses = set()
    for resource in plan.get("resource_changes", []):
        change = resource.get("change", {})
        actions = change.get("actions", [])
        if not ({"create", "update"} & set(actions)):
            continue

        after = change.get("after") or {}
        tags = after.get("tags") or {}
        if "landlord_account_id" not in tags:
            address = resource.get("address", "<unknown resource>")
            missing_addresses.add(address)

    for address in sorted(missing_addresses):
        print(f"Missing landlord_account_id tag: {address}")

    return 1 if missing_addresses else 0


if __name__ == "__main__":
    sys.exit(check_plan(sys.argv[1]))
