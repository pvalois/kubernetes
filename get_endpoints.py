#!/usr/bin/env python3

import time
from kubernetes import client, config
from rich.console import Console
from rich.table import Table, box
from urllib3.exceptions import ProtocolError, ReadTimeoutError


# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------

def load_config():
    try:
        config.load_incluster_config()
    except Exception:
        config.load_kube_config()


# ---------------------------------------------------------------------
# Safe low-level API calls (no OpenAPI objects)
# ---------------------------------------------------------------------

def safe_call(path, retries=5, delay=1):
    api = client.ApiClient()

    for _ in range(retries):
        try:
            data, status, _ = api.call_api(
                path,
                "GET",
                response_type="object",
                _request_timeout=5,
            )
            if isinstance(data, dict):
                return data
        except (ValueError, ProtocolError, ReadTimeoutError):
            pass

        time.sleep(delay)

    return {}  # jamais d'exception


# ---------------------------------------------------------------------
# Collect Ingress → Service mapping
# ---------------------------------------------------------------------

def collect_ingresses():
    ingress_map = {}
    data = safe_call("/apis/networking.k8s.io/v1/ingresses")

    for ing in data.get("items") or []:
        meta = ing.get("metadata") or {}
        spec = ing.get("spec") or {}

        ns = meta.get("namespace")
        for rule in spec.get("rules") or []:
            host = rule.get("host")
            http = rule.get("http") or {}

            for path in http.get("paths") or []:
                backend = path.get("backend") or {}
                service = (backend.get("service") or {}).get("name")

                if ns and service and host:
                    ingress_map.setdefault((ns, service), set()).add(host)

    return ingress_map


# ---------------------------------------------------------------------
# Collect EndpointSlices
# ---------------------------------------------------------------------

def collect_data():
    rows = []
    ingress_map = collect_ingresses()
    data = safe_call("/apis/discovery.k8s.io/v1/endpointslices")

    for es in data.get("items") or []:
        meta = es.get("metadata") or {}
        labels = meta.get("labels") or {}

        ns = meta.get("namespace", "-")
        svc = labels.get("kubernetes.io/service-name", "-")
        service_dns = f"{svc}.{ns}.svc.cluster.local"

        endpoints = es.get("endpoints") or []
        ports = es.get("ports") or []

        for ep in endpoints:
            conditions = ep.get("conditions") or {}
            ready = conditions.get("ready", False)

            for addr in ep.get("addresses") or []:
                for port in ports or [{}]:
                    rows.append({
                        "namespace": ns,
                        "service": svc,
                        "endpoint_ip": addr,
                        "port": port.get("port", "-"),
                        "service_dns": service_dns,
                        "ingress_urls": ", ".join(
                            sorted([f"http://{url}" for url in ingress_map.get((ns, svc), [])])
                        ) or "-",
                        "ready": "[bright_green]YES[/bright_green]" if ready else "[bright_red]NO[/bright_red]",
                    })

    return rows


# ---------------------------------------------------------------------
# Render with Rich
# ---------------------------------------------------------------------

def render_table(rows):
    table = Table(box=box.SIMPLE_HEAVY)

    table.add_column("Namespace", style="bright_white", overflow="ellipsis", no_wrap=True)
    table.add_column("Service", style="bright_cyan", overflow="ellipsis", no_wrap=True)
    table.add_column("Endpoint ip", style="bright_white", overflow="ellipsis", no_wrap=True)
    table.add_column("Port", style="purple", overflow="ellipsis", no_wrap=True, justify="right")
    table.add_column("Service dns", style="bright_yellow", overflow="ellipsis", no_wrap=True)
    table.add_column("Ingress urls", style="bright_green", overflow="ellipsis", no_wrap=True)
    table.add_column("Ready", style="bright_white", overflow="ellipsis", no_wrap=True, justify="center")

    for r in rows:
        table.add_row(
            r["namespace"],
            r["service"],
            r["endpoint_ip"],
            str(r["port"]),
            r["service_dns"],
            r["ingress_urls"],
            r["ready"],
        )

    Console().print(table)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    load_config()
    rows = collect_data()
    render_table(rows)


if __name__ == "__main__":
    main()
