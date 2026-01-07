#!/usr/bin/env python3

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from datetime import datetime, timezone
from rich.table import Table
from rich.console import Console
from rich import box
import argparse

def list_pods():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    all_pods = v1.list_pod_for_all_namespaces().items

    for pod in all_pods:
      pod_phase = pod.status.phase
      namespace = pod.metadata.namespace
      name = pod.metadata.name
      node = pod.spec.node_name or "N/A"
      labels = [f"{k}={v}" for k, v in (pod.metadata.labels or {}).items()]

      yield (pod_phase, namespace, name, node, labels)

console=Console()
table=Table(box=box.MINIMAL, show_header=True)

table.add_column("Phase", style="white")
table.add_column("Namespace", style="cyan")
table.add_column("Name", style="green")
table.add_column("Node", style="white")
table.add_column("Labels", style="white")

for (phase,ns,name,node,labels) in sorted(list_pods(), key=lambda k: k[3]):
    table.add_row(phase,ns,name,node,"\n".join(labels))
    table.add_row("", "", "", "", "")
         
console.print(table)
