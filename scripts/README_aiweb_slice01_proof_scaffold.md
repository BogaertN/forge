# AI.Web Slice 1 Proof Scaffold

This folder contains deterministic local scripts for Slice 1 only.

## Scope

The scaffold records proof and receipt structure. It does not create language authority, memory authority, evidence authority, external-resource authority, UI authority, delivery authority, action authority, GP-014 supersession, GP-015 repair, or GP-015R1 installation.

## Commands

Run verifier:

```bash
python3 scripts/aiweb_slice01_proof_scaffold_verify.py /home/nic/forge
```

Run behavior test:

```bash
python3 scripts/test_aiweb_slice01_proof_scaffold.py /home/nic/forge
```
