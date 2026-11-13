"""
Write tests here proving:
  1. Happy path: running the check against fixtures/plan.json correctly flags the resources
     missing `landlord_account_id` (listing_media, mls_feed_sync) and passes the ones that
     have it (landlord_media[0], screening_report_export). The fixture also has a "no-op"
     entry and a "delete" entry with no `after` block at all — neither should appear in the
     output or crash the check.
  2. Idempotency: running the check twice against the same plan file produces the same
     result both times, with no duplicated output.

check_plan() takes a file path, not a dict — for a case that needs its own plan contents
instead of the shared fixture, write one with pytest's `tmp_path` rather than editing
fixtures/plan.json. You don't need to shell out to the real script for every case.
"""
from scripts.cost_tag_check import check_plan


def test_plan_flags_resources_missing_landlord_tag(capsys):
    result = check_plan("fixtures/plan.json")

    output = capsys.readouterr().out
    print(output, end="")

    assert result != 0
    assert "Missing landlord_account_id tag: aws_s3_bucket.listing_media" in output
    assert "Missing landlord_account_id tag: aws_lambda_function.mls_feed_sync" in output
    assert "landlord_media[0]" not in output
    assert "screening_report_export" not in output
    assert "archive_media" not in output
    assert "decommissioned_media" not in output


def test_plan_with_all_required_tags_passes(tmp_path, capsys):
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        '{"resource_changes": [{"address": "aws_s3_bucket.media", '
        '"change": {"actions": ["create"], "after": '
        '{"tags": {"landlord_account_id": "la-001"}}}}]}',
        encoding="utf-8",
    )

    assert check_plan(str(plan_path)) == 0
    assert capsys.readouterr().out == ""


def test_plan_check_is_idempotent(capsys):
    first_result = check_plan("fixtures/plan.json")
    first_output = capsys.readouterr().out

    second_result = check_plan("fixtures/plan.json")
    second_output = capsys.readouterr().out
    print(second_output, end="")

    assert second_result == first_result
    assert second_output == first_output
