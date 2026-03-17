#!/usr/bin/env python3

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from datetime import datetime, timezone
from rich.table import Table
from rich.console import Console
from rich import box
import argparse

parser=argparse.ArgumentParser()
parser.add_argument("filter", nargs="?", type=str, default=None, help="Filter on pod name")
parser.add_argument("-n","--namespace", type=str, default=None, help="Namespace filter")
parser.add_argument("-N","--node", type=str, default=None, help="Node Filter")
args=parser.parse_args()

def list_pods():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    all_pods = v1.list_pod_for_all_namespaces().items

    for pod in all_pods:
      pod_phase = pod.status.phase
      pod_ip=pod.status.pod_ip
      namespace = pod.metadata.namespace
      name = pod.metadata.name
      node = pod.spec.node_name or "N/A"

      if (args.filter and args.filter.lower() not in name.lower()): 
          continue

      if (args.node and node!=args.node): 
          continue

      if (args.namespace and namespace!=args.namespace): 
          continue

      labels = [f"{k}={v}" for k, v in (pod.metadata.labels or {}).items()]

      yield (pod_phase, namespace, name, pod_ip, node, labels)

console=Console()
table=Table(box=box.MINIMAL, show_header=True)

table.add_column("Phase", style="white")
table.add_column("Namespace", style="cyan")
table.add_column("Name", style="green")
table.add_column("IP", style="yellow")
table.add_column("Node", style="purple")
table.add_column("Labels", style="white")

for (phase,ns,name,ip,node,labels) in sorted(list_pods(), key=lambda k: k[2]):
    table.add_row(phase,ns,name,ip,node,"\n".join(labels))
    table.add_row("", "", "", "", "", "")
         
console.print(table)
