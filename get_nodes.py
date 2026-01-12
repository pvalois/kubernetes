#!/usr/bin/env python3

import humanize
from kubernetes import client, config
from rich.console import Console
from rich.table import Table, box

def parse_resource_quantity(quantity: str) -> int:
    """
    Convertit une quantité Kubernetes en octets (int).
    Exemples : "123Ki" -> 126, "2Gi" -> 2147483648, "123456" -> 123456 octets
    """
    try:
        quantity = quantity.strip()
        if quantity.endswith("Ki"):
            return int(quantity[:-2]) * 1024
        elif quantity.endswith("Mi"):
            return int(quantity[:-2]) * 1024**2
        elif quantity.endswith("Gi"):
            return int(quantity[:-2]) * 1024**3
        elif quantity.endswith("Ti"):
            return int(quantity[:-2]) * 1024**4
        else:
            return int(quantity)  # octets purs
    except Exception:
        return 0

def humanize_quantity(quantity: str) -> str:
    bytes_val = parse_resource_quantity(quantity)
    return humanize.naturalsize(bytes_val, binary=True)

def main():
    console = Console()
    config.load_kube_config()
    v1 = client.CoreV1Api()

    nodes = v1.list_node().items

    table = Table(box=box.MINIMAL)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("IP", style="white", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Role", style="magenta")
    table.add_column("CPU (cores)", justify="right")
    table.add_column("Memory", justify="right")
    table.add_column("Disk Capacity", justify="right")
    table.add_column("Disk Used %", justify="right")
    table.add_column("Taints", style="yellow")  # Nouvelle colonne

    for node in nodes:
        name = node.metadata.name
        ip = None
        
        for address in node.status.addresses:
            if address.type == "InternalIP":
                ip = address.address
                break

        # Status Ready or Not
        conditions_dict = {cond.type: cond.status for cond in node.status.conditions}
        status = "Ready" if conditions_dict.get("Ready") == "True" else "NotReady"
        # Conditions messages
        cond_msgs = [f'{cond.message}' for cond in node.status.conditions if cond.status == "True" and cond.message]
        status_str = "\n".join(cond_msgs) if cond_msgs else status

        # Role detection (master, worker, etc)
        labels = node.metadata.labels
        roles = []
        for key in labels:
            if key.startswith("node-role.kubernetes.io/"):
                role = key.split("/")[-1]
                roles.append(role)
        role = ",".join(roles) if roles else "worker"

        # CPU capacity (in cores)
        cpu = node.status.capacity.get("cpu", "0")

        # Memory capacity (humanized)
        mem = node.status.capacity.get("memory", "0")
        mem_hum = humanize_quantity(mem)

        # Disk capacity (humanized) and usage %
        disk_cap = node.status.capacity.get("ephemeral-storage", "0")
        disk_hum = humanize_quantity(disk_cap)
        disk_alloc = node.status.allocatable.get("ephemeral-storage", "0")
        try:
            used_bytes = parse_resource_quantity(disk_cap) - parse_resource_quantity(disk_alloc)
            usage_percent = (used_bytes / parse_resource_quantity(disk_cap)) * 100 if parse_resource_quantity(disk_cap) > 0 else 0
            usage_percent_str = f"{usage_percent:.1f}%"
        except Exception:
            usage_percent_str = "N/A"

        # Taints
        taints = node.spec.taints or []
        taints_str = ", ".join([f"{t.key}={t.value}:{t.effect}" if t.value else f"{t.key}:{t.effect}" for t in taints]) or "-"

        table.add_row(name, ip, status_str, role, cpu, mem_hum, disk_hum, usage_percent_str, taints_str)

    console.print(table)

if __name__ == "__main__":
    main()
