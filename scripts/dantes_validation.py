#!/usr/bin/env python3
import requests
import sys
import json
import csv
from pathlib import Path

BASE_URL = "http://localhost:3000/"

def refactor_all():
    refactor_url = BASE_URL + "refactorAll"
    response = requests.post(
        refactor_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={}
    )
    response.raise_for_status()
    return response.json()
    
def run_detection(test_smell_file):
    detection_url = BASE_URL + "process-input"
    
    with open(test_smell_file, "r") as f:
        input_text = f.read()

    response = requests.post(
        detection_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"inputText": input_text}
    )
    response.raise_for_status()
    return response.json()

def get_refactored_source(refactor_result):
    if isinstance(refactor_result, str):
        try:
            refactor_result = json.loads(refactor_result)
        except json.JSONDecodeError as error:
            raise ValueError("Refactor response is not valid JSON") from error

    if not isinstance(refactor_result, list) or not refactor_result or not isinstance(refactor_result[0], str):
        raise ValueError("Refactor response does not contain Java source as its first item")

    return refactor_result[0]

def load_test_files(csv_file):
    test_files = []
    with open(csv_file, newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file, delimiter=";")
        if not reader.fieldnames or "PathFile" not in reader.fieldnames:
            raise ValueError("CSV must contain a PathFile column")

        for row_number, row in enumerate(reader, start=2):
            test_file = (row.get("PathFile") or "").strip()
            test_files.append((row_number, Path(test_file) if test_file else None))

    return test_files

def refactor_file(test_file):
    run_detection(test_file)
    refactor_result = refactor_all()["retVal"]
    source = get_refactored_source(refactor_result)
    test_file.write_text(source, encoding="utf-8")
    return test_file

def refactor_csv(csv_file):
    test_files = load_test_files(csv_file)
    total = len(test_files)
    failures = 0

    for index, (row_number, test_file) in enumerate(test_files, start=1):
        try:
            if test_file is None:
                raise ValueError(f"Missing PathFile value on CSV row {row_number}")
            if not test_file.is_file():
                raise FileNotFoundError(f"PathFile on CSV row {row_number} does not exist: {test_file}")

            refactor_file(test_file)
            print(f"[{index}/{total}] Replaced {test_file}")
        except Exception as error:
            failures += 1
            print(f"[{index}/{total}] Failed {test_file or '<empty>'}: {error}", file=sys.stderr)

    print(f"Finished: {total - failures} succeeded, {failures} failed")
    return failures


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/dantes_validation.py <csv_file>")
        sys.exit(1)

    sys.exit(1 if refactor_csv(sys.argv[1]) else 0)