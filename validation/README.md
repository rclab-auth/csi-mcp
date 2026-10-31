# Validation

Scripts that rebuild six CSI verification problems from scratch through the MCP tools of the extensions, run them, and compare the results with the values published in the CSI verification manuals.

| File | Purpose |
|---|---|
| `verif_client.py` | Starts an extension from the repository (`uv run --script`) and calls its tools over MCP, as Claude Desktop does |
| `sap2000_examples.py` | SAP2000 examples 1-007, 1-013, 2-008 |
| `etabs_examples.py` | ETABS examples 1, 6, 8 |
| `make_report.py` | Writes [RESULTS.md](RESULTS.md) from the JSON results |
| `results_*.json` | Results of the last run |

## Running

Requires a licensed SAP2000 / ETABS, [uv](https://docs.astral.sh/uv/) and Python 3.10 or later. Each script starts its program hidden, builds the models (saved in `validation/models`, not in git), and closes the program at the end.

```powershell
uv run --no-project --with "mcp<2" python validation\sap2000_examples.py
uv run --no-project --with "mcp<2" python validation\etabs_examples.py
python validation\make_report.py
```

`etabs_examples.py 1 6` runs only some of the ETABS examples.

## Last run

31/10/2026, SAP2000 26.2.0 and ETABS 23.2.0 : **53 of 53 comparisons pass** (see [RESULTS.md](RESULTS.md)). The prompts that reproduce each example in Claude Desktop are in [examples](../examples).
