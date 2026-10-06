# NIST SSDF Parser

A Python parser that extracts the Secure Software Development Framework (SSDF) practices and tasks from **NIST SP 800-218 Version 1.1** and converts the extracted data into JSON, CSV, and TXT formats.

## Features

The parser extracts the following information:

- Practice ID
- Practice Name
- Task ID
- Task Description
- Notional Implementation Examples
- References

The program also displays a summary in the terminal showing the number of practices, tasks, implementation examples, references, and tasks under each SSDF category.

## Repository Structure

```text
nist-ssdf-parser/
├── parse_nist_ssdf.py
├── README.md
├── input/
│   └── NIST.SP.800-218.pdf
└── output/
    ├── nist_ssdf_v1.1.json
    ├── nist_ssdf_v1.1.csv
    └── nist_ssdf_v1.1.txt
```

## Requirements

- Python 3
- PyMuPDF

Install PyMuPDF using:

```bash
python3 -m pip install pymupdf
```

## Usage

Run the parser using:

```bash
python3 parse_nist_ssdf.py input/NIST.SP.800-218.pdf --output-dir output
```

The `--output-dir` argument specifies where the generated files will be saved.

If no output directory is provided, the files will be saved in the current directory.

## Output

The parser generates three output files:

- `nist_ssdf_v1.1.json` - Structured JSON data
- `nist_ssdf_v1.1.csv` - CSV format for spreadsheets and data processing
- `nist_ssdf_v1.1.txt` - Human-readable text format

Each extracted task follows this structure:

```json
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
```

## SSDF Categories

The SSDF practices are grouped into four main categories:

- **PO** - Prepare the Organization
- **PS** - Protect the Software
- **PW** - Produce Well-Secured Software
- **RV** - Respond to Vulnerabilities

## Source

The data is extracted from:

**NIST Special Publication 800-218**  
**Secure Software Development Framework (SSDF) Version 1.1: Recommendations for Mitigating the Risk of Software Vulnerabilities**
