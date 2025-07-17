#!/usr/bin/env python3

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from colorama import Fore, Style, init
import argparse

init(autoreset=True)

def list_pods():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    all_pods = v1.list_pod_for_all_namespaces().items

    for pod in all_pods:
      pod_phase = pod.status.phase
      namespace = pod.metadata.namespace
      name = pod.metadata.name
      node = pod.spec.node_name or "N/A"

      yield(pod_phase,namespace,name,node)


if __name__ == "__main__":
   for (phase,ns,name,node) in sorted(list_pods(), key=lambda k: k[3]):
        print(f"{phase:<10} {Fore.GREEN}{node}{Style.RESET_ALL}:"
              f"{Fore.BLUE}{ns}{Style.RESET_ALL}/{Fore.CYAN}{name}")
