# Validation results

Each CSI verification example was rebuilt from scratch through the MCP tools (no CSI model file was opened), analyzed, and its results were compared with the values published in the CSI verification manuals (`Manuals\Verification` of each installation). See [examples](../examples) for the prompts.

**67 of 67 comparisons pass.**

## SAP2000 26.2.0

| Example | Quantity | MCP | Published | Difference | |
|---|---|---:|---:|---:|---|
| 1-001 | Case 1 : Uz at the end of the inclined member [in] | -0.0263897 | -0.02639 | -0.00 % | ✅ |
| 1-001 | Case 2 : Uz at the end of the inclined member [in] | 0.0629596 | 0.06296 | -0.00 % | ✅ |
| 1-001 | Case 3 : Uz at the end of the inclined member [in] | 0.0629596 | 0.06296 | -0.00 % | ✅ |
| 1-001 | Case 4 : Uz at the end of the inclined member [in] | -0.296302 | -0.2963 | +0.00 % | ✅ |
| 1-001 | Case 5 : Ux at the knee joint (0, 0, 10 ft) [in] | 0.312502 | 0.3125 | +0.00 % | ✅ |
| 1-001 | Case 6 : Ux at the knee joint (0, 0, 10 ft) [in] | 0.115556 | 0.11556 | -0.00 % | ✅ |
| 1-001 | Case 7 : Ux at the knee joint (0, 0, 10 ft) [in] | 0.00651137 | 0.00651 | +0.02 % | ✅ |
| 1-007 | Model A : Fz at fixed support [k] | 0 | 0 | abs 0 | ✅ |
| 1-007 | Model A : My at fixed support [k-ft] | 50 | 50 | -0.00 % | ✅ |
| 1-007 | Model B : Fz at fixed support [k] | 0 | 0 | abs 0 | ✅ |
| 1-007 | Model B : My at fixed support [k-ft] | 50 | 50 | -0.00 % | ✅ |
| 1-007 | Model C : Fz at fixed support [k] | 5 | 5 | +0.00 % | ✅ |
| 1-007 | Model C : My at fixed support [k-ft] | 0 | 0 | abs 0 | ✅ |
| 1-013 | Uz at midspan [in] | -0.0893327 | -0.08933 | +0.00 % | ✅ |
| 1-013 | My at midspan [k-in] | 17697.9 | 17698 | -0.00 % | ✅ |
| 2-008 | Period mode 1 [s] vs SAP2000 published | 0.0173516 | 0.01735 | +0.01 % | ✅ |
| 2-008 | Period mode 1 [s] vs independent | 0.0173516 | 0.01723 | +0.71 % | ✅ |
| 2-008 | Period mode 2 [s] vs SAP2000 published | 0.00708414 | 0.00708 | +0.06 % | ✅ |
| 2-008 | Period mode 2 [s] vs independent | 0.00708414 | 0.00704 | +0.63 % | ✅ |
| 2-008 | Period mode 3 [s] vs SAP2000 published | 0.00283229 | 0.00283 | +0.08 % | ✅ |
| 2-008 | Period mode 3 [s] vs independent | 0.00283229 | 0.00281 | +0.79 % | ✅ |
| 2-008 | Period mode 4 [s] vs SAP2000 published | 0.00221807 | 0.00222 | -0.09 % | ✅ |
| 2-008 | Period mode 4 [s] vs independent | 0.00221807 | 0.00219 | +1.28 % | ✅ |
| 2-008 | Period mode 5 [s] vs SAP2000 published | 0.00194828 | 0.00195 | -0.09 % | ✅ |
| 2-008 | Period mode 5 [s] vs independent | 0.00194828 | 0.00193 | +0.95 % | ✅ |

## ETABS 23.2.0

| Example | Quantity | MCP | Published | Difference | |
|---|---|---:|---:|---:|---|
| 1-001 | Case 1 : Uz at the end of the inclined member [in] | -0.0264114 | -0.02639 | +0.08 % | ✅ |
| 1-001 | Case 2 : Uz at the end of the inclined member [in] | 0.0629596 | 0.06296 | -0.00 % | ✅ |
| 1-001 | Case 3 : Uz at the end of the inclined member [in] | 0.0629596 | 0.06296 | -0.00 % | ✅ |
| 1-001 | Case 4 : Uz at the end of the inclined member [in] | -0.296302 | -0.2963 | +0.00 % | ✅ |
| 1-001 | Case 5 : Ux at the knee joint (0, 0, 10 ft) [in] | 0.312502 | 0.3125 | +0.00 % | ✅ |
| 1-001 | Case 6 : Ux at the knee joint (0, 0, 10 ft) [in] | 0.115556 | 0.11556 | -0.00 % | ✅ |
| 1-001 | Case 7 : Ux at the knee joint (0, 0, 10 ft) [in] | 0.00651137 | 0.00651 | +0.02 % | ✅ |
| Example 1 | CASE1 B1 M3 End I [k-in] | 0 | 0 | abs 0 | ✅ |
| Example 1 | CASE1 B1 V2 End I [k] | -31.2505 | -31.25 | +0.00 % | ✅ |
| Example 1 | CASE1 B1 M3 1/4 point [k-in] | 1687.53 | 1687.5 | +0.00 % | ✅ |
| Example 1 | CASE1 B1 V2 1/4 point [k] | -31.2505 | -31.25 | +0.00 % | ✅ |
| Example 1 | CASE1 B1 M3 1/2 point [k-in] | 3375.06 | 3375 | +0.00 % | ✅ |
| Example 1 | CASE1 B1 V2 1/2 point [k] | 68.7495 | 68.75 | -0.00 % | ✅ |
| Example 1 | CASE1 B1 M3 3/4 point [k-in] | -337.415 | -337.5 | -0.03 % | ✅ |
| Example 1 | CASE1 B1 V2 3/4 point [k] | 68.7495 | 68.75 | -0.00 % | ✅ |
| Example 1 | CASE1 B1 M3 End J [k-in] | -4049.89 | -4050 | -0.00 % | ✅ |
| Example 1 | CASE1 B1 V2 End J [k] | 68.7495 | 68.75 | -0.00 % | ✅ |
| Example 1 | CASE2 B1 M3 End I [k-in] | 0 | 0 | abs 0 | ✅ |
| Example 1 | CASE2 B1 V2 End I [k] | -67.5005 | -67.5 | +0.00 % | ✅ |
| Example 1 | CASE2 B1 M3 1/4 point [k-in] | 2430.03 | 2430 | +0.00 % | ✅ |
| Example 1 | CASE2 B1 V2 1/4 point [k] | -22.5005 | -22.5 | +0.00 % | ✅ |
| Example 1 | CASE2 B1 M3 1/2 point [k-in] | 2430.06 | 2430 | +0.00 % | ✅ |
| Example 1 | CASE2 B1 V2 1/2 point [k] | 22.4995 | 22.5 | -0.00 % | ✅ |
| Example 1 | CASE2 B1 M3 3/4 point [k-in] | 0.0854484 | 0 | abs 0.0854 | ✅ |
| Example 1 | CASE2 B1 V2 3/4 point [k] | 67.4995 | 67.5 | -0.00 % | ✅ |
| Example 1 | CASE2 B1 M3 End J [k-in] | -4859.89 | -4860 | -0.00 % | ✅ |
| Example 1 | CASE2 B1 V2 End J [k] | 112.499 | 112.5 | -0.00 % | ✅ |
| Example 6 | Eigenvalue mode 1 [rad2/s2] vs ETABS published | 0.589645 | 0.58964 | +0.00 % | ✅ |
| Example 6 | Eigenvalue mode 1 [rad2/s2] vs Wilson and Habibullah | 0.589645 | 0.58954 | +0.02 % | ✅ |
| Example 6 | Eigenvalue mode 2 [rad2/s2] vs ETABS published | 5.53195 | 5.53195 | +0.00 % | ✅ |
| Example 6 | Eigenvalue mode 2 [rad2/s2] vs Wilson and Habibullah | 5.53195 | 5.52696 | +0.09 % | ✅ |
| Example 6 | Eigenvalue mode 3 [rad2/s2] vs ETABS published | 16.5962 | 16.5962 | -0.00 % | ✅ |
| Example 6 | Eigenvalue mode 3 [rad2/s2] vs Wilson and Habibullah | 16.5962 | 16.5879 | +0.05 % | ✅ |
| Example 8 | Period mode 1 [s] vs ETABS published | 0.227059 | 0.22708 | -0.01 % | ✅ |
| Example 8 | Period mode 1 [s] vs Wilson and Habibullah | 0.227059 | 0.22706 | -0.00 % | ✅ |
| Example 8 | Period mode 2 [s] vs ETABS published | 0.215614 | 0.21565 | -0.02 % | ✅ |
| Example 8 | Period mode 2 [s] vs Wilson and Habibullah | 0.215614 | 0.21563 | -0.01 % | ✅ |
| Example 8 | Period mode 3 [s] vs ETABS published | 0.0733462 | 0.07335 | -0.01 % | ✅ |
| Example 8 | Period mode 3 [s] vs Wilson and Habibullah | 0.0733462 | 0.07335 | -0.01 % | ✅ |
| Example 8 | Period mode 4 [s] vs ETABS published | 0.0720045 | 0.07201 | -0.01 % | ✅ |
| Example 8 | Period mode 4 [s] vs Wilson and Habibullah | 0.0720045 | 0.07201 | -0.01 % | ✅ |
| Example 8 | RS X displacement, center of mass story 2 [ft] | 0.0201312 | 0.0201 | +0.15 % | ✅ |

