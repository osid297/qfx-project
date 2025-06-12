# qfx-project

This repository provides a simple script to convert a credit-card PDF statement into a QFX file that can be imported into YNAB.

## Requirements

- Python 3.8+
- `pdfplumber` for extracting text from the statement PDF.

Install the dependency using pip:

```bash
pip install pdfplumber
```

## Usage

Run the converter with the path to your statement PDF and the desired output QFX file. Optionally provide account and bank IDs used by YNAB.

```bash
python pdf_to_qfx.py statement.pdf output.qfx --account-id 1234 --bank-id 111111111
```

The script attempts to parse lines formatted as `MM/DD Description Amount`. Adjust the regular expression in `pdf_to_qfx.py` if your statement layout differs.
