#!/usr/bin/env python3
"""Score prepared SAR observations with a logistic flood-screening model."""

import argparse
import csv
import json
import math
import re
import sys


FEATURES = ("before_db", "after_db", "delta_db")
FIELDS = ("pixel_id", "latitude", "longitude", "before_db", "after_db")


def finite_number(value, name):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a finite number") from None
    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite number")
    return number


def load_model(path):
    with open(path, encoding="utf-8") as source:
        model = json.load(source)
    if not isinstance(model, dict) or not isinstance(model.get("weights"), dict):
        raise ValueError("model must contain a weights object")
    weights = model["weights"]
    if set(weights) != set(FEATURES):
        raise ValueError(f"model weights must contain exactly: {', '.join(FEATURES)}")
    return (
        finite_number(model.get("bias"), "model bias"),
        {name: finite_number(weights[name], f"weight {name}") for name in FEATURES},
    )


def score(before, after, bias, weights):
    delta = after - before
    logit = bias + weights["before_db"] * before + weights["after_db"] * after + weights["delta_db"] * delta
    if not math.isfinite(logit):
        raise ValueError("model score is not finite")
    if logit >= 0:
        return 1 / (1 + math.exp(-logit))
    exp_logit = math.exp(logit)
    return exp_logit / (1 + exp_logit)


def read_observations(path, bias, weights, threshold):
    results = []
    with open(path, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None or any(reader.fieldnames.count(field) != 1 for field in FIELDS):
            raise ValueError(f"CSV must contain each required column once: {', '.join(FIELDS)}")
        for line, row in enumerate(reader, start=2):
            try:
                pixel_id = row["pixel_id"]
                if not pixel_id or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", pixel_id):
                    raise ValueError("pixel_id must start with a letter or digit and contain only letters, digits, _, -, or .")
                latitude = finite_number(row["latitude"], "latitude")
                longitude = finite_number(row["longitude"], "longitude")
                if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
                    raise ValueError("latitude or longitude is out of range")
                before = finite_number(row["before_db"], "before_db")
                after = finite_number(row["after_db"], "after_db")
                probability = score(before, after, bias, weights)
                results.append((pixel_id, latitude, longitude, before, after, probability, int(probability >= threshold)))
            except ValueError as exc:
                raise ValueError(f"CSV row {line}: {exc}") from exc
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("observations", help="CSV of prepared, co-registered SAR observations")
    parser.add_argument("--model", required=True, help="JSON logistic model coefficients")
    parser.add_argument("--threshold", type=float, default=0.5, help="screening threshold between 0 and 1 (default: 0.5)")
    args = parser.parse_args(argv)
    try:
        threshold = finite_number(args.threshold, "threshold")
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
        bias, weights = load_model(args.model)
        results = read_observations(args.observations, bias, weights, threshold)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"error: {exc}\n")
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow((*FIELDS, "flood_probability", "flagged"))
    for pixel_id, latitude, longitude, before, after, probability, flagged in results:
        writer.writerow((pixel_id, latitude, longitude, before, after, f"{probability:.6f}", flagged))


if __name__ == "__main__":
    main()
