# Examples : CSI verification problems rebuilt through Claude

Seven verification problems from the CSI manuals, rebuilt **from scratch** through the extension tools (no CSI model file is opened). Each page has a prompt you can paste into Claude Desktop, the values published in the manual, and the results we obtained.

| Program | Example | Tests | Result |
|---|---|---|---|
| SAP2000 and ETABS | [1-001 Frame, general loading](SAP2000%20and%20ETABS%201-001%20Frame%20general%20loading.md) | frames, 7 load types (point, distributed, trapezoidal, local axes) | ≤ 0.08 % |
| SAP2000 | [1-007 End releases](SAP2000%201-007%20End%20releases.md) | frame releases, support reactions | exact |
| SAP2000 | [1-013 Beam on elastic foundation](SAP2000%201-013%20Beam%20on%20elastic%20foundation.md) | line springs, frame auto-mesh | exact |
| SAP2000 | [2-008 Cantilever plate eigenvalues](SAP2000%202-008%20Cantilever%20plate%20eigenvalues.md) | shells, area auto-mesh, active DOFs, modal | ≤ 0.09 % |
| ETABS | [Example 1 Plane frame gravity loads](ETABS%2001%20Plane%20frame%20gravity%20loads.md) | releases, end offsets, span loads, output stations | ≤ 0.03 % |
| ETABS | [Example 6 Nine-story frame eigenvalues](ETABS%2006%20Nine-story%20frame%20eigenvalues.md) | stories, diaphragms, point masses, eigen | 0.00 % |
| ETABS | [Example 8 Two-story 3D frame response spectrum](ETABS%2008%20Two-story%203D%20frame%20response%20spectrum.md) | 3D frame, user sections, database tables, response spectrum | ≤ 0.15 % |

Full table of all 67 comparisons : [validation/RESULTS.md](../validation/RESULTS.md).

## How the prompts relate to the validation

- **Scripts :** the results above were produced by [`validation/sap2000_examples.py`](../validation/sap2000_examples.py) and [`validation/etabs_examples.py`](../validation/etabs_examples.py). They start the extension and call its MCP tools (`new_blank_model`, `call_api`, `run_analysis`, `get_results` …) exactly as Claude does.
- **Prompts :** each prompt describes the same model as its script, step by step, including the details that matter for an exact match (for example no rigid end offsets in ETABS Example 1, stories at the floor levels in Example 6).
- **What Claude may do differently :** in a chat, Claude may choose other object names or call the tools in a different order. The model and the results should still be the same. If they are not, please open an issue with the conversation.

## Lessons from the examples

- **ETABS end offsets :** ETABS adds rigid end offsets automatically from the member depths. Examples that assume no offsets need them set to 0.
- **ETABS lateral masses :** the default ETABS mass source lumps lateral masses at the **story levels**. A model built with `File.NewBlank` and no stories at the floors gives no mass at all. Use `File.NewGridOnly` (or define stories).
- **ETABS default diaphragm :** a new ETABS model already has a diaphragm called `D1`, so new diaphragms need other names.
- **ETABS user response spectrum :** ETABS's API has no function to define a user response spectrum. It is added through the database table `Functions - Response Spectrum - User Defined` with `edit_table`.
- **Output stations :** `SetOutputStations` with a number of sections divides the clear length into equal parts, which are not quarters when there are point loads. Use a maximum segment size (e.g. L/4) to get the quarter points.
