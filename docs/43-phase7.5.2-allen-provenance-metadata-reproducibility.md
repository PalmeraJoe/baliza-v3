# 43 — Phase 7.5.2 Allen provenance, metadata, and reproducibility

Closure of the records for data already retrieved. No new scientific product was requested beyond the same WFS call used to check reproducibility, plus the WFS capabilities and schema documents that had been read and not stored. Raw feature files were not overwritten. No spot is associated. No local estimate is made.

## What is in hand

Three scientific responses and three service documents. The label remains **DEMONSTRATION / RESEARCH TEST AREA**. The area is the WFS bbox, not a resort.

| File | Role | Bytes | SHA-256 | Retrieval |
|------|------|------:|---------|-----------|
| `benthic_bbox.json` | Dataset retrieval | 7891 | `9c8e75badd8ef73073f3fe0130360fb5878e2674a65d3bee87dabbca7f6beda9` | 2026-10-01T07:46:05.256Z |
| `geomorphic_bbox.json` | Dataset retrieval | 4646 | `f06c0b7ad90c10942c0d1c3fab3148db075421f0eed1b82f2c0ade32ae2e5a58` | 2026-10-01T07:46:05.474Z |
| `mapping_maps.json` | Region publication list | 2133 | `8b8649f8d74e8e51f107784a377eeb88fe0c41ed7792a6305d2a2cd2926278e6` | HTTP Date Thu, 01 Oct 2026 07:46:06 GMT |
| `wfs-capabilities-2.0.0.xml` | Service description | 89844 | `976ca6a84dadf72dfa1e9082732cae65424ffaf0e5a9e74e59dc9028f66755b7` | HTTP Date Thu, 01 Oct 2026 07:52:49 GMT |
| `benthic-describe-feature-type.xml` | Schema | 1164 | `19dfd61dbc1d5529b9abc8d677d8959d65c1c9c203c81da2eb83d374bb3c242d` | HTTP Date Thu, 01 Oct 2026 07:52:50 GMT |
| `geomorphic-describe-feature-type.xml` | Schema | 1173 | `e4daecfc4a8b87d4a0518952dadbaccb46f89b32ef78066263d48479691324f2` | HTTP Date Thu, 01 Oct 2026 07:52:50 GMT |

WMS GetCapabilities was read in Phase 7.5.1 and was not stored. No WMS map image was requested. That is service discovery, not a dataset.

## Inventory

| Field | Benthic extract | Geomorphic extract |
|-------|-----------------|--------------------|
| source | Allen Coral Atlas | Allen Coral Atlas |
| dataset | `coral-atlas:benthic_data_verbose` | `coral-atlas:geomorphic_data_verbose` |
| product | Benthic habitat classes | Geomorphic classes |
| product_version | UNKNOWN in the feature and in the capabilities title | UNKNOWN |
| layer | Title in capabilities: Allen Coral Atlas benthic data | Allen Coral Atlas geomorphic data |
| AOI | Request bbox `-23.48,151.97,-23.47,151.98`, CRS `urn:ogc:def:crs:EPSG::4326` | Same bbox |
| coverage of the layer | Capabilities WGS84 box `-180 -32` to `180 32` | Same |
| spatial extent of these features | UNKNOWN. `geometry` is null because it was not requested | UNKNOWN |
| native_resolution | UNKNOWN. The word resolution is absent from capabilities and from the schema | UNKNOWN |
| CRS of the service layer | `urn:ogc:def:crs:EPSG::4326` | Same |
| CRS inside the feature file | null, recorded as UNKNOWN | null, recorded as UNKNOWN |
| units | `class_name` is a string. `area_sqkm` is a double whose name states square kilometres | Same |
| map_epoch | UNKNOWN on the feature. Region dates in `mapping_maps.json` are not joined | UNKNOWN |
| access_method | WFS 2.0.0 GetFeature, attributes only | Same |
| endpoint | `https://allencoralatlas.org/geoserver/ows` | Same |
| retrieval_timestamp | 2026-10-01T07:46:05.256Z | 2026-10-01T07:46:05.474Z |
| raw_file | `data/phase75/allen/raw/benthic_bbox.json` | `geomorphic_bbox.json` |
| raw_checksum | the SHA-256 above | the SHA-256 above |

Bathymetry, turbidity, and the reef mask are not in this WFS. Their availability as portal downloads is unchanged and is not treated as retrieved.

Schema, stored this phase: both types have `class_name` (string), `geom` (`gml:MultiSurfacePropertyType`), and `area_sqkm` (double). The stored features have `geometry: null`. There is no nodata flag, no band count, and no numeric class code. Categories present are the class names themselves: Coral/Algae, Rock, Rubble, Sand, Seagrass; and Inner Reef Flat, Outer Reef Flat, Plateau, Reef Crest, Reef Slope, Sheltered Reef Slope.

The 5 m figure on the methods page is not copied onto these files.

## Clocks

| Clock | Value |
|-------|--------|
| Source publication time | UNKNOWN for these features |
| Product / map epoch | UNKNOWN on the WFS payload |
| Retrieval time | The GeoJSON `timeStamp` and the HTTP Date above |
| Provider processing time | UNKNOWN |
| Ingestion time | Not a separate stored clock. The file was written in the same session as retrieval |

`mapping_maps.json` publishes dates such as 2022-12-13 for named regions, including Great Barrier Reef and Torres Strait. These features do not name a region, so that date stays on the region list.

## Provenance chain

```text
Allen Coral Atlas
  → benthic or geomorphic habitat map
  → layer coral-atlas:*_data_verbose
  → WFS 2.0.0 GetFeature on /geoserver/ows
  → bbox and propertyName recorded in the URL
  → retrieval timeStamp
  → raw JSON file
  → SHA-256
  → parser phase75.2-allen-record-1
  → normalization phase75.2-none-1
```

Normalization copies the class string. `conversion_method` is `NONE`. A class is not turned into a magnitude. `area_sqkm` stays the provider's polygon area.

Epistemic class of both extracts: `CONTEXT_ONLY`. Transformation type remains `MODEL_ESTIMATED`: a provider map, not a direct observation and not a BALIZA estimate. Bathymetry, turbidity, and reef mask for this retrieval: `NOT_AVAILABLE`.

## Licence

The feature JSON contains no licence field.

The FAQ states that maps, bathymetry, and map statistics are © 2018–2023 Allen Coral Atlas Partnership and Arizona State University, CC BY 4.0. The research citation given there is Allen Coral Atlas (2022), https://doi.org/10.5281/zenodo.3833242. Satellite mosaic imagery is a Planet CC BY-NC-SA 4.0 product and was not retrieved. The same FAQ says reproduction of the entire global habitat-map dataset needs prior written consent, and that WFS is offered subject to the Terms of Use. Those terms prohibit automated retrieval of the website. This test does not decide whether the WFS sentence overrides that prohibition for every later job. Portal login automation remains refused.

## Reproducibility

The same two GetFeature URLs were called again at 2026-10-01T07:52:10Z. The second bodies were not saved over the raw files.

| Extract | Bytes identical | Class and area identical | Matched count |
|---------|-----------------|--------------------------|---------------|
| Benthic | No | Yes | 47 |
| Geomorphic | No | Yes | 26 |

The difference is the feature id and the service timestamp. Scientific content of the attribute extract was stable across that interval. A later change in the live layer would be a service update, not a silent edit of the stored file. The fingerprint used for that comparison drops ids and timestamps.

## Check

The six stored files are non-empty and match the checksums above. The benthic file has 47 features and the geomorphic file has 26. Classes are present. The feature CRS field is empty. The service CRS is present in the capabilities document. Geometry of the AOI features is not in the dataset file, so coverage of those polygons is not verified beyond the WFS filter that returned them.

## Verdict

PHASE 7.5.2 ALLEN PROVENANCE, METADATA & REPRODUCIBILITY CLOSURE — SPATIAL ASSOCIATION STILL OPEN.
