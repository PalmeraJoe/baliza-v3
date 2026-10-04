# MERMAID — field observations

Operator: Wildlife Conservation Society. Service: datamermaid.org.

Pages read on 30 September 2026:

- Terms of Service: https://datamermaid.org/terms-of-service
- Data sharing: https://datamermaid.org/documentation/collect-project-data-sharing
- Survey methods: https://datamermaid.org/documentation/collect-survey-methods
- Bleaching entry: https://datamermaid.org/documentation/collect-bleaching-data
- Benthic entry: https://datamermaid.org/documentation/collect-benthic-data
- Fish belt: https://datamermaid.org/documentation/collect-fish-data
- Habitat complexity: https://datamermaid.org/documentation/collect-habitat-complexity-data
- Sample unit: https://datamermaid.org/documentation/collect-sample-unit
- API guide: https://datamermaid.org/documentation/mermaid-api
- API reference: https://mermaid-api.readthedocs.io/en/latest/projects.html and https://mermaid-api.readthedocs.io/en/latest/aggregated.html

Production API root stated by MERMAID: `https://api.datamermaid.org/v1/`.

MERMAID is a project-based store of field surveys. It is not a gap-free global grid. A site exists where a project submitted one. Country, site name, latitude, and longitude are public metadata. That is not the same as worldwide coverage. The start and end of the whole archive were not established in this pass (`UNKNOWN`).

## What a sample is

A sample unit is one method at one site on one date. Documented methods:

| Method | What is recorded | Stated calculation |
|--------|------------------|--------------------|
| Fish belt | Count and size by species, genus, or family on a belt of stated length and width | Biomass (kg/ha) and abundance. Length–weight coefficients from FishBase. Method cited by MERMAID as Ahmadia et al. 2013. |
| Benthic PIT | Attribute at a fixed interval | Percent cover of top-level benthic groups. Ahmadia et al. 2013, as cited by MERMAID. |
| Benthic LIT | Continuous segments and lengths | Percent cover. Loya 1972, as cited by MERMAID. |
| Benthic photo quadrat | Points on quadrats | Percent cover of the same top-level groups. |
| Habitat complexity | Visual score 0–5 per interval | Average score. Wilson et al. 2007 and Darling et al. 2017, as cited by MERMAID. |
| Bleaching quadrats | Colonies by genus and bleaching category; percent cover of hard coral, soft coral, and macroalgae per quadrat | Counts, percent normal, pale, and bleached colonies, and average covers. Protocol cited by MERMAID as McClanahan and Darling. |
| Macroinvertebrate belt | Name, size, count | Named on the sample-unit page. Density formula was not copied here. |

Bleaching categories on the collect page: normal, pale, 0–20% bleached, 21–50%, 51–80%, 81–100% bleached, and recently dead. Recently dead is a colony category in that survey. It is not a later mortality percentage.

Depth in metres is a transect field on the fish, benthic, and habitat-complexity forms. Bleaching forms require site and transect attributes; a separate depth field on that form was not confirmed (`UNKNOWN` for bleaching depth). CRS of latitude/longitude was not stated (`UNKNOWN`).

Optional context on several forms: time, visibility, current, tide, notes. These are not SST, HotSpot, or DHW.

## Access and quality

Each method has its own policy: Private, Public summary (the default), or Public.

- Private: observations and site summaries stay private. Project, protocol, and site metadata, including location and sample-unit counts, are public.
- Public summary: site-level summaries are public. Individual observations are not.
- Public: observations are public.

Unauthenticated reads follow that policy. Summary endpoints expose site and date aggregates when the policy is public summary or public. Observation-level ground truth is available to the public only where the policy is Public, and to project members when they are authenticated.

The terms say other users' content is provided "as is", without warranty or verification. Project administrators are named. A `suggested_citation` field is part of the exported columns described by the R client; treat citation text as project metadata, not as a BALIZA quality score.

Images are a separate rule. The terms say photos may be stripped of EXIF, including location and date, and that stripped images may be used by anyone for lawful purposes, including model training. That clause is about images. It is not a licence to train on private tabular surveys.

There is no Creative Commons label on the terms page that was read. Use is governed by the Terms of Service and the per-project policy. API keys are required for authenticated calls. Scraping and resale of API access are prohibited. Attribution to MERMAID is required when API data are reused.

## Availability for BALIZA variables

| Variable | Status | Why |
|----------|--------|-----|
| Hard / soft coral and macroalgae percent cover | PARTIAL | Calculated from PIT, LIT, photo quadrats, and bleaching quadrats. Public only under the method's policy. Not ingested. |
| Benthic attribute and growth form | PARTIAL | Recorded on benthic methods. Not the Allen class list. |
| Coral genus on bleaching surveys | PARTIAL | Genus-level colony counts. Not a full species inventory. |
| Bleaching categories and percent bleached colonies | PARTIAL | Field observation when a bleaching sample exists and the policy allows the row. Not a NOAA product. |
| Recently dead colonies | PARTIAL | One bleaching category. Not `mortality_percentage`. |
| Fish counts, size, biomass, trophic group | PARTIAL | Fish belt. Not a coral-vulnerability score. |
| Habitat complexity 0–5 | PARTIAL | Visual score. Not rugosity from a DTM. |
| Site id, name, country, latitude, longitude, reef type, reef zone, exposure | PARTIAL | Metadata. Coverage is the set of submitted sites, not the ocean. |
| Sample date | PARTIAL | One clock per sample event. Archive span `UNKNOWN`. |
| Transect depth (m) | PARTIAL | On the fish, benthic, and habitat forms. |
| Visibility, current, tide | PARTIAL | Optional covariates. Not a thermal product. |
| Disease prevalence | NOT_AVAILABLE | Not in the method pages read. |
| Species richness as its own metric | UNKNOWN | Taxa are recorded. A richness product was not verified. |
| Thermal SST, HotSpot, DHW | NOT_AVAILABLE | Not MERMAID products. |
| A gap-free global ecological layer | NOT_AVAILABLE | Projects and policies leave holes. |

MERMAID rows are field observations or summaries of them. They are not BALIZA alerts, not predictions, and not thresholds. NOAA DHW is not assumed to predict a MERMAID bleaching percent.

Phase 7.4 uses an exposed bleaching row as a direct observation and as validation material, not as a predictor. Recently dead stays a survey category (`docs/40-phase7.4-spot-scientific-baseline.md`).

On 2026-10-01 an unauthenticated client received HTTP 401 for sites and an empty project list. No survey row was stored. A MERMAID site that is not this spot is not this spot's measurement (`docs/44-phase7.6-spatial-association-spot-mapping.md`).

A later read the same day, recorded in `docs/47-phase7.6.3-mermaid-real-data-verification.md`, got HTTP 200 from `summarysampleevents`. The unauthenticated Australia page contained 45 events and no coordinate equal to the heritage point. `/sites/` remained 401. That is an access gap for the spot, not a global absence.
