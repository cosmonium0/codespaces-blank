# OPSEC Tool

Small utility to fetch IP geolocation / ASN info (via ipinfo.io) and render a simple HTML report.

## Install

From the repository root create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r opsec-tool/requirements.txt
```

## Usage

Run the tool with an IP address:

```bash
python3 opsec-tool/main.py 8.8.8.8
```

Output HTML will be written to the `output/` directory at the repository root, e.g. `output/8.8.8.8.html`.

## API Token (optional)

If you have an `ipinfo.io` token, set it in the environment as `IP_API_KEY` before running to avoid rate limits and gain extended fields:

```bash
export IP_API_KEY=your_token_here
python3 opsec-tool/main.py 1.2.3.4
```

## Notes

- The script validates IP addresses and will exit with a non-zero code on errors.
- If `templates/report.html` is missing, the script will use a minimal built-in template.
- Feel free to request a README expansion, tests, or a small CLI wrapper.

