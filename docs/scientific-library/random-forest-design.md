# Random Forest — decision-support design

Not built. Not a decision engine.

```text
RBM state
  → options the playbook already allows
  → a future model
  → a suitability note on those options
  → DSS
  → human Decision
```

Absolute limits:

- The model cannot name an option that the playbook did not allow.
- It cannot create a Decision, an Action, or an Alert.
- It cannot change a RuleVersion, an IndicatorVersion, or a threshold.
- It cannot treat feature importance as evidence strength.
- It cannot run if the RBM state or the allowed set is missing. The fallback is the allowed list with no ranking, plus an explicit gap.

Target of a future model would be suitability of an already allowed option, trained on recorded state, human decision, action, and outcome. Those rows do not exist as a typed series. Historical decisions are not assumed to be optimal. Resort history is not a training set for this model unless a later scientific phase says so. No metric is chosen. Any future training still requires an explicit training permission and a frozen dataset version (`docs/36-phase7-scientific-data-integration.md`).

`observed_bleaching` is not a feature of this model. A suitability score is not a risk score and is not a weight on DHW.
