#!/usr/bin/env python3

import argparse
import csv
import json
import sys

from collections import defaultdict
from kubernetes import client, config

from rich.table import Table
from rich.table import box
from rich.console import Console


def load_config():
    try:
        config.load_incluster_config()
    except Exception:
        config.load_kube_config()


def get_ingress_routes():
    api = client.NetworkingV1Api()
    ingresses = api.list_ingress_for_all_namespaces()

    routes = defaultdict(list)

    for ing in ingresses.items:
        ns = ing.metadata.namespace
        tls_hosts = set()
        for tls in ing.spec.tls or []:
            tls_hosts.update(tls.hosts or [])

        for rule in ing.spec.rules or []:
            if not rule.http:
                continue

            host = rule.host or ""
            for path in rule.http.paths:
                svc = path.backend.service
                if not svc:
                    continue

                routes[(ns, svc.name)].append({
                    "host": host,
                    "path": path.path or "/",
                    "port": svc.port.number or svc.port.name,
                    "tls": host in tls_hosts
                })

    return routes


def collect_data():
    discovery = client.DiscoveryV1Api()
    slices = discovery.list_endpoint_slice_for_all_namespaces()
    ingress_routes = get_ingress_routes()

    rows = []

    for es in slices.items:
        ns = es.metadata.namespace
        svc_name = es.metadata.labels.get("kubernetes.io/service-name")
        if not svc_name:
            continue

        svc_dns = f"{svc_name}.{ns}.svc.cluster.local"
        routes = ingress_routes.get((ns, svc_name), [])

        ports = [ { "port": p.port, "protocol": p.protocol or "TCP" } for p in es.ports or [] if p.port ]

        for ep in es.endpoints:
            ready = ep.conditions.ready
            for addr in ep.addresses or []:
                if ports:
                    for p in ports: 
                        rows.append( build_row( ns, svc_name, addr, f"{p['port']}/{p['protocol']}", svc_dns, routes, ready))
                else:
                    rows.append(build_row(ns, svc_name, addr, None, svc_dns, routes, ready))

    return rows


def build_row(ns, svc, ip, port, dns, routes, ready):
    return {
        "namespace": ns,
        "service": svc,
        "endpoint_ip": ip,
        "port": port,
        "service_dns": dns,
        "ingress_urls": [
            f"{'https' if r['tls'] else 'http'}://{r['host']}{r['path']}"
            for r in routes
        ],
        "ready": ready
    }


def print_table(rows):
    table = Table(box=box.MINIMAL)

    table.add_column("Namespace", style="white")
    table.add_column("Service", style="cyan")
    table.add_column("Endpoint IP", style="yellow")
    table.add_column("Port", style="white")
    table.add_column("Service DNS", style="green")
    table.add_column("Ingress URLS", style="yellow")
    table.add_column("Ready", style="white")


    for r in rows:
        table.add_row(
            r["namespace"],
            r["service"],
            r["endpoint_ip"],
            r["port"],
            r["service_dns"],
            "\n".join(r["ingress_urls"]) if r["ingress_urls"] else "",
            str(r["ready"])
        )

    console=Console()
    console.print(table) 

def output_json(rows):
    data = json.dumps(rows, indent=2)
    print(data)


def output_csv(rows):
    fieldnames = [
        "namespace",
        "service",
        "endpoint_ip",
        "port",
        "service_dns",
        "ingress_urls",
        "ready"
    ]

    writer = csv.DictWriter(sys.stdout,fieldnames=fieldnames)
    writer.writeheader()

    for r in rows:
        row = r.copy()
        row["ingress_urls"] = ";".join(r["ingress_urls"])
        writer.writerow(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["json", "csv"])
    args = parser.parse_args()

    load_config()
    rows = collect_data()

    if args.format == "json": output_json(rows) 
    elif args.format == "csv": output_csv(rows)
    else:
      print_table(rows)


if __name__ == "__main__":
    main()
