# Risk-based management — scientific specification

No engine. No weights. No score. No threshold.

A future RBM state would be a structured reading of:

| Component | What may fill it | What may not |
|-----------|------------------|--------------|
| Hazard | Versioned thermal observations: SST, HotSpot, DHW | A weighted sum |
| Exposure | Reef mask or a local statement that reef is present | Allen class treated as live-coral percent |
| Vulnerability | Only a variable whose role is later set to VULNERABILITY with a source | Species richness used because it is available |
| Consequence | A defined outcome such as mortality after a stated interval | CRW legend text treated as measured mortality |
| Uncertainty | Qualitative statement, as in Phase 6 | A confidence of 0.83 |
| Evidence strength | The registry's strength for the finding actually used | Feature importance |

The state is an input to the DSS. It is not a Decision.

MERMAID may later supply field evidence of ecological condition. It does not create an alert or a score. Local resort history may later inform hazard, exposure, vulnerability, consequence, uncertainty, historical response, and recovery at that site. That does not create an engine, a weight, a score, a probability, or a threshold.

Every future numeric rule that consumes this state must point at a `ScientificSource`, a method, an evidence package, and a `RuleVersion`. Until that rule exists, the RBM state is unspecified and must not be invented as "high" or "low".

ML output may inform a component only as an estimate with provenance. It cannot delete a constraint, change a threshold, or select an action.
