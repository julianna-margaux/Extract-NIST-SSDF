NIST SSDF Parser

A Python parser that extracts the Secure Software Development Framework
(SSDF) practices and tasks from NIST SP 800-218 Version 1.1 and
converts the data into structured JSON, CSV, and TXT files.

Features

The parser extracts the following information from the SSDF table:

Practice ID

Practice name

Task ID

Task description

Notional implementation examples

References

After extraction, the script also prints a summary in the terminal
showing the number of practices, tasks, implementation examples,
reference entries, unique reference sources, and tasks grouped by SSDF
category and practice.

Repository Structure

nist-ssdf-parser/
├── parse_nist_ssdf.py
├── README.md
├── requirements.txt
├── input/
│   └── NIST.SP.800-218.pdf
└── output/
    ├── nist_ssdf_v1.1.json
    ├── nist_ssdf_v1.1.csv
    └── nist_ssdf_v1.1.txt

Requirements

Python 3

PyMuPDF

Install the required dependency with:

python3 -m pip install pymupdf

Alternatively, if the repository includes a requirements.txt file:

python3 -m pip install -r requirements.txt

Usage

Run the parser by providing the path to the NIST SP 800-218 PDF:

python3 parse_nist_ssdf.py input/NIST.SP.800-218.pdf --output-dir output

The --output-dir argument specifies where the generated files will be
saved. If it is not provided, the files are saved in the current
directory.

Output

The parser generates three files:

nist_ssdf_v1.1.json --- structured JSON representation of the
extracted SSDF data.

nist_ssdf_v1.1.csv --- CSV representation for spreadsheet and
data-processing use.

nist_ssdf_v1.1.txt --- human-readable text representation.

Each extracted task contains the following fields:

{
  "practice_id": "PO.1",
  "practice_name": "Define Security Requirements for Software Development",
  "task_id": "PO.1.1",
  "task_description": "...",
  "notional_implementation_examples": [
    "..."
  ],
  "references": {
    "BSAFSS": "..."
  }
}

SSDF Categories

The extracted practices are organized under the four main SSDF groups:

PO --- Prepare the Organization

PS --- Protect the Software

PW --- Produce Well-Secured Software

RV --- Respond to Vulnerabilities

Source

The dataset is extracted from NIST Special Publication 800-218, Secure
Software Development Framework (SSDF) Version 1.1: Recommendations for
Mitigating the Risk of Software Vulnerabilities.

This repository does not modify the SSDF framework. It converts
information from the document into structured formats for easier
processing and analysis.
