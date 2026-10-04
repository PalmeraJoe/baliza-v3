# 33 — Open scientific questions

These are unanswered. They are not filled with estimates.

1. Which covariates actually improve local temperature over the NOAA pixel, on held-out stations? The exact target of a future temperature model stays OPEN.
2. What spatial resolution is defensible for a management unit: 5 km, 10 m, or the transect?
3. Which depth variable matters: diver depth, Allen relative depth, or the European DTM?
4. Which biodiversity measures have evidence as vulnerability rather than as concurrent description?
5. Is vulnerability a taxon trait, a history, a habitat class, or something else? No choice is made.
6. Which mapped layers are only context?
7. How would acclimatization be measured without assuming that prior bleaching protects? One GBR result points the other way.
8. How should pixel-scale and survey-scale uncertainty be shown together without a fake confidence number?
9. Which associations in a future model are correlation only?
10. Is the validation outcome bleaching percent, mortality after a fixed interval, or both?
11. For which reefs does EMODnet Physics have a usable historical series?
12. What is the CRS and vertical datum of each grid?
13. What licence applies to each NOAA, EMODnet, and Allen file we would store?
14. Does annual turbidity say anything about the survey week?
15. What event definition, if any, should count as stress frequency? None is adopted.
16. Which MERMAID projects and policies actually cover a future BALIZA site? The platform does not answer that until those projects are queried.
17. What, if anything, may be calibrated at a site? No method, weight, or correction factor is chosen. Calibration rows must stay out of the independent validation set.
18. Which spatial unit blocks a future holdout? Reef, zone, site, station, transect, or another group that the tables actually support. Not chosen.
19. What uncertainty method and what applicability boundary would a future estimate use? Not chosen. Until they are, training is not authorised (`docs/37-phase7.1-ml-validation-protocol.md`).
20. Is a Spot the same object as a Zone, a subdivision of a Zone, or a declared group of stations? Not chosen (`docs/38-phase7.2-scientific-target-and-spot-resolution.md`).
21. Which variable, if any, is the first downscaling target, and which in-situ series is its ground truth? Not chosen. Local temperature and bleaching percentage are not assumed.
22. Where are the boundaries between a valid estimate, high uncertainty, insufficient data, and abstention? No numeric cutoff is set.
23. Which age, per source, separates stale, recent, and current data? Not set (`docs/39-phase7.3-spot-intelligence-evidence-state-model.md`).
24. When is evidence for a spot complete, partial, or insufficient? Not set. Empty evidence is not a normal state.
25. Which published state names and playbook entry conditions, if any, should exist? The names in the Phase 7.3 matrix are illustrations. None are adopted.
26. What age separates current, recent, and stale for each source? Not set. A duration may be shown; the class may not (`docs/40-phase7.4-spot-scientific-baseline.md`).
27. Which versioned rule, if any, may treat NOAA HotSpot or DHW as a BALIZA alert input? None is adopted. The cell is not the spot.
28. Are the two ERDDAP SST-anomaly datasets interchangeable? A retrieved cell returned 0.78 and 0.4 on the same day. They stay separate (`docs/41-phase7.5-real-scientific-data-acquisition.md`).
29. Why was the retrieved HotSpot negative while the methodology page clips at zero? The value is kept. It is not clipped here.
