"""
Write tests here proving:
  1. A PropertyManager scoped to la-001 (pm-001) is DENIED access to la-002's tenant's
     screening report (rep-002).
  2. The same PropertyManager (pm-001) IS allowed access to their own account's screening
     report (rep-001).

Use the `property_managers`, `properties`, `tenants`, and `screening_reports` fixtures from
conftest.py — don't re-invent the seed data here.
"""
from app.access_control import can_access_screening_report
from app.models import ScreeningReport


def test_manager_is_denied_access_to_another_landlords_report(
    property_managers, properties, tenants, screening_reports
):
    assert can_access_screening_report(
        property_managers[0],
        screening_reports[1],
        properties=properties,
        tenants=tenants,
    ) is False


def test_manager_can_access_report_in_their_landlord_account(
    property_managers, properties, tenants, screening_reports
):
    assert can_access_screening_report(
        property_managers[0],
        screening_reports[0],
        properties=properties,
        tenants=tenants,
    ) is True


def test_access_is_denied_when_report_tenant_is_missing(
    property_managers, properties, tenants
):
    report = ScreeningReport(
        id="rep-missing-tenant",
        tenant_id="ten-does-not-exist",
        ssn_last4="0000",
        credit_score=0,
    )

    assert can_access_screening_report(
        property_managers[0], report, properties=properties, tenants=tenants
    ) is False


def test_access_is_denied_when_tenant_property_is_missing(
    property_managers, properties, tenants, screening_reports
):
    tenants_without_property = [
        type(tenants[0])(
            id=tenants[0].id,
            name=tenants[0].name,
            property_id="prop-does-not-exist",
        ),
        tenants[1],
    ]

    assert can_access_screening_report(
        property_managers[0],
        screening_reports[0],
        properties=properties,
        tenants=tenants_without_property,
    ) is False
