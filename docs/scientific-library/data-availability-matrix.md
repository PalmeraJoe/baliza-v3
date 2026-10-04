# Data availability

States: `AVAILABLE`, `PARTIAL`, `UNKNOWN`, `INSUFFICIENT`, `NOT_AVAILABLE`.

`INSUFFICIENT` means a product exists but does not meet a station-scale bleaching use without more data. No product is marked `INSUFFICIENT` unless that judgment follows from the source note. Where the judgment would be a guess, the cell stays `UNKNOWN`.

| Variable | Evidence | Best current source | History | Local | Quality known | ML suitability | RBM suitability | Gap |
|----------|----------|---------------------|---------|-------|---------------|----------------|-----------------|-----|
| SST, anomaly, HotSpot, DHW, MMM | Method paper plus CRW page | NOAA v3.1 | 1985–present | NOT_AVAILABLE | Surface, gap-filled, versioned | Feature candidate only | Hazard candidate only | Pixel is ~5 km; not colony temperature |
| Alert area | CRW definition | NOAA v3.1 | same | NOT_AVAILABLE | Categorical product | Not suitable (double count) | Not suitable as a state | Must stay external evidence |
| Allen habitat, extent | Atlas methods | ACA v2 | 2018–2020 epoch | NOT_AVAILABLE | 60–90% by region | Context feature candidate | Context or exposure | Not a time series of cover |
| Turbidity | Atlas methods | ACA annual | annual | NOT_AVAILABLE | Cap 100 FNU; ×10 storage | Context candidate | Context only | Does not match survey week |
| EMODnet bathymetry | EMODnet page | 2024 DTM | static release | NOT_AVAILABLE | European seas only | Context inside footprint | Context | Indo-Pacific gap |
| EUSeaMap | 2023 report | EMODnet | 2023 map | NOT_AVAILABLE | Predictive broad-scale | Context inside footprint | Context | Not global reefs |
| Physics series | Catalogue | EMODnet Physics | series-specific | NOT_AVAILABLE | UNKNOWN at reefs | UNKNOWN | UNKNOWN | No reef inventory yet |
| Cover, richness, bleaching %, mortality, disease, local depth | Not opened | none | none | NOT_AVAILABLE | none | Not usable | Not usable | Ground truth absent |
| Downscaled temperature | none | none | none | NOT_AVAILABLE | n/a | Target of a future model | Do not feed RBM until validated | Model does not exist |

Missingness for every local biological variable is total in the current system of record.
