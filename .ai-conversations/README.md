# AI conversation records

If you used an AI assistant for B2, put the record of that here before submitting (export,
screenshot-transcribed text, or your own written summary of the exchange) — see B2's section
in DESIGN_NOTES.md for what to cover. Leave this folder empty if you didn't use one.


#### Prompt1 
 
 ```text
 act as my SRE who has experience is cloud platform , deployment and management using ci/cd , terraform and python for automation, i want you to go throught the entire repo specifically read all the annotation [README.md](README.md)  files to understand the entire repo .

How domain model works
```

`solution`



The domain model is a tenant-isolation hierarchy centered on `LandlordAccount`:

```text
LandlordAccount
└── Property
    └── Tenant
        └── ScreeningReport

PropertyManager ── belongs to exactly one LandlordAccount
```

### Entities

- `LandlordAccount`
  - The tenant/billing boundary.
  - Examples: `la-001`, `la-002`.
  - Every property, tenant, and screening report ultimately belongs to one account.

- `Property`
  - Belongs to a landlord through `landlord_account_id`.
  - Example: `prop-001 → la-001`.

- `Tenant`
  - Belongs to a property through `property_id`.
  - It does not directly store `landlord_account_id`.
  - Example: `ten-001 → prop-001 → la-001`.

- `ScreeningReport`
  - Belongs to a tenant through `tenant_id`.
  - It contains sensitive information such as SSN last four digits and credit score.
  - Example: `rep-001 → ten-001 → prop-001 → la-001`.

- `PropertyManager`
  - Is scoped directly to exactly one landlord account.
  - Example: `pm-001 → la-001`.

### Access-control rule

A property manager may access a screening report only when both resolve to the same `LandlordAccount`.

The access lookup must therefore be:

```text
PropertyManager.landlord_account_id
        ==
ScreeningReport
  → Tenant
  → Property
  → Property.landlord_account_id
```

For example:

```text
pm-001 → la-001
rep-001 → ten-001 → prop-001 → la-001
```

Access is allowed.

```text
pm-001 → la-001
rep-002 → ten-002 → prop-002 → la-002
```

Access is denied.

The model deliberately requires traversal because `ScreeningReport` and `Tenant` do not carry the landlord account ID directly. If the tenant or property cannot be found, access must fail closed.

### Billing and infrastructure meaning

`LandlordAccount` is also the billing unit. Infrastructure resources associated with landlord data should therefore use:

```text
landlord_account_id
```

as their cost-allocation tag.

A `tenant_id` alone is insufficient because the tenant is only indirectly associated with the billing account. The Terraform media buckets are intended to be one bucket per landlord account, for example:

```text
haven-media-la-001
haven-media-la-002
```

The repository’s Terraform configuration has already moved from positional `count` indexing to key-based `for_each`, which is safer because resources are addressed by stable landlord IDs instead of list positions.

### Current repository state

The model and seed data are complete, but these assessment functions are still stubs:

- `app/access_control.py`
  - Must resolve report → tenant → property and compare landlord-account IDs.

- `scripts/cost_tag_check.py`
  - Must check `create` and `update` resources for the `landlord_account_id` tag.

The important design principle throughout the repository is:

> The landlord account is the security boundary, tenancy boundary, and billing boundary.


### b1 part 1 access control

```text
from b2 part 1 lets us impliment the access screening report that  PM of the landlord account can only access other should not be able to access it.



- read the [access_control.py](app/access_control.py)  - read its annotation use [README.md](README.md)  here to understand the hirecarchy to build the code to ensure we have the right access procvided.
```

```text
Implemented can_access_screening_report() in [app/access_control.py](C:/Users/Admin/Downloads/haven-infra-assessment-main/app/access_control.py).

It now:
- Resolves ScreeningReport → Tenant → Property.
- Compares the property’s landlord_account_id with the manager’s account.
- Denies access if the tenant or property is missing.
- Prevents cross-landlord report access.
The test could not run because Python is not installed/configured in the environment (pyenv has no active version).

```

`test cases`

```text
### question

now lets write test cases in [test_access_control.py](tests/test_access_control.py)  to ensure that code we have written is working  and also lets test it locally using pytest if you cannot run locally provide me to run it locally
Added four access-control tests in [tests/test_access_control.py]

(C:\Users\Admin\Downloads\haven-infra-assessment-main\tests\test_access_control.py):

- Cross-landlord access is denied.
- Same-landlord access is allowed.
- Missing tenant fails closed.
- Missing property fails closed.

I attempted to run:

```powershell
pytest -q tests/test_access_control.py
```

but Python is not configured locally:

```text
No global/local python version has been set yet.
```

After configuring Python and installing dependencies, run:

```powershell
pyenv local 3.7.4
python -m pip install -r requirements.txt
pytest -q tests/test_access_control.py
```

Expected result:

```text
4 passed
```

`b2 part 2 cost tag check`

```
in  b2 next part is to check the tagging&#x20;

ensure you have read the [cost_tag_check.py](scripts/cost_tag_check.py) and [test_cost_tag_check.py](tests/test_cost_tag_check.py)&#x20;



and impliment the tag check in cost_tag_check.py then write the test cases for the same to check it in test_cost_tag_check.py



- ensure that the test cases are checked and locally&#x20;
- ensure the test case values shown up in the terminal screen so that it can be validated on the go&#x20;

use the below addtional information to create that&#x20;



1. A cost-tagging check that fails if a resource is missing a landlord_account_id tag - the real billing unit - not tenant_id, which is what resources are tagged with today.

### Must work:

- A test proving the cross-account case is denied, and the same-account case is allowed.
- The tag check is generic, not hardcoded to one example resource.
- The tag check is idempotent - rerunning it on an unchanged plan gives the same result. State the exact key you used to determine that, in DESIGN_NOTES.md, using the word ‘idempotency’
- Before writing any code: say out loud, on your recording, what you learned from the README that changes how you'd build this
```
