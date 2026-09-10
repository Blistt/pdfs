# Generador de Constancias

A Streamlit form that generates Concertinos certificates as PDF files.

## Run locally

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

To generate the standalone sample, run `python generar_constancia.py`.

## Streamlit Community Cloud

Deploy `app.py` from this repository. Dependencies are declared in
`requirements.txt`. The Caladea fonts and their license are included in `fonts/`,
so no operating-system packages or `packages.txt` are needed.

The September 8, 2026 deployment failed during `apt-get update` because the
hosting environment referenced an expired Debian `bullseye-security` release.
Removing the system font dependency avoids that failing installation step.
Push this change to the deployed branch (`main`) so Streamlit rebuilds the app.

## Letter layout and preview

The preview below the fields updates when an edit is committed (press Tab or
click outside the field). **Descargar PDF** saves exactly the PDF shown there.
The preview includes zoom controls and displays both pages of a long letter.

Titles wrap and shrink from 18 pt down to 10 pt within the header, beside the
logo. The body shrinks from 12 pt down to 10 pt to fit one page, accounting for
the date, signature, and contact details. If it still does not fit, the letter
uses up to two pages at the largest size that fits. The closing block stays
together on the last page. Text that exceeds two readable pages produces a
message asking the user to shorten it; it is never silently clipped.

The viewer uses Streamlit's `pdf` extra; it needs no operating-system packages.

## Tests

```sh
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```
