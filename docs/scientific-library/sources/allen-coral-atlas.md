# Allen Coral Atlas — product note

Pages read:

- Methods: https://allencoralatlas.org/methods/
- FAQ: https://allencoralatlas.org/resources/
- Earth Engine catalog, ACA reef habitat v2.0: https://developers.google.com/earth-engine/datasets/catalog/ACA_reef_habitat_v2_0
- Lyons and co-authors, global reef-area estimates (article page): https://www.sciencedirect.com/science/article/pii/S2949790624000016

## Products described

| Product | What the pages state | What they do not state |
|---------|----------------------|------------------------|
| Benthic habitat v2 | 5 m pixels. Shallow reefs. FAQ: benthic layer covers areas shallower than 10 m. Classes include sand, seagrass, and other benthic labels in the Earth Engine table. | Live coral cover percent. Species. Bleaching percent. |
| Geomorphic zonation v2 | 5 m pixels. FAQ: geomorphic layer covers areas shallower than 15 m. | A depth measurement at a BALIZA station. |
| Reef extent / reef mask | 5 m global shallow-reef extent, including reef area not given a benthic or geomorphic class. | A legal boundary or a management zone. |
| Bathymetry | Methods: 10 m, Sentinel-2 surface reflectance, images with low cloud and low turbidity over 12 months, median depth. Gaps filled with Landsat-8 or Planet Dove. Relative / satellite-derived depth. | Surveyed depth. Uncertainty per pixel was not copied as a number. |
| Turbidity | Annual product. Formazin nephelometric units. Download values are FNU × 10. Maximum detectable value stated as 100 FNU. Shallow-water algorithm cited as Li et al. 2022; optically deep water uses Dogliotti et al. 2015. | A bleaching effect size. |
| Imagery | Temporal composites, predominantly 2018–2020 PlanetScope, with Sentinel-2 used for depth. | A monitoring time series at survey frequency. |

FAQ: overall map accuracy is between 60% and 90% and varies by region. Accuracy depends on habitat complexity, depth, turbidity, the mosaic, the derived depth, and the reference set. Maps are for whole reef systems, not a substitute for a local survey. Highly turbid or optically deep areas are excluded or poorly constrained.

Update frequency of the habitat maps after v2 was not established (`UNKNOWN`). Access: Atlas portal downloads and the Earth Engine asset named above. Licence text was not copied (`UNKNOWN`).

Allen products are spatial context and, for turbidity and satellite depth, environmental layers. They are not NOAA thermal products and not ground-truth bleaching surveys.

Phase 7.4 keeps the reef mask, benthic class, geomorphic zone, satellite depth, and turbidity as `CONTEXT_ONLY`. None of them is a derived local indicator (`docs/40-phase7.4-spot-scientific-baseline.md`).

On 2026-10-01 the methods page responded and no raster was retrieved (`docs/41-phase7.5-real-scientific-data-acquisition.md`).

A later unauthenticated WFS request stored benthic and geomorphic class names for a small bbox. Checksums, the service CRS, and a repeat of that request are in `docs/43-phase7.5.2-allen-provenance-metadata-reproducibility.md`. Bathymetry, turbidity, and the reef mask were not on that WFS. A map class is not a field identification of the spot (`docs/44-phase7.6-spatial-association-spot-mapping.md`). The website package download was not automated (`docs/42-phase7.5.1-allen-automated-access-test.md`).
