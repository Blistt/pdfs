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
