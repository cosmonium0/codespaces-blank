import argparse
import ipaddress
import os
import sys
import time
from typing import Any, Dict, Optional

import requests
from jinja2 import Template
from rich.console import Console
from rich.table import Table

try:
    from . import config
except Exception:
    # fallback
    import config

console = Console()


def fetch_ip_data(ip: str, timeout: int = 5, retries: int = 2) -> Dict[str, Any]:
    base = f"https://ipinfo.io/{ip}/json"
    token = getattr(config, "IP_API_KEY", None)
    url = f"{base}?token={token}" if token else base

    for attempt in range(1, retries + 2):
        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, dict):
                raise ValueError("Unexpected response format")
            return data
        except Exception:
            if attempt <= retries:
                time.sleep(1)
                continue
            raise


def print_terminal_report(data: Dict[str, Any]) -> None:
    title = f"OPSEC Report for {data.get('ip', 'Unknown')}"
    table = Table(title=title)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", style="white")

    for key in sorted(data.keys()):
        table.add_row(str(key), str(data.get(key, "")))

    console.print(table)


def generate_html(data: Dict[str, Any], ip: str, template_path: Optional[str] = None) -> str:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_template = os.path.join(base_dir, "templates", "report.html")
    output_dir = os.path.join(base_dir, "output")

    template_path = template_path or default_template

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            tpl = Template(f.read())
    else:
        # Minimal fallback template
        fallback = (
            "<!doctype html>\n<html><head><meta charset=\"utf-8\"><title>OPSEC Report - {{ ip }}</title>"
            "<style>body{font-family:sans-serif;padding:20px}</style></head><body>"
            "<h1>OPSEC Report: {{ ip }}</h1>"
            "<ul>"
            "{% for k,v in data.items() %}<li><strong>{{ k }}:</strong> {{ v }}</li>{% endfor %}"
            "</ul></body></html>"
        )
        tpl = Template(fallback)

    rendered = tpl.render(ip=ip, data=data,
                          hostname=data.get("hostname", "Unknown"),
                          city=data.get("city", "Unknown"),
                          region=data.get("region", "Unknown"),
                          country=data.get("country", "Unknown"),
                          loc=data.get("loc", "Unknown"),
                          org=data.get("org", "Unknown"),
                          timezone=data.get("timezone", "Unknown"))

    out_path = os.path.join(output_dir, f"{ip}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    console.print(f"[bold cyan]✔ Saved: {out_path}[/]")
    return out_path


def validate_ip(ip_str: str) -> str:
    try:
        ipaddress.ip_address(ip_str)
        return ip_str
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid IP address: {ip_str}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="OPSEC IP report generator")
    p.add_argument("ip", type=validate_ip, help="IP address to query")
    return p


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    ip = args.ip
    console.print(f"[yellow]Fetching data for {ip}...[/]")

    try:
        data = fetch_ip_data(ip)
    except Exception as e:
        console.print(f"[red]Error fetching data: {e}[/]")
        return 2

    data["ip"] = ip
    print_terminal_report(data)
    try:
        generate_html(data, ip)
    except Exception as e:
        console.print(f"[red]Error generating HTML: {e}[/]")
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())