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

def coagulate():
    pods = sorted(set(get_pods()), key=lambda k: (k[0], k[1]))
    for node,ns in pods: 
      yield ((node,ns))

def main():

    results=list(coagulate())
    list_nodes=sorted(set([node for node,ns in results]))

    for n in list_nodes:
      namespaces=sorted([ns for node, ns in results if node==n])
      print (f"{Fore.GREEN}{n} {Fore.RESET}({len(namespaces)})\n")
      for ns in namespaces:
        print (f"   {Fore.CYAN}{ns}")
      print ("")

if __name__ == "__main__":
    main()
