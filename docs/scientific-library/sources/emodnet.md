# EMODnet — product note

Provider: European Marine Observation and Data Network.

Pages read:

- Bathymetry: https://emodnet.ec.europa.eu/en/bathymetry
- EUSeaMap story map: https://emodnet.ec.europa.eu/en/euseamap-evolution-2012-2023-storymap
- Seabed Habitats Phase IV note: https://emodnet.ec.europa.eu/en/node/49113
- Physics: https://emodnet.ec.europa.eu/en/physics
- EUSeaMap 2023 technical report (Ifremer): https://archimer.ifremer.fr/doc/00859/97116/105963.pdf

## What is actually documented

**Bathymetry DTM, 2024 release.** Grid 1/16 arc minute. Coverage listed by EMODnet: Greater North Sea, English Channel, Celtic Seas, western and central Mediterranean, Iberian coast and Bay of Biscay, Adriatic, Aegean–Levantine, Madeira and Azores, Baltic, Black Sea, Norwegian and Icelandic seas, Canary Islands, European Arctic and Barents Sea. A separate world base layer is assembled with GEBCO and other DEMs where the European DTM does not apply. That world layer is not the same product as the European DTM. CRS of the 2024 grid was not confirmed on the page read (`UNKNOWN`).

**EUSeaMap 2023.** Broad-scale predictive seabed habitat map. European sea basins, plus the Caspian and some EU jurisdictions in the Caribbean named by the project (Anguilla, Sint Maarten, Guadeloupe, Martinique). Inputs cited by EMODnet include EMODnet Bathymetry, Geology, and Copernicus Marine model outputs such as bottom currents. Resolution in the 2023 report is described as about 100 m where the EMODnet bathymetry DTM is used, with GEBCO filling gaps. This is not a global coral-reef habitat map.

**Physics.** In situ series and profiles: temperature, salinity, currents, sea level, waves, wind, light attenuation, underwater noise, river flow, sea ice. Aggregation with Copernicus Marine In Situ TAC, SeaDataNet, and global programmes (Argo, OceanSITES, DBCP, and others). There is no statement that this is a gap-free temperature grid on tropical reefs. Whether a given reef has a nearby series is `UNKNOWN` until a station catalogue is queried. Licence: the Physics catalogue entry describes open access; the exact licence text was not copied (`UNKNOWN` per dataset).

**Chemistry, biology, geology.** Thematic portals exist. This registry does not claim a specific coral-bleaching variable from them. Status: `UNKNOWN` until a product record is opened. No concentration, species list, or current speed was invented.

## Consequence for coral bleaching

EMODnet is a useful source for European seas and for the named Caribbean territories in EUSeaMap. It is `NOT_AVAILABLE` as a global reef thermal product. It does not replace NOAA CRW for SST, HotSpot, or DHW. Indo-Pacific reefs are outside the European DTM footprint described above.

Phase 7.4 classifies bathymetry, EUSeaMap, and physics series as context only. Outside a footprint the association is `NOT_AVAILABLE`, not a filled value (`docs/40-phase7.4-spot-scientific-baseline.md`).

On 2026-10-01 the bathymetry WMS returned GetCapabilities. No depth was read for the CRW demonstration cell, which lies outside the European DTM footprint. A missing depth is a coverage gap, not a zero (`docs/44-phase7.6-spatial-association-spot-mapping.md`).
