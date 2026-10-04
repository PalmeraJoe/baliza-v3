# SST, HotSpot, and anomaly

Three different CRW fields:

| Field | Formula in v3.1 | Sign |
|-------|-----------------|------|
| SST anomaly | SST minus the interpolated daily climatology | Positive or negative |
| HotSpot | SST minus MMM, else 0 | Never negative |
| SST | CoralTemp | °C |

Anomaly is not HotSpot. Climatology version is part of the measurement. Details: `sources/noaa-crw.md`.
