# AI Insights from SAR Data

Synthetic aperture radar (SAR) can observe the ground through clouds and at night. For disaster response, a model can screen changes between pre- and post-event radar observations to help analysts prioritize areas for flood assessment.

## Flood-screening example

This repository includes a dependency-free Python 3 example of model inference on **already prepared** observations. The supplied model coefficients and observations are invented for demonstration: they are not trained or validated, and their scores are not calibrated probabilities. Do not use this example for emergency decisions, alerts, or other operational purposes.

```sh
python3 sar_flood.py examples/observations.csv --model examples/flood_model.json
```

The command writes CSV to standard output, including `flood_probability` (the logistic model's score) and `flagged` (1 if the score is at least the threshold, otherwise 0). Use `--threshold 0.7` to change the default threshold of 0.5. For example, redirect the output to a file for inspection in a GIS:

```sh
python3 sar_flood.py examples/observations.csv --model examples/flood_model.json > scores.csv
```

Each input row represents the same ground location in two acquisitions:

| Column | Meaning |
| --- | --- |
| `pixel_id` | Identifier beginning with an ASCII letter or digit, followed by letters, digits, `_`, `-`, or `.` |
| `latitude`, `longitude` | WGS84 coordinates in decimal degrees |
| `before_db`, `after_db` | Pre- and post-event calibrated backscatter in decibels |

Coordinates must be in range and all numeric values must be finite. Missing or invalid values fail the run rather than being treated as zero. Extra input columns are ignored. The command validates all rows before writing results and holds them in memory; for large scenes, partition the input into manageable batches.

The model file contains a numeric `bias` and exactly three numeric `weights`: `before_db`, `after_db`, and `delta_db`, where `delta_db = after_db - before_db`. The score is `sigmoid(bias + sum(weight × feature))`. A replacement model must use this exact feature definition and be trained and validated for the intended sensor, preprocessing, region, and task. The example detects possible current change; it does not forecast future flooding.

## From radar scenes to decision support

1. Acquire suitable pre- and post-event SAR scenes with compatible orbit, polarization, and viewing geometry. Calibrate to comparable backscatter, terrain-correct and co-register them to a common grid, and convert positive linear backscatter to dB (`10 * log10(value)`). Apply appropriate speckle handling and mask no-data, layover, shadow, and other unreliable pixels. This repository does **not** perform these preprocessing steps or read raw SAR/GeoTIFF files.
2. Extract matching grid-cell values and WGS84 coordinates into the CSV schema above. Track acquisition times, processing version, quality masks, and scene provenance alongside each batch.
3. Train a model on representative, independently labeled flood and non-flood observations, separating evaluation data by event and geography. Evaluate precision, recall, calibration, and performance across land cover and conditions; choose thresholds with domain experts according to the consequences of missed and false detections. Smooth water may appear dark, but wind, vegetation, urban structures, and permanent water can confound flood mapping.
4. Package a validated model and its exact preprocessing in a reproducible batch or service deployment. Version model, data, and code; monitor latency, input quality, distribution drift, and performance, and retain audit records. Join scores back to the source grid for mapping, and compare them with other imagery and local reports.
5. Have trained responders review outputs and uncertainty before any action. Radar acquisition and processing delays, incomplete coverage, and model errors mean this is decision support, not a substitute for verified situational awareness.

Run the focused checks with `python3 -m unittest -v test_sar_flood`.
