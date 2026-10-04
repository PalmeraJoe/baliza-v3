# 42 — Phase 7.5.1 Allen automated access test

Experimental only. No training, no downscaling, no alert, and no spot association. The parser is `src/baliza/experimental/phase75/allen.py`, marked **EXPERIMENTAL / PHASE 7.5.1**. It is not on the critical path.

Credentials supplied for this test were not written to disk, were not placed in a URL, and were not sent. The official machine interface did not ask for them.

## Official mechanism

Read on 2026-10-01 from the Atlas FAQ and Terms of Use.

| Path | What the provider says | Used here |
|------|------------------------|-----------|
| WMS and WFS | Published for analysis of the benthic and geomorphic maps, subject to the terms. Capabilities URLs are on the FAQ | Yes, unauthenticated |
| `https://allencoralatlas.org/mapping/maps` | Metadata about habitat-map regions | Yes. Region name and publication date only |
| Earth Engine `ACA/reef_habitat/v2_0` | A Google catalog asset | No. It needs a Google session, which is not an Allen password |
| Website “My Areas” package | Login, then the site builds a package. Bathymetry is described as download-only. Turbidity and imagery are optional package layers. Large areas need an account | No |

The terms prohibit a robot, spider, or other automated means from accessing, retrieving, scraping, or indexing the site. Automating the logged-in package screen would be that kind of retrieval. It was not attempted. No username, password, or token variable was verified as an Allen API credential, so none was assumed.

Reproduction of the entire global habitat dataset needs prior written consent. This test requested attributes inside a bbox of about 0.01° by 0.01°.

Attribution stated on the FAQ for maps, bathymetry, and map statistics: © 2018–2023 Allen Coral Atlas Partnership and Arizona State University, CC BY 4.0. Research citation given there: Allen Coral Atlas (2022), doi.org/10.5281/zenodo.3833242. Planet imagery is a different licence and was not downloaded.

## What came back

Label: **DEMONSTRATION / RESEARCH TEST AREA**. The bbox is `-23.48,151.97,-23.47,151.98` in the WFS 2.0 axis order requested as `EPSG:4326`. It sits on the same public cell used in Phase 7.5. It is not a resort.

WMS GetCapabilities and WFS GetCapabilities returned HTTP 200. The only feature types were `coral-atlas:benthic_data_verbose` and `coral-atlas:geomorphic_data_verbose`. Bathymetry, turbidity, and a reef-mask layer were not in that service.

The schema fields are `class_name`, `geom`, and `area_sqkm`. Geometry was not requested, so the raw files stay small and no polygon was silently reduced to one class. Both responses were stored whole:

| File | Bytes | SHA-256 | Service time |
|------|------:|---------|--------------|
| `data/phase75/allen/raw/benthic_bbox.json` | 7891 | `9c8e75badd8ef73073f3fe0130360fb5878e2674a65d3bee87dabbca7f6beda9` | 2026-10-01T07:46:05.256Z |
| `data/phase75/allen/raw/geomorphic_bbox.json` | 4646 | `f06c0b7ad90c10942c0d1c3fab3148db075421f0eed1b82f2c0ade32ae2e5a58` | 2026-10-01T07:46:05.474Z |
| `data/phase75/allen/raw/mapping_maps.json` | 2133 | `8b8649f8d74e8e51f107784a377eeb88fe0c41ed7792a6305d2a2cd2926278e6` | HTTP Date Thu, 01 Oct 2026 07:46:06 GMT |

The benthic response matched 47 features and returned 47: Coral/Algae, Rock, Rubble, Sand, and Seagrass. The geomorphic response matched 26 and returned 26: Inner Reef Flat, Outer Reef Flat, Plateau, Reef Crest, Reef Slope, and Sheltered Reef Slope. None is selected. No mean is taken. `area_sqkm` is the provider's polygon area, not the area of the bbox.

The response `crs` is null because geometry was omitted. The request CRS is recorded. Native 5 m resolution is not a field in these files, so this test does not confirm it from the file. Map epoch is not on the feature. `mapping/maps` lists regions and publication dates, including “Great Barrier Reef and Torres Strait” on 2022-12-13, but these features do not name a region, so that date is not attached to them.

Feature ids differed between an earlier capped request and this full response. They are not a stable key. A repeat on the same morning matched class and area and did not match bytes (`docs/43-phase7.5.2-allen-provenance-metadata-reproducibility.md`).

Each parsed row is `MODEL_ESTIMATED`: a provider map from remote sensing, not a direct observation and not a BALIZA estimate. `spatial_precision` is `UNKNOWN`. `spatial_relation` is `INTERSECTS` only as the WFS bbox filter. Overlap and distance were not computed. Spot association waits for Phase 7.6.

## Products

| Product | This test |
|---------|-----------|
| Benthic map | Attributes retrieved for the bbox. Not a single class |
| Geomorphic map | Attributes retrieved for the bbox. Not a single class |
| Bathymetry | Not on WFS. Portal package only. Not retrieved |
| Turbidity | Not on WFS. Portal package only. Not retrieved |
| Reef mask | Not a WFS layer in the capabilities that were read. Not retrieved |

## Verdict

PHASE 7.5.1 ALLEN CORAL ATLAS AUTOMATED ACCESS TEST — SCIENTIFIC DATA INTEGRATION NOT YET AUTHORIZED BEYOND THE TEST.
