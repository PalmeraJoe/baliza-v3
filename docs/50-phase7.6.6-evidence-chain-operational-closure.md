# 50 — Phase 7.6.6 evidence chain operational closure

This pass does not acquire new data. It re-reads the files audited in `docs/49-phase7.6.5-evidence-chain-real-dataset-audit.md` and closes a category only when those files demonstrate it. The manifest is `docs/scientific-library/audit/phase-7.6.6-evidence-chain-manifest.json`. `generated_at` is `UNKNOWN` because no separate audit clock was stored. The code is `src/baliza/experimental/phase766/closure.py`.

## What closed

Raw traceability is closed for the files on disk. Each NOAA CSV, Allen JSON, and Allen XML file has a path, a byte size, and a SHA-256 computed by BALIZA. A missing dataset is `NOT_AVAILABLE`. That is not the same fact as a file whose provenance is incomplete.

Checksum traceability is closed for those same files. The six NOAA CSV checksums and the three Allen JSON checksums match the values stored at acquisition. The three Allen XML files had no stored checksum. They are hashed now, the origin is `BALIZA_COMPUTED`, and the comparison is `NOT_AVAILABLE`. The old provenance file was not rewritten. Metadata `info.json` files are hashed the same way. No checksum of a derived spot record is presented as a raw checksum.

The NOAA product remains a NOAA product. BALIZA parsed it. That separation stays closed.

## What stays partial, and why

NOAA product version `3.1` is the `product_version` attribute in the stored ERDDAP info file. Allen feature files do not state a version, so source, product, and version together stay partial.

NOAA retrieval is the calendar date `2026-10-01` plus the stored endpoint and request. The grid time `2026-09-26T12:00:00Z` is not that retrieval and is not an observation time. CRS is unknown, so the four cell centers stay four external associations and the spatial link stays unknown. One cell has a value. Three do not. There is no average.

The parse module is known. The time it ran is not stored, so the transformation chain stays partial. Original CSV units are unchanged and no conversion was applied. Allen has no unit.

Source quality is unknown except HotSpot, which stays BALIZA `QUESTIONABLE`. Association quality is unknown. There is no quality score. Freshness stays `UNKNOWN` because no versioned policy exists. Uncertainty stays `UNKNOWN`, not zero. Model uncertainty is not applicable. Individual chains are partial, and the EMODnet chain is broken because no file exists.

Allen classes are present in the benthic extract, including Coral/Algae. None is attached to the spot. Geometry is null. Epoch is unknown. The extract is not a field observation and not a measured value.

MERMAID official access stays partial. Summary sample-event access is available. Site access is partial. Spatial and temporal compatibility stay `UNKNOWN`. That is not `NO_COMPATIBLE_RECORD`. The count 16557 is not a count of observations of this spot. The response body was not stored, so that body is not reproducible. Local checksums and the CSV parse are reproducible. The providers were not called again.

EMODnet and resort data stay `NOT_AVAILABLE`. Resort history is not base-model training.

## Verdict

PHASE 7.6.6 EVIDENCE CHAIN OPERATIONAL CLOSURE — SCIENTIFIC ESTIMATION / DOWNSCALING / ML NOT AUTHORIZED.

Whether any of these files can support a local estimate is decided in `docs/51-phase7.7-scientific-target-ground-truth-applicability.md`. They cannot.
