#!/usr/bin/env python3

import os, sys
import pprint
from kubernetes import client, config, watch
from rich.table import Table
from rich.table import box
from rich.console import Console

try:
  name=sys.argv[1]
except:
  name=""

#Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()
ret = v1.list_pod_for_all_namespaces(watch=False)

table = Table(box=box.MINIMAL)
table.add_column("Pod Name", style="white")
table.add_column("Node", style="cyan")
table.add_column("Node IP", style="green")
table.add_column("Pod Ip", style="yellow")

for pod in sorted(ret.items, key=lambda x: x.metadata.name):
  node = pod.spec.node_name or ""
  node_ip = pod.status.host_ip or ""
  pod_ip = pod.status.pod_ip
  if (pod_ip == node_ip): pod_ip=""
  table.add_row(pod.metadata.name,node,node_ip,pod_ip)

console=Console()
console.print(table)

