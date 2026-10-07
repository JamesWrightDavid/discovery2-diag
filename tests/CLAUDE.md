# tests/

The hardware-free pytest suite for the pack. Install the platform and the pack first
(`pip install "openostler @ git+https://github.com/openostler/ostler@main"`, then
`pip install -e ".[dev]"`), then run `pytest -q` from the repo root.

## Files

- `fakes.py` — `FakeKLineEcu`, a half-duplex ECU simulator at the transport level.
- `fake_sources.py` — simulated Td5/SLABS/info sources and the fake fault report (test
  scaffolding; the product has no demo mode).
- `test_pack_contract.py` — the pack resolves through the `openostler.vehicle` entry point
  and satisfies the platform's `VehiclePack` contract (api_version, manifest, module ids,
  stores, actions, sniff spec, `layout.json` against the platform's layout schema, with
  `driver_side: "right"`).
- `test_lr_d2_pack.py` — pack members, ids and aliases. `test_d2_catalog.py` — the real
  menus against the platform catalog (links resolve, drift guard).
  `test_demo_sessions.py` — the committed demo sessions regenerate byte for byte.
- `phase0_golden.py` + `test_phase0_golden.py` — platform outputs over this pack, by value
  (the Phase 0 / split no-behaviour-change golden).
- `test_metrics_d2.py` — every store `metric` resolves to a known VSS path, the
  common-set fields carry the expected one (ADR-0016), and a path mapped by several modules
  has exactly one `primary` module. Skips on a platform without metrics.
- `test_kline_profiles_d2.py` — the modules' K-line profiles; a profile-built session
  sends the same bytes and sleeps as the legacy constructors.
- `test_<area>.py` — one file per module layer or tool (td5, slabs, bcu, airbag, importer, …).

## Editing rules

- No test may need hardware or the network.
- Platform behaviour is tested in the platform repo with a fake pack; test here only what
  depends on Discovery 2 code or data.
- Prefer a `FakeKLineEcu` response sequence or `callable(count)` over mocking internals.
- Do not hard-code the test count in docs. CI is the source.
