#!/usr/bin/env python3

from kubernetes import client, config, watch
from colorama import Fore, Back, Style, init

init(autoreset=True)

def get_pods():
  #Configs can be set in Configuration class directly or using helper utility
  config.load_kube_config()

  v1 = client.CoreV1Api()
  ret = v1.list_pod_for_all_namespaces(watch=False)

  for pod in ret.items:
    nodename=pod.spec.node_name
    namespace=pod.metadata.namespace

    yield(nodename,namespace)

def main():
    pods = sorted(set(get_pods()), key=lambda k: (k[0], k[1]))
    last_node = None

    for node, ns in pods:
        if node != last_node:
            if last_node is not None:
                print()
            print(f"{Fore.CYAN}{node}")
            last_node = node
        print(f"  {Fore.RESET}{ns}")

if __name__ == "__main__":
    main()
