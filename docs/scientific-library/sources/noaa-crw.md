# NOAA Coral Reef Watch — product note

Provider: NOAA Coral Reef Watch (CRW), NESDIS.

Primary pages read:

- Daily global 5 km suite, Version 3.1: https://coralreefwatch.noaa.gov/product/5km/index.php
- Methodology: https://coralreefwatch.noaa.gov/product/5km/methodology.php
- ERDDAP access note (3 April 2024): https://www.coralreefwatch.noaa.gov/instructions/Accessing_Coral_Reef_Watch_Data_via_Data_Servers_at_CoastWatch_20240403.pdf
- Method paper: Skirving et al., Remote Sensing 12, 3856 (2020), https://doi.org/10.3390/rs12233856

## Suite

Version 3.1, released 1 August 2018. Grid 0.05 degree (stated as 5 km). Daily. Global. Record described as 1 January 1985 to present. Recent grids are usually available about one day behind UTC. Formats stated by CRW: NetCDF4 via FTP, HTTP, THREDDS, and ERDDAP; preview images; Google Earth. Licence: free download; a specific legal licence name was not copied here (`UNKNOWN`).

Pixel centers run from longitude −179.975 to 179.975 (7200 pixels) and latitude 89.975 to −89.975 (3600 pixels), per the 2024 ERDDAP note. The EPSG code was not stated on the pages read (`UNKNOWN`). Do not assume a CRS until the file metadata is read.

## Products in v3.1

| Product | Unit / type | Role for BALIZA |
|---------|-------------|-----------------|
| CoralTemp SST | °C, nighttime SST calibrated to 0.2 m | External observation of sea-surface temperature. Not reef-water temperature at depth. |
| SST anomaly | °C, SST minus a daily climatology | External observation. Not HotSpot. |
| Coral Bleaching HotSpot | °C, SST − MMM, negative values set to 0 | External observation of warm-season exceedance. |
| Degree Heating Week | °C-weeks | External observation of accumulated HotSpot. |
| Bleaching Alert Area, single-day and 7-day maximum | Categorical CRW classes | External evidence. Not a BALIZA Alert. |
| 7-day SST trend | °C over 7 days, with a stated significance test | External observation. |
| Monthly / annual / year-to-date composites | Same variables | Derived CRW products, not local surveys. |
| Regional Virtual Stations | 214 regions; values taken from the pixel of the daily 90th-percentile HotSpot, plus a 20 km buffer | Regional summary. Not a BALIZA Station. |
| Four-month outlook, via the virtual-station pages | Prediction, up to eight weeks shown on those pages | Not an observation. Not used on the BALIZA critical path. |

Climatology used by the heat-stress products: monthly means for 1985–2012, adjusted to 1988.2857, then the maximum monthly mean (MMM). The SST anomaly uses a daily climatology linearly interpolated from those monthly means, with the monthly mean placed on the 15th. This is CRW's method (Skirving et al. 2020), not a BALIZA threshold.

HotSpot: `HS = SST − MMM` when positive, else 0.

DHW: sum, over 84 days, of HotSpot values that are at least 1 °C, each divided by 7. Unit °C-weeks.

CRW's Bleaching Alert Area classes, as published on the methodology page, use HotSpot and DHW bands (No Stress through Alert Level 5) and attach mortality-risk wording. Those bands are CRW product semantics. They are not BALIZA `RuleVersion`s. CRW itself says the single-day alert layer does not consistently identify harmful stress in variable locations, which is why the 7-day maximum exists.

CoralTemp merges OSTIA reanalysis (1985 to November 2002), Geo-Polar reanalysis (November 2002 to October 2016), and near-real-time Geo-Polar SST (October 2016 onward). The 1985–2002 segment has lower data density. Nighttime SST reduces diurnal warming; it is still a surface foundation temperature, not a measurement on a colony.

Heritage 50 km twice-weekly products were retired from near-real-time updates on 30 April 2020. Archives remain. Do not mix 50 km and 5 km series without recording the version.

Phase 7.4 uses these grids only as external indicators associated with a spot. They are not local SST, local HotSpot, or local DHW, and Bleaching Alert Area is not a BALIZA alert (`docs/40-phase7.4-spot-scientific-baseline.md`).

On 2026-10-01, CoastWatch ERDDAP served six of these products for one cell. Two anomaly datasets differed. The HotSpot value was negative. The 7-day trend, single-day Bleaching Alert Area, and MMM grid were not in that dataset list. Details and checksums: `docs/41-phase7.5-real-scientific-data-acquisition.md`.

Phase 7.6 does not turn a cell that contains a coordinate into a local HotSpot. A boundary point is not given one of the adjacent cells, and the grid CRS remains unknown (`docs/44-phase7.6-spatial-association-spot-mapping.md`).
