# Design Notes

## B2 — idempotency key

State exactly what key your `cost_tag_check.py` uses to decide whether two resources in the
same run are "the same" for dedup purposes, and why running it twice against an unchanged
plan file produces identical output and exit code without the script keeping any record
between runs. Use the word "idempotency" in your explanation.

The check uses each Terraform resource's `address` as its idempotency key. Addresses identify
resources within a plan, so missing-tag findings are stored in a set and printed once in sorted
order. Each invocation reads the plan from scratch and does not persist state; therefore running
the check twice against an unchanged plan produces the same output and exit code.

## Any other decision with a non-obvious alternative

The check requires `landlord_account_id`, because `LandlordAccount` is the domain's billing and
tenancy boundary. A `tenant_id` tag alone is not sufficient, even though a tenant may be present.
