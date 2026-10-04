# 41 — Phase 7.5 real scientific data acquisition

Acquisition and characterization only. No training. No downscaling. No synthetic environmental values. The experimental parser lives in `src/baliza/experimental/phase75/` and is marked **EXPERIMENTAL / PHASE 7.5**. It is not on the critical path. `alembic/` and the Phase 0–6 domain models, rules, and alert engine were not changed.

There is no authorised resort coordinate in this repository. The case below is a **DEMONSTRATION / RESEARCH TEST AREA**: one public NOAA CRW grid cell. It is not a BALIZA spot and not a resort.

## What was retrieved on 2026-10-01

CoastWatch ERDDAP at `https://coastwatch.noaa.gov/erddap/` answered. A search for `noaa crw` returned eight datasets. Six are CRW heat products. The other two are eddy products and were not retrieved. The legacy `NOAA_DHW` dataset at `coastwatch.pfeg.noaa.gov` returned HTTP 404.

One row was requested for 2026-09-26T12:00:00Z at latitude -23.475 and longitude 151.975. ERDDAP returned that same center. Raw CSV files and the metadata excerpts are in `data/phase75/raw/`. SHA-256 checksums are in `data/phase75/provenance.json`. The downloader did not store a sub-second retrieval clock. That limitation is recorded. The raw files are not edited by the parser.

| Dataset | Variable returned | Value | Unit string | Coverage read from ERDDAP | Access |
|---------|-------------------|-------|-------------|---------------------------|--------|
| `noaacrwsstDaily` | `analysed_sst` | 22.72 | `degree_C` | 1985-01-01 to 2026-09-29, step P1D. Id `CoralTemp-v3.1` | API_AVAILABLE |
| `noaacrwsstanomalyDaily` | `sea_surface_temperature_anomaly` | 0.78 | `degree_C` | 1985-01-01 to 2026-09-29, P1D | API_AVAILABLE |
| `noaacrwsstanomalybaselineDaily` | `sea_surface_temperature_anomaly` | 0.4 | `degree_Celsius` | 2006-01-01 to 2026-09-29. Comment: 1991–2020 baseline | API_AVAILABLE |
| `noaacrwhotspotDaily` | `hotspot` | -4.39 | `degree_C` | 1985-01-01 to 2026-09-26 | API_AVAILABLE |
| `noaacrwdhwDaily` | `degree_heating_week` | 0.0 | `degree_Celsius_weeks` | 1985-03-25 to 2026-09-26 | API_AVAILABLE |
| `noaacrwbaa7dDaily` | `bleaching_alert_area` | 0 | `stress_level` | 1985-03-31 to 2026-09-29. Metadata resolution attribute `P7D` | API_AVAILABLE |

The grid spacing attribute on the SST dataset is the double `0.049999999999999996`, not a separately measured 0.05. Product version attribute is `3.1`. `date_created` on that dataset is `2018-01-01T00:00:00Z`. The CoralTemp license attribute includes an OSTIA restriction for 1985–2002 (academic use, Met Office terms, a five-year clause, and a reproduction form) and a GHRSST / CRW statement for later data. The 2026-09-26 row is inside the near-real-time segment named in the summary (2017 to present). The early-record restriction still sits on the dataset and is not dropped.

Not on this ERDDAP result list, and not retrieved: the 7-day SST trend, the single-day Bleaching Alert Area, and the MMM climatology grid. The CRW product index still links to pages for the trend, a single-day alert view, and a climatology description. Those pages are not data rows. Status for those three: product pages exist; this pass did not obtain a file. A search URL for `SST Trend Coral` returned HTTP 404.

The 7-day Bleaching Alert Area comment on the dataset lists codes 0 No Stress, 1 Bleaching Watch, 2 Bleaching Warning, 3 Alert Level 1, 4 Alert Level 2. The value `0` is that external code. It is not a BALIZA alert and it is not the state `NORMAL`. The methodology page previously recorded a longer CRW scale. This retrieval does not erase that page and does not merge the two descriptions.

The two anomaly datasets share a variable name and returned different numbers, 0.78 and 0.4, in different unit strings. They stay two products. The parser maps both Celsius spellings to `degC` with conversion `identity` and version `phase75-celsius-labels-1`. It does not map `stress_level`.

The HotSpot row is `-4.39`. The methodology page defines HotSpot as `max(SST − MMM, 0)`. This dataset's comment does not state that clip. Source quality is `UNKNOWN` because the row has no flag. BALIZA quality is `QUESTIONABLE` and the negative value is kept. It is not clipped into a local HotSpot.

## The cell is not a spot

NOAA's heritage 50 km station list `orig24_names.txt` publishes "Heron Island, GBR" at latitude -23.5 and longitude 152.0. That point sits 0.025° from each of four 0.05° centers, including the one retrieved. The association of that published point with this cell is not unique, so the spatial relation is `UNKNOWN`. The sample characterizes the grid cell whose center ERDDAP returned. `spatial_precision` is `GRID`. `transformation_type` is `DERIVED` because these are provider products, not in-situ observations.

## Other sources, this pass

| Source | What responded | What was not obtained | Access class |
|--------|----------------|------------------------|--------------|
| EMODnet bathymetry WMS `https://ows.emodnet-bathymetry.eu/wms` | GetCapabilities HTTP 200 | No depth value. The European DTM footprint already recorded does not include this western Pacific cell. No number was filled | API_AVAILABLE for the service. The cell is not covered by the European DTM |
| EMODnet physics, currents, waves | Not queried as a value | No series at this cell | NOT retrieved. Reef completeness remains UNKNOWN |
| Allen Coral Atlas | Methods page HTTP 200. Unauthenticated WFS returned benthic and geomorphic attributes for a small bbox. Provenance for that extract is in `docs/43-phase7.5.2-allen-provenance-metadata-reproducibility.md` | Bathymetry, turbidity, and reef mask were not on that WFS. No geometry was stored. The classes are not a spot measurement | WMS/WFS public for habitat maps. Portal package download was not automated |
| MERMAID | `GET /v1/` HTTP 401. `GET /v1/projects/` HTTP 200 with count 0. `GET /v1/sites/` HTTP 401. `GET /v1/choices/` HTTP 200 (lookup names, not surveys). `GET /v1/projecttags/` HTTP 200 (not copied; the payload contains account identifiers) | No site, survey date, cover, bleaching, fish, or habitat-complexity row | Observations RESTRICTED without a project authorization. An API is not permission to train |
| Resort files | None in the repository | Sensors, surveys, history | NOT_AVAILABLE |

No MERMAID observation was stored. No Allen raster was stored. No EMODnet depth was invented for the Great Barrier Reef.

## Canonical row

Each parsed CRW row can answer where (the returned center), when (the returned instant), what (a dataset-specific name), value, original unit, source, product, version, the resolution attribute, method, source quality `UNKNOWN`, BALIZA quality, provenance (the raw file and checksum), transformation `DERIVED`, spatial precision `GRID`, temporal precision `daily`. `DOWNSCALED` is not produced. `MODEL_ESTIMATED` is not produced.

## Grid-cell report

```text
DEMONSTRATION / RESEARCH TEST AREA
CRW cell center -23.475, 151.975
time 2026-09-26T12:00:00Z

OBSERVED
  none

EXTERNAL INDICATORS
  CoralTemp SST 22.72 degree_C
  SST anomaly v3.1 0.78 degree_C
  SST anomaly 1991-2020 baseline 0.4 degree_Celsius
  HotSpot -4.39 degree_C   QUESTIONABLE against the clipped definition
  DHW 0.0 degree_Celsius_weeks
  Bleaching Alert Area 7-day code 0   external NOAA product, not a BALIZA alert

DERIVED BY BALIZA
  none beyond unit-label identity and the quality note

DATA QUALITY
  source-provided UNKNOWN
  HotSpot BALIZA QUESTIONABLE

FRESHNESS
  product end dates are 2026-09-26 or 2026-09-29
  class CURRENT / RECENT / STALE is still OPEN

SPATIAL RELATION
  UNKNOWN relative to the heritage station point
  GRID for the cell itself

TEMPORAL RELATION
  daily stamp as returned
  7-day BAA metadata says P7D; the row time matched the request. Not reconciled further

UNCERTAINTY
  no numeric error
  two anomaly products disagree because they are different baselines

MISSING
  7-day trend, single-day BAA, MMM grid
  in-situ temperature, Allen layers, EMODnet depth, MERMAID survey, resort history

ESTIMATED
  NONE

DOWNSCALING
  NOT AUTHORIZED
```

## Indicator discovery from this retrieval

| Indicator | After this pass |
|-----------|-----------------|
| CoralTemp SST, v3.1 anomaly, HotSpot, DHW, 7-day BAA | AVAILABLE_NOW as an external grid cell via ERDDAP. Not a spot property |
| 1991–2020 anomaly | AVAILABLE_NOW as a second product. Not interchangeable with the v3.1 anomaly |
| 7-day trend, single-day BAA, MMM | NOT retrieved. Product pages exist. Not AVAILABLE_NOW |
| Allen mask, class, geomorphology, depth, turbidity | NOT_AVAILABLE in this environment |
| EMODnet depth at this cell | NOT_AVAILABLE for the European DTM footprint |
| MERMAID bleaching, cover, fish, complexity | NOT_AVAILABLE without authorization. Not a predictor |
| Resort temperature and surveys | NOT_AVAILABLE |
| Local temperature, local DHW, local HotSpot, risk score | NOT_AVAILABLE |
| Freshness class, completeness class, heat state, alert from these grids | REQUIRES_SCIENTIFIC_DECISION |
| A future target with enough ground truth | Still OPEN. This cell has no in-situ label. No model is authorised |

## Gaps

| Gap | Description | Impact | Indicator | Where | Possible resolution | Status |
|-----|-------------|--------|-----------|-------|---------------------|--------|
| Ground truth | No in-situ temperature or survey at this cell | Nothing here can validate a local estimate | Local temperature, bleaching | This cell | A real measurement with its own provenance | OPEN |
| Source | Trend, single-day BAA, and MMM were not in the retrieved ERDDAP list | Those indicators stay unfilled | Trend, single-day BAA, climatology | CRW | A later file retrieval, not a calculation from this one SST | OPEN |
| Spatial | Heritage point is equidistant from four cells | A spot at that point has no unique pixel | All CRW grids | Published -23.5, 152.0 | A written point-in-pixel rule that states how ties are handled | OPEN |
| Spatial | Allen and EMODnet values were not retrieved here | No habitat or depth context for this cell | Mask, depth, turbidity | This cell | A licensed file, and only inside that product's footprint | OPEN |
| Temporal | HotSpot and DHW end three days before SST in the metadata read | A shared day is not guaranteed | HotSpot, DHW, SST | Datasets | Compare end times per product at `as_of` | OPEN |
| Quality | HotSpot sign disagrees with the clipped definition | Using the number as clipped HotSpot would be false | HotSpot | This row | Keep the provider value and the question | OPEN |
| License / access | OSTIA clause on the SST dataset; MERMAID sites return 401; Allen has no open file in this session | Storage and reuse are not the same for every year and source | SST early record, MERMAID, Allen | Those sources | Read the terms before any redistribution or training | OPEN |
| Spot | No resort dataset | A spot report cannot be produced | All local fields | Repository | An authorised site file | NOT_AVAILABLE |

## Failure behaviour

A short or mismatched CSV raises `AcquisitionError`. It does not insert a temperature. An absent Allen or MERMAID file is a gap, not a zero.

## Model boundary

Ready only as a retrieved external sample and a parser for that CSV shape. Not ready: a spot, a target, ground truth, downscaling, an uncertainty method, an applicability domain. Training is not authorised. Resort rows remain absent and are not base-model training.

## Verdict

PHASE 7.5 REAL SCIENTIFIC DATA ACQUISITION & SOURCE CHARACTERIZATION — ML IMPLEMENTATION NOT AUTHORIZED.
