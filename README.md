# AI Insights from SAR for Mission-Critical Communications

A technical, source-backed guide to generating Synthetic Aperture Radar (SAR) products and continuously converting them into actionable intelligence for mission-critical communication networks and services.

**Status:** Research and proposed reference architecture, not an implemented or certified operational system. Source review: 16 November 2026. Technical capabilities are distinguished below from proposed telecom integrations; numerical examples and service objectives are illustrative, not provider guarantees.

## 1. What is possible, and what is not?

SAR is an active microwave imaging technology. It can observe the Earth's surface at night and through most cloud cover, providing evidence about flooding, surface change, and ground movement. Weather, vegetation, acquisition geometry, and radar wavelength still affect interpretation. SAR does not directly measure whether a radio site, fiber, power supply, or mission-critical application is working. [1][2]

The useful transformation is:

```text
SAR observation -> physical hazard evidence -> exposed network assets
                -> service dependency analysis -> prioritized operational action
```

For example: "Newly observed water overlaps the access road and compound of a site supporting emergency-service coverage; the alternate backhaul shares the same flood corridor. Verify power and accessibility, then prepare a deployable site."

**Three essential distinctions:**

| Term | What can realistically be delivered |
|---|---|
| Continuous processing | A service that watches for new data and processes every eligible observation, including delayed or revised products. |
| Real-time insight | Low-latency updates after data becomes available, and faster re-evaluation using live network/weather feeds between satellite observations. This is not continuous satellite observation. |
| Deterministic insight | Repeatable computation and explicit, versioned decision rules under a qualified execution environment. This does not make an AI prediction certain or guarantee hard real-time deadlines. |

Satellite revisit, scene availability, processing latency, and network reaction time are different constraints. A pipeline cannot recover an event that occurs and disappears between usable observations. CEMS Rapid Mapping is an example of acquisition-dependent emergency mapping, not a live video feed. [3]

## 2. Valuable AI-led insights for communications

These are **proposed operator workflows** built on established SAR capabilities. They are not claims of a deployed, standardized SAR-to-MCX interface.

| Insight | SAR evidence and possible AI | Additional information required | Operational use and limitation |
|---|---|---|---|
| Flood exposure of sites and exchanges | Water segmentation; pre/post backscatter change; temporal change models | Site footprints, equipment elevation, drainage, permanent-water baseline, power telemetry | Rank inspections, protect power, stage portable coverage. Water near a site does not prove outage or equipment inundation. |
| Common-cause backhaul risk | Hazard intersections across routes and facilities | Actual fiber/microwave topology, shared ducts, leased routes, protection groups | Identify primary and backup paths exposed to the same event. Logical redundancy alone does not establish physical diversity. |
| Slow ground movement near towers, ducts, or shelters | InSAR time series; anomaly detection on displacement trends | Geotechnical assessment, foundation design, GNSS, maintenance history | Prioritize engineering surveys. Radar line-of-sight movement is not automatically vertical subsidence or structural damage. |
| Landslide or earthquake impact screening | Backscatter/coherence change; terrain-aware change classification | DEM, slope inventory, rainfall/seismic reports, field observations | Flag slopes and corridors for inspection. Decorrelation is not a unique landslide/damage signature. |
| Access and restoration planning | Flood polygons and change maps | Road topology, bridge status, water depth/flow, vehicle constraints, responder reports | Identify potentially blocked approaches and staging areas. An unflagged route must not be described as safe. |
| Mission-critical service exposure | Hazard-to-asset joins, graph analytics, calibrated outage-risk models where labels exist | Coverage predictions, live counters, MCX platform dependencies, dispatch priorities | Prioritize MCPTT, MCVideo, and MCData continuity. SAR does not observe call setup, application availability, or radio QoS. |
| Deployable asset placement | Hazard-aware spatial optimization | Terrain, RF planning, power/fuel, permissions, backhaul and transport access | Recommend candidate locations for cells-on-wheels or portable backhaul. Perform RF and operational validation before deployment. |
| Long-term resilience investment | Historical hazard frequency and displacement trends | Incident/loss records, service criticality, engineering costs | Compare hardening, relocation, and diverse routing. Historical exposure is not a guarantee of future event probability. |

3GPP defines mission-critical services and their common/service-specific requirements; this guide uses that context rather than asserting that 3GPP requires SAR integration. Deliver recommendations to authorized operations or dispatch systems through supported interfaces, outside latency-sensitive voice/media paths. [4]

## 3. How SAR data is generated

### 3.1 Physical measurement

A side-looking radar transmits microwave pulses while a satellite or aircraft moves along its track. The receiver records echoes from many surface scatterers. Travel time determines slant range; coherent observations from successive platform positions synthesize a much larger antenna aperture.

**Synthetic aperture does not mean AI-generated or simulated data.** Operational SAR images are derived from measured electromagnetic echoes.

| Parameter | Technical meaning and downstream consequence |
|---|---|
| Frequency and wavelength | Related by `lambda = c / f`. X-, C-, and L-band systems respond differently to surface roughness, vegetation, moisture, and structure. Longer wavelength does not imply unrestricted penetration. |
| Polarization | HH, HV, VH, VV describe transmit then receive orientation. Match model channels to the actual sensor product; dual-polarization is not full polarimetry. |
| Look/incidence angle | Controls scattering and terrain geometry. Local incidence angle also depends on slope. Compare compatible geometries or explicitly account for their differences. |
| Orbit and viewing direction | Ascending/descending acquisitions observe different line-of-sight components. Orbit state vectors and timing are required for accurate focusing/geolocation. |
| Pulse bandwidth and duration | A frequency-modulated chirp supports pulse compression: long transmitted energy with fine range discrimination. |
| Pulse repetition frequency (PRF) | Controls along-track sampling and interacts with Doppler and range ambiguities, swath, antenna design, and acquisition mode. |
| Sampling rate and quantization | Determine sampled echo representation and data volume. Sampling more finely does not by itself improve physical resolution. |
| Acquisition mode | Stripmap, spotlight, and ScanSAR/TOPS trade swath, resolution, and dwell time. Mode compatibility matters for time series. |
| Calibration and noise | Antenna patterns, instrument response, thermal noise, and calibration information affect quantitative backscatter. |

SAR is not an ordinary photograph: bright pixels indicate strong radar return, not necessarily buildings; dark pixels can indicate smooth water, radar shadow, or other low-return surfaces. Speckle arises from coherent interference within a resolution cell. [1][2]

### 3.2 Echoes to a focused image

```text
Acquisition plan and radar configuration
    -> chirp transmission and surface scattering
    -> coherent receiver and digitization
    -> downlink, packet decoding, timing/orbit/calibration association
    -> Level-0 echo product
    -> range compression and azimuth focusing
    -> phase-preserving SLC
         |-> detection + multilooking + ground-range projection -> GRD
         |-> calibration + geocoding + radiometric terrain correction -> RTC
         `-> compatible SLC stack -> interferometry -> displacement products
```

This is a conceptual chain, not one universal processor graph: providers can generate GRD and other products through dedicated branches. Many users should start with validated Level-1 or analysis-ready products rather than rebuilding the raw-data processor.

1. **Acquire and decode echoes.** Record complex in-phase/quadrature samples, acquisition timing, sensor configuration, and orbit information. The range direction is sampled in fast time; successive pulses form slow time along track. Level-0 packaging and quantization are mission-specific.
2. **Range compression.** Apply a matched filter based on the transmitted chirp to localize scatterers in slant range.
3. **Motion and geometry compensation.** Use platform trajectory, timing, Doppler information, and the relevant Earth/terrain model. Airborne systems also require suitable motion compensation.
4. **Azimuth focusing.** Combine phase histories across platform positions, handling range-cell migration and Doppler effects. Range-Doppler, chirp-scaling, omega-k, and backprojection are alternative image-formation approaches, not mandatory consecutive stages.
5. **Produce SLC.** Preserve complex amplitude and phase in the radar image geometry. Verify impulse response, radiometry, geolocation, noise, and burst consistency against mission specifications.
6. **Generate application products.** Detect and multilook for intensity products; calibrate, terrain-correct, and geocode as appropriate; retain phase-preserving inputs for InSAR.

NASA's imaging-basics chapter, SAR Handbook, and Copernicus product documentation provide the underlying theory and mission-specific detail. [1][2][5]

### 3.3 Essential equations and interpretation

For a simplified monostatic system, with `c` the speed of light:

| Quantity | Relationship | Qualification |
|---|---|---|
| Slant range | `R = c * tau / 2` | `tau` is the round-trip propagation time; precise processing also needs timing and propagation corrections. |
| Ideal slant-range resolution | `delta_r ~= c / (2 * B)` | `B` is processed bandwidth. Weighting and processing can broaden resolution. |
| Approximate ground-range resolution | `delta_gr ~= delta_r / sin(theta)` | Flat-ground approximation; local terrain changes the geometry. |
| Ideal broadside stripmap azimuth resolution | `delta_az ~= L_a / 2` | Ideal focused stripmap case, not a universal formula for TOPS/spotlight products. |
| Complex image sample | `z = I + jQ = A * exp(j * phi)` | Amplitude `A = abs(z)`; intensity `P = abs(z)^2`. |
| Power/backscatter in decibels | `P_dB = 10 * log10(P_linear)` | Equivalent to `20 * log10(A)` with a consistent reference. Mask invalid values; do not log complex data or apply log twice. |
| Interferogram | `z1 * conjugate(z2)` | Requires precisely co-registered compatible SLCs. |
| Coherence estimate | `abs(sum(z1 * conjugate(z2))) / sqrt(sum(abs(z1)^2) * sum(abs(z2)^2))` | Computed over a defined window with valid power; depends on window, noise, geometry, and scene stability. |
| Displacement magnitude from corrected phase | `abs(d_LOS) = lambda * abs(delta_phi_deformation) / (4 * pi)` | Use unwrapped deformation phase, not raw total phase. Signed conversion depends on interferogram/processor convention. |

For intuition, `B = 20 MHz` gives about `7.5 m` ideal slant-range resolution. At wavelength `5.6 cm`, one `2*pi` deformation-phase cycle corresponds to `2.8 cm` line-of-sight displacement magnitude. Neither example guarantees achieved accuracy.

**Pixel spacing is not spatial resolution.** Resampling onto a 10 m grid does not create 10 m independent detail. Likewise, millimeter-scale displacement precision under favorable InSAR conditions is not millimeter-scale image resolution or guaranteed single-scene accuracy.

For approximate uncompressed complex-echo storage:

```text
bytes ~= pulse_count * range_samples_per_pulse * channel_count
         * 2 * bits_per_I_or_Q_sample / 8
```

The factor of two represents I and Q. Packet overhead, compression, metadata, temporary processing arrays, and derived products are additional; estimate from the actual acquisition rather than assuming a standard scene size.

### 3.4 Products, formats, and what each enables

| Product | Information retained | Typical use | Important restriction |
|---|---|---|---|
| Level-0 | Mission-specific echo data and associated metadata | Instrument/science processing and custom focusing | Specialized decoder, auxiliary data, calibration, and validated focusing are required. Not a normal flood-model input. |
| Level-1 SLC | Focused complex samples, amplitude and phase | Interferometry, coherence, phase-sensitive analysis | Requires compatible acquisition geometry and phase-aware processing. |
| Level-1 GRD | Detected, multilooked ground-range image; phase discarded | Backscatter change and flood segmentation | Not an interferometric phase product; ground-range projection is not equivalent to full terrain correction. |
| RTC backscatter | Calibrated, geocoded backscatter with topographic radiometric normalization | More consistent spatial/temporal backscatter analysis | Inspect normalization, units, DEM, masks, and geometry; RTC cannot restore information lost to shadow or layover. |
| Interferogram/coherence | Relative phase and local similarity between acquisitions | Deformation processing and change indicators | Coherence loss has multiple causes; wrapped phase alone is not displacement. |
| Displacement time series | Quality-controlled, referenced line-of-sight movement estimates | Slow deformation monitoring and engineering screening | Needs temporal context, reference definition, uncertainty, and geotechnical interpretation. |

Sentinel-1 products commonly use a SAFE package with measurement TIFFs, annotation, calibration, noise, and manifest information. Other missions use different conventions, including HDF5. Application outputs often use Cloud Optimized GeoTIFF (COG) for tiled rasters, GeoJSON/GeoPackage for vector results, and STAC for discovery and provenance. Preserve the authoritative source metadata rather than treating an exported TIFF as self-describing. [5][6]

For Sentinel-1, C-band center frequency is approximately 5.405 GHz. IW uses TOPS burst acquisition; the often-quoted roughly 5 m by 20 m IW resolution describes acquisition capability, not a universal output pixel size or all product resolutions. Check mode, product class, processing version, polarization, and actual metadata. Do not assume a fixed global revisit cadence from a nominal constellation configuration. [5][7]

### 3.5 Generating AI-ready backscatter

Use the processing steps appropriate to the exact source product; do not blindly repeat corrections already applied.

1. Select the area/time interval, polarization, relative orbit, acquisition mode, and compatible pre-event baseline.
2. Verify completeness, product version, checksum, annotation, orbit information, and processing quality flags.
3. Apply the relevant orbit updates, border/thermal-noise handling, and radiometric calibration through a validated processor.
4. Calibrate to the required backscatter convention, such as sigma-nought or gamma-nought. These conventions and RTC variants are not interchangeable without checking their definitions.
5. Apply DEM-based geometric terrain correction and, where required, radiometric terrain correction. These address different problems: map location versus topographic brightness effects.
6. Produce layover/shadow, no-data, water-baseline, and other relevant quality masks. Geocoding cannot reconstruct surfaces hidden by radar geometry.
7. Align dates to a common CRS/grid. Use a suitable projected CRS for distances/areas; geographic degrees are not meters. Preserve original acquisition geometry in metadata.
8. Use any speckle filtering consistently with model training. Filtering/multilooking changes statistics and can erase narrow roads or small features.
9. Convert to linear/dB representation exactly as required by the model. For power averages and ratios, explicitly choose and document the domain.
10. Normalize using training-derived parameters; tile with overlap/halos, retain valid-data masks, and define deterministic seam handling.
11. Export analysis-ready imagery plus a manifest recording units, polarization order, acquisition time, DEM, corrections, grid, processor version, and hashes.

**Training/serving parity matters:** a model trained on a particular GRD preprocessing chain must not be moved to RTC imagery without adaptation and evaluation. "Both are Sentinel-1" is not sufficient compatibility.

### 3.6 Generating InSAR displacement

Use a separate phase-preserving workflow, not the flood/intensity preprocessing branch:

1. Select compatible SLCs or an SLC stack: relative orbit, mode, burst overlap, polarization, and suitable temporal/perpendicular baselines.
2. Apply orbit/geometry information and precise co-registration. Sentinel-1 TOPS requires burst-aware alignment and stringent azimuth registration, commonly refined with Enhanced Spectral Diversity.
3. Generate interferograms and coherence; remove modeled flat-Earth and topographic contributions using orbit information and a DEM.
4. Apply suitable filtering and phase unwrapping, retaining connected components and low-coherence masks.
5. Address residual orbit, atmosphere, DEM error, and other sensor/propagation terms as required. A single interferogram cannot uniquely separate all these effects.
6. Invert a well-connected interferogram network for a referenced time series, using an appropriate small-baseline or persistent-scatterer approach.
7. Geocode and publish line-of-sight displacement, velocity, reference point/time, sign convention, uncertainty, and quality indicators.
8. Validate with GNSS, leveling, or other independent measurements where possible. Ascending/descending observations can constrain selected components under assumptions; they do not automatically provide full 3D motion.

One phase cycle represents an ambiguous displacement interval until unwrapped. Vegetation, rapid surface change, snow, long baselines, atmospheric delay, and poor reference stability can invalidate an estimate. Do not present low-coherence gaps as zero movement. ISCE and MintPy document practical processing and time-series workflows. [8][9]

## 4. Data sources and training datasets

| Source | Appropriate role | Selection cautions |
|---|---|---|
| Copernicus Sentinel-1 via Copernicus Data Space or ASF | Open SAR acquisition archive and operational scene discovery; GRD/SLC selection | Check current acquisition plan, coverage, mode, orbit, release latency, access quotas, and auxiliary-data availability. [5][7] |
| NASA OPERA RTC-S1 | Analysis-ready terrain-corrected backscatter | Check the specific collection's coverage, product version, units, masks, and delivery characteristics. [10] |
| NASA OPERA DSWx-S1 | Derived dynamic surface-water extent | Useful baseline or independent comparison where appropriate; not independent ground truth if derived from the same SAR input. Check class definitions and coverage. [10] |
| NASA OPERA CSLC-S1 / DISP-S1 | Co-registered complex data and displacement products | Coverage differs from other OPERA products. Inspect reference, uncertainty, cadence, and quality layers; do not assume globally available displacement. [10] |
| Sen1Floods11 | SAR flood-model training and benchmarking, including VV/VH imagery and hand/weak labels | Respect invalid pixels, label provenance, geography/event splits, preprocessing, license, and required citation. Benchmark results are not operational certification. [11] |
| SpaceNet 8 | Optical flood-affected roads/buildings and multimodal research | This is an optical-imagery benchmark, not a SAR training dataset. Do not treat its imagery as radar input. [12] |
| Operator GIS, alarms, performance counters, power and transport telemetry | Convert physical exposure into communication-service evidence | Validate inventory completeness, timestamps, route accuracy, access permissions, and actual service dependencies. |
| DEM, rainfall, gauges, weather alerts, GNSS and field reports | Terrain correction, interpretation, validation, and faster contextual updates | Record resolution, vertical datum where relevant, timing, uncertainty, license, and source reliability. |

Commercial taskable SAR or airborne collection can complement open archives where budgets and access permit, but tasking acceptance, geometry, downlink, coverage, and delivery must be contracted and measured. Do not advertise a tasking request as an immediate observation guarantee.

If simulated SAR is needed for research, model sensor geometry, scattering, motion, noise, and focusing, then document the simulator and synthetic-label assumptions. Simulation and augmentation can help robustness experiments; neither substitutes for independent real-event validation.

## 5. Step-by-step AI workflow

### Step 1: Define the operational decision

Start with a bounded question: "Which emergency-service sites and physically diverse backup routes are exposed to newly observed flooding?"

Define the area of interest, asset types, decision owner, acceptable false alarms/misses, maximum data age, required confidence/coverage, and permitted actions. Specify distinct deadlines for hazard mapping, asset-risk updates, and live network response.

### Step 2: Build the asset and service dependency model

Load sites, compounds, power dependencies, fiber routes, microwave links, access roads, exchanges, coverage predictions, and MCX application dependencies into a controlled geospatial store. Represent physical and service dependencies as a graph.

Use geometry and position uncertainty rather than unqualified point intersections. A buffer represents an exposure assumption, not a physical damage radius. A microwave link crossing a water polygon is not itself proof of attenuation or failure; evaluate endpoints, power, terrain clearance, and actual link telemetry.

### Step 3: Discover and ingest observations

Use provider catalog/search APIs, including STAC where offered. Store the original data immutably with checksums, metadata, licensing, and acquisition/publication/ingestion timestamps.

Validate AOI overlap, product type, polarization, relative orbit, usable coverage, and completeness. Route invalid or unsupported products to a visible quarantine queue with reasons; do not silently substitute an old or incompatible image.

### Step 4: Generate the correct analysis-ready product

Apply Section 3.5 for backscatter or Section 3.6 for displacement. Cache static DEMs, reference baselines, grids, and masks. Version processor configuration and auxiliary data so that a result can be reproduced.

### Step 5: Establish labels and independent baselines

For flooding, distinguish permanent water, event water, non-water, and unknown/invalid areas. Align imagery and labels in time and space. Weak labels from another model are not equivalent to verified observations.

For service-impact prediction, obtain time-aligned outage and cause records. Without representative labels, publish **physical exposure**, not a fabricated probability of service failure.

### Step 6: Develop models against simple alternatives

| Task | Start with | Add AI where justified | Key output |
|---|---|---|---|
| Open-water/flood mapping | Backscatter thresholding, pre/post change, terrain/permanent-water masks | U-Net/DeepLab-style segmentation; temporal or multimodal models | Water class probabilities, valid-data mask, uncertainty/abstention mask |
| Surface change screening | Intensity/coherence change statistics | Siamese or temporal change models | Candidate change regions, not automatic structural damage claims |
| Deformation anomaly detection | Robust trends and engineering thresholds on validated InSAR series | Time-series anomaly models | Movement trend, confidence/quality, change-point evidence |
| Service impact prioritization | Explicit exposure and dependency rules | Calibrated tabular/graph models if enough outage labels exist | Exposure rank or separately validated outage-risk estimate |

Train by held-out geography and event, with time-based separation where appropriate. Random neighboring tile splits can leak nearly identical scenes. Evaluate unseen terrain, seasons, sensor geometries, urban environments, and extreme events.

Use augmentations consistent with radar physics. Do not assume arbitrary intensity changes, rotations with geometry-sensitive channels, or phase alterations preserve the meaning of the input.

### Step 7: Validate accuracy and uncertainty

Measure flood-class precision, recall, and IoU on valid labeled pixels, with per-event/terrain breakdowns rather than only aggregate scores. For asset exposure, report missed exposed critical assets, false alerts per event/site, boundary/location sensitivity, and area with no usable observation.

Check calibration with reliability analysis and an appropriate score such as Brier score when probabilities are claimed. Evaluate out-of-distribution behavior and explicit abstention. Validate displacement against independent references and report uncertainty, not only model fit.

Evaluate the final action, not just pixel accuracy: did the workflow reveal a shared-risk backup route, reduce inspection delay, or improve restoration prioritization without unacceptable false actions?

### Step 8: Fuse hazards with network evidence

Intersect hazard polygons or uncertainty-aware raster summaries with asset footprints/routes. Propagate exposure through dependencies to affected coverage and services.

Keep distinct evidence states:

```text
SAR: physical exposure observed / not observed / unknown
Network telemetry: degraded / unavailable / normal / unknown
Operator assessment: unreviewed / verified / rejected
```

An illustrative rule is: raise an inspection recommendation when a fresh, quality-approved flood observation overlaps a site footprint; escalate restoration priority only using criticality, dependency exposure, and corroborating operational evidence.

"No exposure observed" is conditional on valid coverage and acquisition time, not proof of present safety. A priority score is not a calibrated probability unless separately validated.

### Step 9: Publish traceable recommendations

Produce versioned hazard layers, an asset-risk API/dashboard, and authorized notifications/tickets. Include the observation time, product age, uncertainty, quality, affected dependencies, rule/model versions, and reason for each recommendation.

An LLM may summarize these structured findings with source references. It must not invent coordinates, infer unobserved outages, or set safety-critical thresholds. The authoritative decision path should remain structured, auditable, and independently testable.

### Step 10: Close the learning loop

Capture operator dispositions, field measurements, actual failures, and restoration results. Monitor drift in model inputs, alert rates, calibration, and missed events. Retrain offline, validate on locked holdouts, shadow/canary the candidate, and promote only through approval with rollback.

Continuous data processing does not require continuous self-modifying models.

## 6. Continuous processing reference architecture

```text
                         SLOW / OBSERVATION-DRIVEN PATH
SAR catalog/notifications -> scheduled reconciliation -> immutable source store
                                                        |
                                                  durable work queue
                                                        |
                                           validate -> preprocess -> infer
                                                        |
                                              quality/uncertainty gate
                                                        |
                                            versioned hazard evidence store
                                                        |
                         FAST / EVENT-DRIVEN PATH         v
Network alarms / power / weather / gauges -> time-aware fusion + dependency graph
                                                        |
                                              deterministic policy engine
                                                        |
                                        alert API / NOC map / dispatch adapter
                                                        |
                                    authorized operator / approved runbook action
```

The slow path refreshes physical observations whenever a usable acquisition arrives. The fast path continuously re-evaluates service risk using the latest valid SAR context plus fresh telemetry. A new alarm can trigger immediate prioritization without pretending that the SAR scene has changed.

An illustrative stack could use object storage and STAC for discovery, a durable queue and workflow orchestrator, SNAP or OPERA processing for backscatter, ISCE/MintPy for interferometry, GDAL/Rasterio for geospatial operations, a qualified ML runtime, and PostGIS for spatial joins. Select components for the actual deployment and qualify them; this is not a packaged installation recipe. [6][8][9][13]

### 6.1 Reliability requirements

| Concern | Required behavior |
|---|---|
| Missing notifications | Reconcile the catalog on a bounded schedule; record last successful search and uncovered intervals. |
| Duplicate/revised products | Deduplicate by provider product identity and version/checksum. Include baseline, preprocessing, grid, model, and policy versions in processing identity. |
| Retries and partial failure | Use idempotent jobs, bounded retries, explicit failures, and a dead-letter/quarantine path with operator visibility. |
| Tile completeness | Stage outputs and publish a complete manifest atomically. If publishing partial coverage, label its exact footprint and unknown regions. |
| Late/out-of-order observations | Use acquisition time for ordering, retain revisions, and prevent an older result from silently replacing a newer applicable one. |
| Alert storms | Correlate by event/asset, use versioned hysteresis and deduplication, and retain an auditable alert lifecycle. |
| Data staleness | Apply use-case-specific TTLs and publish stale/unknown status. A failed refresh must not reset data age. |
| Overload | Use admission control, bounded queues, quotas, and visible deadline-miss status. Do not silently drop lower-priority coverage. |
| Provider/product revision | Reprocess affected evidence, link superseded decisions, and issue correction/retraction events where needed. |
| Infrastructure failure | Use tested restore/failover procedures, durable checkpoints, access-controlled backups, and monitoring of end-to-end health. |

## 7. Real-time latency: measure the entire chain

```text
event-to-alert latency =
    wait for a suitable observation
  + acquisition/downlink/product-publication delay
  + discovery/download delay
  + queue wait
  + preprocessing
  + inference
  + spatial fusion/policy evaluation
  + notification delivery
```

Some stages overlap, but measuring only inference time is misleading. Event onset can be unknown; in that case report acquisition-to-alert and publication-to-alert latency without calling either event-to-alert latency.

Record at least `acquired_at`, `provider_published_at` when available, `ingested_at`, `processing_started_at`, `processed_at`, and `alerted_at`, using UTC and synchronized clocks. For mosaics/time-series products, retain the contributing acquisition intervals rather than inventing a single instantaneous observation.

| Processing path | Example engineering objective, not a measured SLA | Constraint |
|---|---|---|
| Network-triggered risk re-evaluation | p95 within 5 seconds of accepted telemetry | Requires cached hazard evidence, bounded graph queries, capacity and dependency budgets; does not refresh the SAR observation. |
| New-scene flood processing | p95 within 15 minutes of complete supported input ingestion for a benchmarked AOI | Hardware, tiles, input size, storage, network, queueing, and quality review must be bounded and measured. |
| InSAR monitoring | Scheduled update after a usable acquisition/stack update | Requires coherent historical observations and heavier processing; not a substitute for live structural sensors. |
| Emergency map release | Provider/activation-specific | Acquisition opportunity, delivery, quality control, and human review remain outside local inference control. |

Choose freshness thresholds by application and actual collection schedule. For a rapidly evolving flood, an hours-old map may be unsuitable for access decisions even when it is the latest image available. Use gauges, weather forecasts, and field reports to bridge gaps, marking forecasts as forecasts rather than SAR observations.

Optimize safely: preprocess reference data, use AOI-based reads/COGs, cache model weights and static spatial indexes, preallocate capacity, process tiles in parallel, and profile CPU/GPU/I/O separately. Track p50/p95/p99, queue age, failure rate, deadline misses, and coverage completeness under realistic surge load.

## 8. What "deterministic" must mean operationally

| Dimension | Implementation requirement | Remaining limitation |
|---|---|---|
| Data determinism | Immutable inputs; pinned auxiliary data, baselines, grids, units and band order | Provider revisions and new observations are different inputs and must produce new versions. |
| Computational reproducibility | Pin model, preprocessing, runtime, libraries, drivers and qualified hardware; evaluation mode; seeds and deterministic kernels where supported | Identical seeds do not guarantee identical results across releases, platforms or CPU/GPU environments. [14] |
| Decision determinism | Versioned thresholds, freshness/quality gates, rounding, spatial tolerances, tie-breaking, temporal ordering and alert hysteresis | Repeatable rules can still be wrong if evidence or policy is wrong. |
| Temporal predictability | Bounded input sizes, admission, queues, resources, dependencies and timeouts; tested degraded mode | Latency percentiles are soft real-time objectives, not worst-case guarantees. |
| Safety assurance | Hazard analysis, acceptance evidence, operator authority and approved rollback/runbooks | Neither a neural network nor a deterministic policy is automatically certified for mission-critical control. |

PyTorch explicitly cautions that complete reproducibility is not guaranteed across releases/platforms. Qualify the exact execution environment and test repeatability. Where byte-identical floating-point output is infeasible, define justified numeric tolerances and require stable downstream classifications, including threshold-boundary tests. [14]

**Hard real-time** operation requires a defensible worst-case execution-time and scheduling argument for every dependency under stated assumptions. Shared-cloud inference plus an external satellite feed cannot simply be declared hard real-time. Keep safety-critical control independent of the SAR service and define a safe response to stale data, outage, overload, or missed deadlines.

### 8.1 Example decision contract

This is an illustrative schema shape, not an observed incident or a validated model output:

```json
{
  "schema_version": "1.0",
  "insight_id": "illustrative-site-042-flood-v1",
  "asset_id": "site-042",
  "hazard": "flood_exposure",
  "acquired_at": "2026-11-16T10:00:00Z",
  "ingested_at": "2026-11-16T10:12:00Z",
  "processed_at": "2026-11-16T10:18:00Z",
  "evaluated_at": "2026-11-16T10:19:00Z",
  "observation_age_seconds": 1140,
  "freshness_policy": "flood-screening-example-v1",
  "freshness": "within_policy",
  "coverage": "complete_for_asset_footprint",
  "quality_gate": "passed",
  "evidence_state": "exposure_observed",
  "flooded_footprint_fraction": 0.62,
  "uncertainty": {
    "probability_claim": "none",
    "boundary_accuracy": "not_validated_for_site_level_control",
    "limitations": ["urban_scattering", "asset_position_error"]
  },
  "telemetry_state": "unknown",
  "service_outage_state": "unconfirmed",
  "priority": "high",
  "reason_codes": ["FLOOD_OVERLAP", "CRITICAL_SERVICE_DEPENDENCY"],
  "recommendation": "Verify site condition and assess deployable coverage",
  "automatic_network_change_authorized": false,
  "provenance": {
    "source_product_id": "illustrative-input-product",
    "input_manifest_sha256": "illustrative-placeholder-not-a-real-hash",
    "asset_inventory_version": "illustrative-inventory-v1",
    "dependency_graph_version": "illustrative-graph-v1",
    "baseline_version": "illustrative-permanent-water-v1",
    "preprocessing_version": "illustrative-rtc-pipeline-v1",
    "model_version": "illustrative-flood-model-v1",
    "policy_version": "illustrative-exposure-policy-v1"
  }
}
```

Production contracts must validate types, enumerations, real content hashes, value ranges, units, geometries/CRS where supplied, and timestamp consistency. Define separate fields for model probability, quality, and priority; they are not interchangeable. Include expired, unknown, superseded, retracted, and failed outcomes rather than forcing every response into a successful-looking risk classification.

## 9. Failure modes and safety boundaries

| Failure mode | Required mitigation |
|---|---|
| Dark shadow mistaken for water | Terrain/geometry masks, valid-data handling, compatible reference imagery, and explicit unknown areas. |
| Flooded urban areas missed by low-backscatter logic | Urban-specific evaluation; consider intensity plus coherence and supporting observations, recognizing double-bounce effects. |
| Permanent water, wind-roughened water, vegetation or wet soil misclassified | Contextual baselines, independent labels, terrain/season validation, and uncertainty. |
| Change map interpreted as damaged tower/fiber | Label physical change/exposure only; verify with telemetry, engineering survey or field reports. |
| Flood extent interpreted as depth or passability | Require an independently validated hydraulic/depth model and operational ground confirmation. SAR extent alone does not give either. |
| No-data or low coherence interpreted as no hazard | Preserve masks and publish unknown/insufficient evidence. |
| Sensor/region/preprocessing shift | Compatibility checks, drift monitoring, abstention and requalification. |
| High pixel accuracy but poor operational decisions | Evaluate asset-level misses, shared dependencies, alert burden and restoration outcomes. |
| Automated rerouting creates a second failure | Use authorized, independently validated runbooks with capacity/diversity checks, human approval where required and rollback. |

Protect precise site coordinates, network topology, responder locations, and critical-infrastructure inventories. Apply least privilege, encryption, audit logs, retention controls, and supplier/license restrictions. Do not send sensitive asset data to public AI services. Hazard products may be open while the joined operational intelligence is sensitive.

## 10. Phased implementation and acceptance

| Phase | Deliverable | Exit evidence |
|---|---|---|
| 1. Historical feasibility | One region, flood-exposure use case, curated site/route inventory, simple baseline and AI comparison | Held-out event results, label/coverage audit, documented failure cases and operator review. |
| 2. Continuous shadow service | Catalog reconciliation, queue, immutable store, reproducible preprocessing, versioned evidence, dashboard | Real arrivals and replay tests demonstrate completeness, freshness, latency and explicit failure handling. |
| 3. Operational advisory pilot | Dependency-aware prioritization, NOC integration, operator feedback and approved escalation | Asset-level usefulness and false-alert burden meet pre-agreed thresholds; stale/unknown behavior is accepted. |
| 4. Controlled production | Resilient deployment, access control, monitoring, rollback and change management | Surge/failover/deadline-miss exercises and repeatability tests pass; responsibility and operational approvals are recorded. |
| 5. Expanded capabilities | InSAR trends, additional hazards, validated forecasting or outage models | Each capability has independent labels, uncertainty evaluation and acceptance criteria; no transfer of flood-model assurances by assumption. |

Before production, replay duplicates, out-of-order scenes, revised products, missing tiles, incompatible polarizations, empty observations, corrupt inputs, source outages, lost notifications, overloaded queues, threshold-boundary values, and model rollback. Verify that every case produces the intended visible state and does not silently clear an existing hazard.

**Recommended first outcome:** a continuously updated, evidence-linked flood-exposure advisory for a small set of critical sites and their physically diverse backhaul routes. Keep outage confirmation and network control separate until their own evidence and assurance requirements are satisfied.

## 11. Sources and further technical reading

Primary mission/product documentation and dataset maintainers are preferred. The architecture, sample contract, candidate models, timing objectives and telecom decision policies above are proposals, not claims made by these sources. Acquisition plans, product coverage, APIs and documentation can change; confirm the selected collection/version before implementation.

| Reference | Source | Supports |
|---|---|---|
| [1] | [NASA Earthdata: The SAR Handbook](https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/sar-handbook) | Radar principles, scattering, polarization, speckle, interpretation and preprocessing foundations. |
| [2] | [NASA/JPL: Synthetic Aperture Radars (SAR) Imaging Basics, Chapter 1](https://descanso.jpl.nasa.gov/SciTechBook/series2/02Chap1_110106_amf.pdf) | SAR geometry, signal formation, focusing and resolution theory. |
| [3] | [Copernicus EMS: Rapid Mapping portfolio](https://mapping.emergency.copernicus.eu/about/rapid-mapping-portfolio/) and [JRC: Manual for CEMS-Rapid Mapping Products](https://publications.jrc.ec.europa.eu/repository/handle/JRC121741) | Acquisition-dependent emergency mapping, product interpretation and delivery context. |
| [4] | [3GPP TS 22.280: Mission Critical Services Common Requirements](https://www.3gpp.org/DynaReport/22280.htm), [TS 22.179: MCPTT](https://www.3gpp.org/DynaReport/22179.htm), [TS 22.281: MCVideo](https://www.3gpp.org/DynaReport/22281.htm), [TS 22.282: MCData](https://www.3gpp.org/DynaReport/22282.htm) | Mission-critical communication requirements and service scope, not a mandate for SAR integration. |
| [5] | [Copernicus SentiWiki: S1 Products](https://sentiwiki.copernicus.eu/web/s1-products) | Sentinel-1 product levels, SLC/GRD characteristics, acquisition/product distinctions and packaging. |
| [6] | [SpatioTemporal Asset Catalog specification](https://stacspec.org/en) | Standardized geospatial asset discovery and metadata; not a SAR processor or a delivery guarantee. |
| [7] | [Copernicus Data Space: Sentinel-1 documentation](https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel1.html) | Mission data, product access and processing context. |
| [8] | [ISCE2 project documentation](https://github.com/isce-framework/isce2) | Interferometric SAR processing framework and supported workflows. |
| [9] | [MintPy project documentation](https://github.com/insarlab/MintPy) | Referenced line-of-sight displacement time series, corrections and quality assessment. |
| [10] | [NASA/JPL OPERA products](https://www.jpl.nasa.gov/go/opera/products/), [RTC](https://www.jpl.nasa.gov/go/opera/products/rtc-product/), [DSWx](https://www.jpl.nasa.gov/go/opera/products/dswx-product-suite/) and [DISP](https://www.jpl.nasa.gov/go/opera/products/disp-product-suite/) | Product definitions, coverage differences and technical documentation. |
| [11] | [Sen1Floods11 dataset and documentation](https://github.com/cloudtostreet/Sen1Floods11) | SAR flood training data, VV/VH channels, labels, invalid values, splits and citation requirements. |
| [12] | [SpaceNet 8 dataset](https://spacenet.ai/sn8-dataset/) | Optical flood-affected infrastructure benchmark; not a SAR imagery source. |
| [13] | [OPERA RTC science application software](https://github.com/opera-adt/RTC) | Open implementation for generating Sentinel-1 RTC backscatter with mission-specific configuration. |
| [14] | [PyTorch: Reproducibility](https://docs.pytorch.org/docs/stable/notes/randomness.html) | Deterministic algorithm controls and cross-platform/version reproducibility limitations. |

Some primary pages were available through indexed web search but could not be fetched directly from the research environment. No live acquisition, vendor SLA, model accuracy, timing benchmark, or end-to-end deployment has been verified by this documentation exercise.

## 12. Architecture & Blueprint Selection by Scenario

This section extends the reference architecture with three **proposed implementation blueprints**. They share ingestion, provenance, quality control, and advisory delivery, but require different physical measurements and processing branches. Architecture selection must begin with the operational question, not with a preferred AI model.

### 12.1 Selection guide

| Scenario | Primary measurement and input | Select this blueprint when | Processing and delivery pattern | Do not substitute |
|---|---|---|---|---|
| Rapid Disaster Response: Flood & Damage Mapping | Calibrated GRD/RTC backscatter and compatible pre-event references; optional SLC-derived coherence | Responders need event-water extent, candidate damage/change areas, and asset/access exposure after an incident | Event-triggered, parallel area-of-interest processing; separate flood and damage-screening heads; versioned emergency map releases | A dark-pixel mask for a validated flood product, or a change map for confirmed structural damage |
| Maritime Security: Dark Vessel & Oil Spill Detection | Calibrated sea-surface intensity, acquisition geometry, AIS observations, wind and ocean context | Maritime analysts need vessel candidates, unexplained AIS non-matches, or suspected surface pollution | Acquisition-triggered dual detection branches, event-time track association, analyst case management | Missing AIS for proof of wrongdoing, or dark water for confirmed oil |
| Infrastructure Protection: Deformation & Stability Monitoring | Compatible phase-preserving SLC/CSLC stacks, or qualified displacement products | Engineers need repeatable movement trends around towers, foundations, slopes, pipelines, ducts, or other assets | Stateful, historical time-series processing; quality-gated anomaly detection; engineering review | GRD/RTC intensity for interferometric phase, or line-of-sight displacement for full 3D structural movement |

**Blueprint selection rules:**

1. If the question is **where surface water or surface change is visible now**, choose the disaster blueprint; retain uncertainty and acquisition-time limitations.
2. If the question is **what vessel-like or slick-like features are visible at sea**, choose the maritime blueprint; identity association and pollution interpretation are separate tasks.
3. If the question is **whether a coherent target is moving over successive acquisitions**, choose the infrastructure blueprint; first establish whether the historical stack and geometry support that measurement.
4. If an event spans scenarios, run the relevant branches independently and fuse their evidence at the asset/case layer. For example, flood exposure and foundation displacement are different observations, not interchangeable confidence scores.

All three blueprints use the reliability requirements in Section 6.1 and the decision-contract principles in Section 8.1. Service objectives, resource sizing, model thresholds, and freshness policies must be established through local benchmarking and operational approval; none below is a measured SLA.

### 12.2 Rapid Disaster Response (Flood & Damage Mapping)

#### 1. Objective

Produce an acquisition-time picture of newly observed inundation and candidate disaster-related surface change, then identify exposed communities, emergency-service facilities, communication assets, power dependencies, and restoration access routes.

Separate the deliverables into **flood extent**, **damage/change screening**, and **operational exposure**. They answer different questions and require separate quality indicators.

| Operational question | Deliverable | Decision supported | Boundary |
|---|---|---|---|
| Where is event water visible beyond normal water conditions? | Event-water class/probability raster, permanent-water layer, uncertainty and valid-coverage masks | Prioritize reconnaissance, pumping, protection, and response planning | Extent alone does not measure depth, flow, contamination, or route passability |
| Where has the surface changed after the incident? | Candidate change polygons with intensity/coherence evidence and event context | Target imagery review and field inspection | Change does not uniquely establish structural damage or its cause |
| Which facilities and dependencies intersect that evidence? | Footprint/route exposure summaries, shared-risk dependencies, prioritized inspection list | Protect power and backhaul; stage portable coverage | Exposure is not confirmation of service outage |
| What changed since the previous release? | Versioned map differences, acquisition intervals, additions/retractions and coverage changes | Update a common operating picture without hiding revisions | A new model version or newly valid coverage is not necessarily a physical change |

The response lead owns incident priorities; the geospatial analyst owns map qualification; network operators and field teams confirm service impact and access conditions. Define the AOI, incident window, map scale, acceptable missed critical assets, review authority, and maximum evidence age before activation.

#### 2. The Physics

Smooth open water often reflects radar energy away from the sensor and therefore appears dark. Flooding can cause a marked reduction in backscatter relative to compatible pre-event imagery. This is a useful mechanism, not a universal flood signature. SAR scattering and product distinctions are described in Sections 3.1-3.5 and sources [1][2][5].

| Physical effect | Observable evidence | Design consequence |
|---|---|---|
| Specular reflection from smooth water | Low return, often with a pre/post intensity decrease | Combine backscatter, temporal change, terrain, and permanent-water context rather than using one global threshold |
| Wind-roughened water | Higher return than calm water | Evaluate wind/exposure conditions and avoid equating bright water with dry land |
| Urban or vegetation-water double bounce | Flooded targets may become brighter, depending on geometry and canopy/structure | Evaluate urban and vegetated flood classes separately; consider multi-date/polarization evidence and abstain where unsupported |
| Wet soil and changing vegetation | Intensity changes unrelated to standing water | Use seasonal references, land-cover context, rainfall information, and representative negative examples |
| Shadow, layover, and terrain distortion | Dark or geometrically mixed areas unrelated to inundation | Retain geometry masks and unknown classes; DEM correction cannot recover hidden surfaces |
| Structural or land-surface disturbance | Changes in intensity, texture, or SLC-derived coherence | Maintain a separate change-screening branch; account for vegetation, moisture, acquisition interval, and viewing geometry |

For matched linear-power images, a useful feature is `10 * log10(P_post / P_reference)`; equivalently, subtract consistently defined dB backscatter images. Mask zero/invalid inputs and compare equivalent calibration, geometry, and preprocessing. A large negative change can support open-water interpretation, but is neither a universal threshold nor proof of flooding.

Coherence loss can support disturbance screening only when compatible SLC pairs and a meaningful pre-event coherence baseline exist. Coherence also changes with vegetation, water, temporal separation, noise, and co-registration quality. GRD products do not contain the phase required to derive interferometric coherence.

#### 3. The Architecture

**Recommended blueprint: event-driven raster analysis with two independent inference heads and an asset-aware advisory layer.**

```text
Incident activation / catalog reconciliation
    -> AOI + acquisition/baseline compatibility checks
    -> immutable GRD/RTC store ------------------------------+
    -> calibrated, aligned intensity tiles                  |
         |-> flood baseline + segmentation -> water evidence|
         `-> pre/post change detector ------> change evidence|
                                                            v
Optional compatible SLC stack -> coherence processing -> evidence quality gate
                                                            |
DEM / water history / assets / roads / field reports -> spatial fusion
                                                            |
                                versioned maps + inspection recommendations
                                                            |
                                    analyst approval -> response/NOC delivery
```

The diagram represents logical services, not mandatory individual microservices. A small deployment can use one orchestrated batch pipeline with durable checkpoints; scale out tile workers only when AOI size and delivery budgets justify it.

| Component | Design detail |
|---|---|
| Activation and scheduler | Store incident ID, AOI version, event window and priority; search archives for compatible references; reconcile new scenes and publish explicit acquisition/coverage gaps |
| Preprocessing workers | Follow Section 3.5; cache DEM/reference mosaics; preserve tile halos and masks; treat SLC/coherence processing as a distinct optional path |
| Flood model | Begin with threshold/change baselines; compare a U-Net-style segmentation or temporal model using supported VV/VH channels, reference/current backscatter, and qualified contextual features |
| Damage-screening model | Begin with intensity/coherence change statistics; evaluate a Siamese or temporal model only with temporally aligned, event-specific change/damage labels; do not relabel an unvalidated change score as damage probability |
| Spatial fusion | Join results to full asset footprints and physical routes with position/boundary uncertainty; propagate shared power, transport and backhaul exposure through the dependency graph |
| Publication | Store COG rasters and vector exposure layers, source manifests, model/policy versions, and analyst dispositions; issue corrections when a release is superseded |
| Surge handling | Prioritize critical AOIs, bound tile queues and retries, checkpoint completed work, and expose partial coverage instead of presenting incomplete maps as complete |

**AI insight design:** use separate output heads/contracts for `event_water`, `candidate_surface_change`, and `asset_exposure`. Inputs must distinguish permanent water, event water, non-water, and unknown. A flood probability is meaningful only if calibrated on the relevant sensor, event types, and terrain; it must not become an outage or damage probability through a spatial join.

For each recommendation, retain the asset footprint/inventory version, observed overlap fraction over valid coverage, unknown footprint fraction, observation time, baseline age, model quality, and corroborating telemetry. Record reason codes such as `NEW_WATER_OVERLAP`, `COMMON_CAUSE_BACKHAUL_EXPOSURE`, or `POST_EVENT_CHANGE_REVIEW`. Criticality can raise inspection priority without changing the model's physical hazard probability.

Train and evaluate by held-out events/geographies, with dedicated urban, vegetated, coastal and mountainous subsets. Sen1Floods11 can support flood research [11]; it does not supply universal damage labels. Optical-only damage data such as SpaceNet 8 [12] needs a separately justified multimodal/label-alignment design rather than being treated as SAR imagery.

#### 4. The workflow

1. **Activate and define the decision.** Register the disaster footprint/time, decision owners, critical assets, observation-age policy, release criteria, and authoritative incident reports.
2. **Select current and reference observations.** Match orbit, polarization, mode, geometry and processing; use representative seasonal/pre-event references. Record insufficient references as a limitation rather than silently selecting incompatible imagery.
3. **Generate analysis-ready inputs.** Calibrate and terrain-correct as appropriate, align grids, apply masks, and retain valid coverage. Generate coherence only through a qualified compatible SLC path.
4. **Infer water and screen change separately.** Run each against its simple baseline; retain per-pixel uncertainty/abstention, permanent-water distinctions, model versions and seam handling.
5. **Apply physical plausibility and quality checks.** Review terrain, water connectivity where appropriate, urban scattering, missing tiles and implausible boundaries. Connectivity is supporting context, not a rule that erases isolated genuine flooding.
6. **Create asset/dependency insights.** Calculate valid-area exposure and shared-corridor risks; add outage/power telemetry with its own timestamps. Produce inspection and deployment candidates, not an assertion that an unflagged route is safe.
7. **Review and release.** Have the authorized analyst qualify the map, uncertainty and coverage; distribute versioned layers and evidence-linked recommendations. Preserve the difference between preliminary automated output and approved operational maps.
8. **Refresh and reconcile.** Reprocess new scenes and corrections, compare only compatible versions, expire stale recommendations, and collect field/outage dispositions for offline evaluation.

**Acceptance evidence:** measure per-event flood precision/recall/IoU on valid labeled areas, critical-asset exposure misses, false inspections, unknown coverage, change-screening accuracy against independent event labels, map geolocation/boundary error, and acquisition/publication-to-release latency. Establish release thresholds with responders; report the acquisition wait separately from local processing time.

### 12.3 Maritime Security (Dark Vessel & Oil Spill Detection)

#### 1. Objective

Detect vessel-like targets and suspected oil slicks in a maritime AOI, associate vessel observations with available reporting data, and provide prioritized, evidence-linked cases to authorized maritime analysts.

Here, **dark-vessel candidate** means a vessel-like SAR detection with no reliable match in the available AIS data under a documented association policy. It is not a determination that a vessel deliberately disabled AIS, violated reporting rules, or committed an offense.

| Operational question | Deliverable | Decision supported | Boundary |
|---|---|---|---|
| What vessel-like targets are visible? | Geolocated detections with localization uncertainty, footprint estimates and quality flags | Surveillance review and follow-up collection | Detection and approximate dimensions depend on resolution, sea state, geometry and vessel construction |
| Which detections lack a trustworthy AIS association? | Matched, ambiguous, unmatched, or insufficient-AIS association status | Investigate unexplained observations | Receiver gaps, stale messages, non-equipped vessels and timing errors can produce non-matches |
| Which surface features are consistent with an oil slick? | Suspected-slick polygons, confidence/quality, environmental context and look-alike indicators | Direct authorized verification and response planning | SAR does not identify oil chemistry or reliably derive spill thickness/volume from dark intensity alone |
| Is there evidence worth reviewing for a possible source? | Candidate vessel/track associations with temporal and drift uncertainty | Analyst reconstruction of possible events | Proximity or an apparent trailing feature does not establish responsibility |

EMSA's CleanSeaNet provides operational context for satellite-based oil-spill and vessel detection, supporting data, and follow-up by authorities. It is evidence for the capability class, not validation of the AI models or integration proposed here. See [M1][M2] below.

#### 2. The Physics

Vessels can produce strong returns from metallic structures, corners and multiple reflections, appearing as bright targets against sea clutter. Small or low-reflectivity craft may not be detectable. Sea clutter varies with wind, waves, incidence angle, polarization and noise; one brightness threshold cannot maintain the same false-alarm rate everywhere.

Oil films can damp the short surface waves that contribute to microwave backscatter, creating dark slick-like regions relative to surrounding water. Detectability requires sufficient contrast: calm water can already be dark, while rough weather and breaking waves can obscure or disperse the signature. Product-specific and locally validated environmental applicability limits are necessary; do not hard-code an unsupported universal wind interval. [M1][M2]

| Effect or ambiguity | Consequence for design |
|---|---|
| Variable ocean clutter | Estimate local background statistics; evaluate by sea state, incidence angle and coastal/open-ocean setting |
| Small vessels, weak reflectors, crowding | Report resolution-limited detectability and merged targets; output apparent dimensions with uncertainty rather than exact hull dimensions |
| SAR imaging of moving targets | Motion can shift or smear an apparent target location; include motion/geolocation uncertainty when matching to AIS |
| Coastal structures, platforms, rocks and bright artifacts | Use shoreline/fixed-object context and dedicated hard negatives; preserve coastal review paths so masking does not simply hide real nearshore vessels |
| Low-wind zones, biogenic films, rain cells, fronts and wakes | Treat dark patches as candidates requiring environmental context and look-alike discrimination |
| Surface transport after release | Keep acquisition time explicit; use a separate current/wind-driven drift model for forecasts and source hypotheses, not a pixel-based certainty claim |

AIS supplies cooperative position reports, not a complete or infallible inventory. SAR-to-AIS association must account for message time, reception coverage, position accuracy, plausible vessel motion and potentially unreliable identifiers. Radar observations and AIS assertions must retain separate provenance.

#### 3. The Architecture

**Recommended blueprint: dual maritime detectors with event-time association, environmental fusion, and analyst-controlled case management.**

```text
SAR catalog -> calibrated sea-surface intensity + geometry + quality masks
                         |                              |
                 vessel detector                 slick segmenter
                         |                              |
AIS history -> event-time association        wind / sea state / currents
                         |                              |
             matched / ambiguous /          look-alike assessment +
             unmatched / insufficient AIS   suspected-slick evidence
                         |                              |
                         +---- evidence/case fusion ----+
                                       |
                         analyst review + authorized verification
                                       |
                           maritime operations advisory
```

Use the common ingestion/storage infrastructure, but do not assume the land-focused flood RTC preprocessing, masks or training statistics are appropriate for the sea. Retain the calibration, incidence-angle, noise, geolocation and radiometric conventions required by the selected maritime product and model.

| Component | Design detail |
|---|---|
| Vessel baseline and model | Start with a locally validated constant false alarm rate (CFAR) detector; compare an object detector or instance-segmentation model for targets and crowded/coastal cases |
| Slick baseline and model | Start with local dark-region segmentation and interpretable shape/contrast/context features; compare a segmentation model plus a separately validated look-alike classifier |
| AIS event-time store | Retain report and ingestion timestamps, receiver/coverage provenance, quality and identifier history; support bounded waiting/reconciliation for late messages |
| Association engine | Propagate eligible tracks to acquisition time within bounded gaps, gate candidates using uncertainty, and resolve competing matches; do not force nearest-neighbor identity assignments |
| Environmental fusion | Join time/space-matched wind, sea state, currents, coastline and fixed-object context; label missing/stale context and widen uncertainty or abstain as required |
| Case store | Keep detections, association hypotheses, suspected slicks, revisions, evidence references, reviewer decisions and verification results; preserve ambiguous alternatives |
| Delivery | Publish observations at acquisition time and separate forecast layers; issue case updates/retractions rather than repeated independent accusations |

**AI insight design:** keep three model/logic products distinct: vessel detection confidence, AIS-association confidence/status, and suspected-slick confidence. None is automatically a probability of illegal activity. If calibration is unavailable, publish a score with its evaluation context instead of labeling it a probability.

A vessel case should include `detection_id`, acquisition time, geometry/position uncertainty, model version, quality flags, association window, AIS coverage status, candidate match identifiers and scores where permitted, association state, and analyst disposition. A slick case should include polygon area in an appropriate CRS, contrast/shape evidence, wind/context age, look-alike indicators, valid coverage, and `verification_status`. Do not populate chemistry, thickness, volume, identity, or liability fields from unsupported inference.

Use hard-negative training cases from platforms, ports, islands, breaking waves, rain and low-wind water. Split validation by region, acquisition period, sensor, vessel track and pollution incident to reduce leakage. AIS absence is not a valid vessel-negative label; an unverified dark patch is not a confirmed oil-positive label. Require independent expert annotations and follow-up evidence where available.

#### 4. The workflow

1. **Define surveillance intent and authority.** Register the AOI, authorized users, lawful data access, target detectability requirements, environmental limits and follow-up owner.
2. **Ingest SAR, AIS and environmental context.** Preserve acquisition versus message/ingestion times, reception coverage, source quality and missing-data states. Reject unsupported modes or resolutions visibly.
3. **Prepare maritime imagery.** Apply product-appropriate calibration/noise handling and geolocation; retain incidence-angle/context layers and carefully qualified coastal/fixed-object masks.
4. **Run independent vessel and slick branches.** Detect vessel-like targets against local clutter and segment slick-like regions; retain branch-specific uncertainty and invalid/environmentally unsuitable regions.
5. **Associate vessels at event time.** Use bounded track interpolation or propagation with growing uncertainty; resolve candidate conflicts. Publish `insufficient_AIS` when the feed cannot support an absence claim, and `ambiguous` when multiple associations remain plausible.
6. **Assess suspected pollution.** Evaluate contrast, morphology, local wind/sea state and look-alikes. If source review is required, use time-aware tracks and a validated drift model with uncertainty; do not infer responsibility from nearest-vessel proximity.
7. **Open an evidence-linked case.** Present the image chip, wider context, uncertainty, source ages, association alternatives and reason codes such as `SAR_VESSEL_NO_RELIABLE_AIS_MATCH` or `SLICK_LIKE_FEATURE_REQUIRES_VERIFICATION`.
8. **Verify and reconcile.** Authorized analysts request appropriate corroboration or inspection. Update match states as late AIS arrives, preserve history, and record confirmed/rejected/inconclusive pollution findings independently of the original model score.

**Acceptance evidence:** report vessel precision/recall by vessel size and sea state, false alarms per unit of valid searched sea area, geolocation error, AIS match accuracy/ambiguity, performance under receiver gaps, slick object/pixel precision-recall, area error and look-alike false alarms. Measure analyst workload, verification yield, acquisition-to-case latency and correction latency. No universal detection accuracy or delivery interval is assumed.

### 12.4 Infrastructure Protection (Deformation & Stability Monitoring)

#### 1. Objective

Identify persistent or changing ground/target movement around critical infrastructure and prioritize engineering investigation before a potentially consequential condition is overlooked.

Applicable assets include tower foundations, communication shelters, fiber/utility corridors, embankments, bridges, dams, ports and industrial sites, subject to observability and engineering context. A radar scatterer near an asset is not necessarily on that asset, and an asset smaller than the effective spatial support may not be separable from its surroundings.

| Operational question | Deliverable | Decision supported | Boundary |
|---|---|---|---|
| Is the observed target moving relative to the reference? | Referenced line-of-sight displacement series, velocity and quality | Rank surveys and compare with known regional trends | Relative radar displacement is not automatically vertical settlement |
| Has behavior changed? | Trend/change-point evidence, persistence and uncertainty | Request geotechnical review or increased instrumentation | An anomaly score does not establish structural instability or predict failure time |
| Are adjacent parts of a corridor moving differently? | Differential movement over defined distances with spatial support/uncertainty | Investigate potential strain-sensitive segments | Surface movement is not a direct measurement of buried pipe/fiber strain |
| Which communication dependencies could be affected? | Asset-linked movement evidence plus criticality and live telemetry | Coordinate inspection and resilience planning | SAR alone does not confirm equipment, foundation or service failure |

Asset engineers define investigation criteria using design, soil, loading, consequence and instrument context. Safety-critical alarms and closures must remain supported by independently qualified monitoring and approved procedures; satellite revisit cannot replace continuous structural sensing.

#### 2. The Physics

InSAR compares phase from compatible, precisely co-registered complex acquisitions. A conceptual phase budget is:

```text
observed phase difference =
    geometric/topographic contribution
  + deformation contribution
  + atmospheric/ionospheric contribution
  + orbit/DEM residuals
  + scattering/noise terms
  (observed modulo 2*pi before unwrapping)
```

After appropriate corrections and unwrapping, deformation phase can be converted to line-of-sight displacement using wavelength and the processor's signed convention. Section 3.6 describes the phase-preserving chain; [8][9] provide implementation context.

| Physical constraint | Architectural consequence |
|---|---|
| Phase discarded in GRD/intensity RTC | Start with compatible SLC/CSLC or a qualified displacement product; no AI model can reconstruct the missing observed phase from intensity |
| Temporal/spatial decorrelation | Mask unreliable observations and retain disconnected components; a gap is unknown movement, not stability |
| Wrapped phase and unwrapping errors | Check interferogram-network consistency, connected components, residuals and abrupt discontinuities before interpreting trends |
| Atmospheric delay, including terrain-correlated signals | Apply suitable corrections and spatial/temporal checks; compare with independent ground measurements rather than trusting a smooth fitted trend |
| Reference dependence | Record reference region/point, epoch and stability evidence; changing the reference changes the reported relative series |
| Line-of-sight projection | Publish LOS geometry and sign; ascending/descending data can support selected component estimates under assumptions, not unconstrained 3D recovery |
| Layover, shadow and mixed scattering | Document actual observable targets and spatial support; nearby radar measurements cannot automatically be assigned to a specific foundation |
| Rapid motion between observations | Aliasing, decorrelation and unwrapping failure may prevent reliable recovery; lack of a measured anomaly cannot establish safety |

Persistent-scatterer approaches suit sufficiently stable individual radar targets; small-baseline time-series approaches can exploit suitable distributed/coherent areas. These are selection principles, not mutually exclusive products: choose the processor and strategy after assessing target density, land cover, temporal/perpendicular baselines, geometry and independent validation. No universal minimum scene count guarantees a reliable trend.

#### 3. The Architecture

**Recommended blueprint: stateful InSAR time-series processing with a separate engineering anomaly and decision layer.**

```text
Compatible SLC/CSLC archive + new acquisitions
    -> orbit / DEM / burst-aware co-registration
    -> interferogram network + coherence
    -> correction / unwrapping / consistency checks
    -> referenced time-series inversion + uncertainty
    -> quality-controlled target/region evidence store
                          |
GNSS / leveling / tilt / weather / engineering asset model
                          |
          robust trends + qualified anomaly detector
                          |
         engineering review -> inspection recommendation
                          |
             field findings + versioned reassessment
```

A qualified provider displacement product may enter at the time-series evidence layer after reference, coverage, units, quality and compatibility checks. It is an alternative upstream implementation, not permission to skip provenance or independent validation.

| Component | Design detail |
|---|---|
| Stack manager | Track relative orbit, burst overlap, mode, polarization, reference epoch, baseline network, orbit/DEM versions and coherent coverage |
| Phase-processing workers | Use a validated processor such as ISCE with appropriate mission support; cache reusable pair products; isolate memory/I/O-heavy jobs from low-latency advisory services |
| Time-series processor | Use an appropriate inversion/correction workflow such as MintPy; retain coherence, residuals, connected components, uncertainty and reference metadata [8][9] |
| Versioned state | Store the input graph and complete released series; new acquisitions/corrections may revise historical estimates, so publish a new consistent version rather than appending an unexplained final point |
| Asset association | Associate scatterers/regions with surveyed footprints and geolocation uncertainty; distinguish structure, adjacent ground and background reference targets |
| Anomaly service | Start with robust trends, engineering-approved limits and change-point tests; add seasonal/state-space or other temporal ML models only if they improve independent validation |
| Engineering delivery | Display displacement and uncertainty alongside geometry, coverage, sensor corroboration, maintenance history and prior investigations; preserve reviewer authority and audit history |

**AI insight design:** AI consumes quality-controlled displacement observations and context; it should not treat raw wrapped phase as direct movement or silently interpolate unsupported measurements. Candidate features include referenced LOS trend, trend change, differential movement over a defined baseline, seasonal residual, coherence, sampling gaps and independent sensor agreement. Acceleration claims require enough observations and uncertainty analysis; noisy finite differences are not failure forecasts.

Keep `movement_estimate`, `measurement_quality`, `anomaly_score`, and `engineering_priority` separate. Record units, reference epoch/region, LOS vector/sign, observation dates, fit window, target count/spatial support, uncertainty method, processing version and asset-association confidence. An illustrative recommendation is "review sustained relative movement near this foundation and compare with GNSS," not "tower collapse imminent."

Training labels should come from engineer-reviewed movement episodes, maintenance and instrumentation with aligned dates. Hold out entire assets/regions and later time periods; avoid leakage from revised full-series products into historical prediction tests. Run retrospective evaluations using only data and corrections available at each decision time. Unsupervised anomalies require review and cannot be advertised as calibrated failure probabilities.

#### 4. The workflow

1. **Define the engineering question.** Inventory assets and consequence, survey target locations, document expected motion and permissible investigation actions, and establish qualified reference measurements.
2. **Assess observability and history.** Check compatible archive length, coherent target density, viewing geometry, data gaps and achievable spatial support. Report assets without usable measurements explicitly.
3. **Build the phase-preserving stack.** Follow Section 3.6 or qualify a provider product; construct a connected interferogram network and retain processing/auxiliary-data versions.
4. **Generate and qualify the time series.** Correct/invert as appropriate, verify reference stability, inspect unwrapping/network residuals and mask unreliable estimates. Retain uncertainty and disconnected coverage.
5. **Validate and associate with assets.** Compare against GNSS/leveling or other measurements in compatible geometry/reference/time; distinguish adjacent ground from actual structure observations.
6. **Detect meaningful changes.** Apply approved trend/persistence rules before optional ML; account for seasonality, irregular sampling, multiple comparisons and uncertainty. Low quality produces an insufficient-evidence state rather than a reassuring zero trend.
7. **Review and prioritize.** An engineer examines spatial consistency, corroborating instruments, rainfall/temperature/loading and maintenance. Prioritize surveys using consequence and dependencies without relabeling priority as failure probability.
8. **Refresh with revision control.** Process each usable acquisition, publish series revisions and reference changes, reassess earlier alerts, and collect field outcomes. Instrumented local alarms continue independently between satellite updates.

**Acceptance evidence:** compare LOS displacement/velocity against independent measurements with compatible reference and geometry; report bias, error distributions, uncertainty calibration, coherent coverage and reference sensitivity. Evaluate false investigations per asset/time, missed known movement episodes, detection delay, robustness to gaps/atmosphere/unwrapping errors and workload. Qualify any component decomposition separately; no generic millimeter-accuracy or failure-prediction claim is implied.

### 12.5 Shared AI insight and delivery contract

The common platform should normalize **provenance and decision lifecycle**, not erase scenario-specific measurement meaning. Extend the illustrative contract in Section 8.1 with the following scenario payloads.

| Contract element | Required design |
|---|---|
| Identity and time | Stable observation/case/asset IDs, scenario, contributing acquisition interval, ingestion/evaluation times and evidence age; retain per-source timestamps for fusion |
| Measurement | Typed physical quantity/class, units, geometry/CRS and spatial support; distinguish observed, modeled, forecast and reported evidence |
| Evidence and quality | Valid/unknown coverage, uncertainty method, calibration status, compatibility flags, environmental limitations and links to source products |
| Scenario payload | Flood: water/change/exposure layers. Maritime: target/slick geometry and association/verification states. Infrastructure: referenced LOS series, quality and trend evidence |
| Decision | Versioned reason codes, priority, rule/model versions, reviewer state, recommended action and explicit automation authority |
| Lifecycle | Support preliminary, approved, stale, insufficient-evidence, failed, superseded and retracted states; source corrections must reach affected cases |

**LLM-assisted explanation design:** generate the authoritative measurement, spatial join, association, trend and policy result using qualified structured services first. An optional LLM can turn that contract into a concise operator narrative with evidence IDs and limitations. Require schema validation and checks that every numerical value, coordinate, identity and claim is supported by the contract; reject unsupported statements rather than silently repairing them into authoritative findings.

Treat free-text reports and retrieved material as untrusted evidence, not execution instructions. Limit retrieval to access-authorized sources, minimize sensitive asset/vessel information, and retain explanation/model provenance. The LLM must not invent oil-spill confirmation, assign liability, declare a route safe, infer structural failure, or set operational thresholds. Missing context should result in an explicit insufficient-evidence explanation.

**Operational separation:** GPU inference may accelerate flood/maritime imagery; InSAR needs its own qualified phase-processing and historical-state resources. Size each workload from representative scenes/stacks, tile counts, intermediate storage and surge behavior. A shared event bus, immutable object store, geospatial database and dashboard are useful; a single universal model or preprocessing graph is not.

### 12.6 Additional maritime sources

These sources supplement Section 11 for the maritime scenario. They describe established service concepts, not measured performance or certification of this proposed blueprint. Relevant material was discoverable through indexed search; direct EMSA page retrieval was unavailable during this update.

| Reference | Source | Supports |
|---|---|---|
| [M1] | [EMSA: CleanSeaNet](https://www.emsa.europa.eu/csn-menu.html) and [CleanSeaNet service catalogue](https://emsa.europa.eu/publications/leaflets/download/7509/4962/23.html) | Satellite-based oil-spill and vessel detection, contextual interpretation and follow-up |
| [M2] | [European Cooperation on Coast Guard Functions: CleanSeaNet oil spill and vessel detection services products](https://coastguard.europa.eu/catalogues/maritime-data-catalogue/601-cleanseanet-oil-spill-and-vessel-detection-services-products) | Maritime detection products, supporting information and operational service context |

## 13. SAR Preprocessing Pipeline: Core Prerequisites for AI

Preprocessing must match the SAR product and the model's intended task. There is no single sequence that is correct for every sensor or AI model. First establish which corrections are already present in the source product; do not apply them again blindly. The backscatter workflow in Section 3.5 covers the Sentinel-1 intensity branch, while phase-sensitive InSAR requires the separate workflow in Section 3.6.

### 13.1 Core input checks

Before creating model inputs:

1. **Identify the product and its meaning.** Record the mission, product type and processing level, acquisition mode, polarization, acquisition time, calibration state, units, coordinate reference system, pixel spacing, and available quality/no-data masks. SLC, GRD, and RTC products are not interchangeable; use a phase-preserving SLC workflow for interferometric tasks.
2. **Apply only relevant source corrections.** For Sentinel-1 GRD, check whether orbit updates and applicable border/thermal-noise corrections are needed, then radiometrically calibrate to the selected backscatter convention. Keep the convention (for example, sigma-nought or gamma-nought) and units explicit.
3. **Account for terrain and geometry.** Use DEM-based terrain correction when map-geolocated data are required. Radiometric terrain correction/flattening is a separate choice for topographic effects on measured brightness; it is not the same operation as geometric correction.
4. **Treat speckle filtering as task-dependent.** Speckle is inherent in coherent radar imaging. Filtering or multilooking may reduce it but can also remove spatial detail or change image statistics. Use these operations only when suitable for the task, and keep the preprocessing consistent between training and inference.
5. **Make scenes comparable.** Align inputs to a documented common map grid and compatible pixel spacing; preserve polarization channels as distinct features unless the model specification explicitly combines them. Carry valid-data, layover/shadow, and other relevant quality masks through the pipeline.
6. **Match the model's value representation.** Record whether inputs are linear backscatter or in decibels and use the exact representation and normalization expected by the trained model. Do not mix representations or derive normalization separately at inference time.
7. **Retain provenance.** Store the source product identifiers, processor/version, orbit and DEM versions, corrections and parameters, grid definition, units, polarization order, masks, and model-input transformation with each prepared dataset.

### 13.2 What terrain correction cannot fix

Side-looking radar geometry can produce foreshortening, layover, and radar shadow. DEM-based terrain correction improves the geographic placement of observed returns and accounts for terrain in the projection, but it cannot recreate returns from shadowed areas or make geometrically overlapping layover returns unambiguous. Keep these areas identified in quality masks; do not treat them as ordinary valid observations for model training or inference.

The sequence and optional operations should be selected from the product documentation and processing tool guidance for the chosen mission. In particular, do not assume that every SAR model requires speckle filtering, radiometric terrain flattening, or conversion to decibels.

**Technical references:** [NASA Earthdata SAR Handbook](https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/sar-handbook); [Copernicus Sentinel-1 product guide](https://sentiwiki.copernicus.eu/web/s1-products); [Copernicus Data Space Sentinel-1 documentation](https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel1.html); [NASA/JPL OPERA Radiometric Terrain Corrected product](https://www.jpl.nasa.gov/go/opera/products/rtc-product/).
