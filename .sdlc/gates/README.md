# Gates module

> **Redirect:** Write gate documentation lives in [`../gateways/README.md#write-gate-mechanical-acl`](../gateways/README.md#write-gate-mechanical-acl).

This folder keeps only the generated shim [`paths.yaml`](paths.yaml).

> **Data:** [`paths.yaml`](paths.yaml) · **Config:** `.sdlc/sdlc.yaml` → `core.gates.enforcement` · **Runtime:** `.sdlc/dsl/gate.py` + `.cursor/hooks/sdlc_gate_hook.py`

Run `python .sdlc/scripts/sdlc_sync_model.py --write` to refresh `paths.yaml` from lifecycle-model `write_policy`.

See [`../gateways/README.md`](../gateways/README.md) for write gate purpose, stage ACL, commands, and enforcement controls.
