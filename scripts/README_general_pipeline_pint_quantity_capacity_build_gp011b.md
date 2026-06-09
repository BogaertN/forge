# General Pipeline Build GP-011B — Pint Quantity/Capacity Integration and Dimensional Verification

GP-011B converts the existing `fraction_change_capacity` domain from exact-number arithmetic with decorative unit text into a governed Pint-backed quantity computation path.

## Runtime path

`capacity question -> existing bounded structural matcher -> Pint-validated CapacityQuantityAST -> Forge service request -> Pint SafeQuantityAdapterReceipt -> governed gate -> Manifest Contract v2 -> renderer -> Echo -> DeliveryAuthorizationReceiptV2`

## Active scope

The supported capacity domain accepts quantities of mass or volume only. It accepts compatible requested output conversion within those dimensions, for example kilograms to grams or liters to milliliters. Length and rate quantities are refused with a `FULL_INPUT_PARSE_REFUSED` non-delivery receipt.

## Dependency transition

GP-011B installs and activates from the audited GP-011A wheelhouse:
- Pint 0.25.3
- flexcache 0.3
- flexparser 0.4
- platformdirs 4.10.0

`typing_extensions==4.15.0` already exists inside Forge and exactly satisfies the acquired Pint resolution. It is reused as a protected pre-existing dependency and is not installed, overwritten, or removed by GP-011B.

## Boundaries

GP-011B does not add a new domain, modify MEA, ingest corpus data, persist memory, modify Identity Vault, create Contribution Economy records, mint CT, or write ledgers.
