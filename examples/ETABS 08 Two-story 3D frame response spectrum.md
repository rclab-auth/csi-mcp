# ETABS Example 8 : Two-story 3D frame, response spectrum analysis

**Source :** CSI ETABS verification manual, Example 8 (`Manuals\Verification\Analysis\Example 08.pdf`).

A two-story 3D frame (3 × 3 column lines) with story masses at the centers of mass, under a constant 0.4 g response spectrum. Four periods and the X displacement of the second-story center of mass are compared with Wilson and Habibullah (1992) and Peterson (1981).

## Prompt

```text
Using ETABS, rebuild CSI verification Example 8 (two-story 3D frame, response spectrum) from scratch and compare with the manual.

- Initialize a new model in kip-ft units and create it with File.NewGridOnly: 2 stories of 13 ft, 3 x 3 grid at 35 ft (X) and 25 ft (Y).
- Materials (weight and mass 0): columns E = 350000 ksf, beams E = 500000 ksf.
- General sections, shear areas 0: columns A = 4 ft2, I22 = I33 = 1.25 ft4, J = 2.5 ft4 ; beams A = 5 ft2, I22 = 1.67 ft4, I33 = 2.61 ft4, J = 4.28 ft4. (The manual does not give J; I22 + I33 is assumed.)
- Columns at x = 0, 35, 70 and y = 0, 25, 50 for both stories, fixed bases. Beams along X and Y between all column lines at z = 13 and 26.
- One rigid diaphragm per story (new names, not D1), assigned to all joints of the story.
- At each story add a point at the center of mass (38, 27, z), assign it to the diaphragm, and give it mass 6.212 kip-s2/ft in X and Y (no rotational mass).
- Eigen modal case with 6 modes.
- Response spectrum function CONST, constant 0.4 g with 5 % damping (periods 0 and 10 s). ETABS has no API function for this, so add it through the database table "Functions - Response Spectrum - User Defined" with edit_table.
- Response spectrum case RSX: U1 with function CONST, scale factor g = 32.174 ft/s2, modal case = the eigen case.
- Save, run, and report the first four periods and the maximum X displacement of the second-story center of mass under RSX.

Expected: periods 0.22708, 0.21565, 0.07335, 0.07201 s (references 0.22706, 0.21563, 0.07335, 0.07201) ; X displacement 0.0201 ft.
```

## Results

| Quantity | MCP | Manual ETABS | Difference | References | Difference |
|---|---:|---:|---:|---:|---:|
| Period mode 1 [s] | 0.22706 | 0.22708 | -0.01 % | 0.22706 | 0.00 % |
| Period mode 2 [s] | 0.21561 | 0.21565 | -0.02 % | 0.21563 | -0.01 % |
| Period mode 3 [s] | 0.073346 | 0.07335 | -0.01 % | 0.07335 | -0.01 % |
| Period mode 4 [s] | 0.072005 | 0.07201 | -0.01 % | 0.07201 | -0.01 % |
| RS X displacement, story 2 CM [ft] | 0.020131 | 0.0201 | +0.15 % | 0.0201 | +0.15 % |

Script : [`validation/etabs_examples.py`](../validation/etabs_examples.py), function `example_8`.
