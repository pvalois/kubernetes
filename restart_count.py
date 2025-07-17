#!/usr/bin/env python3 

from kubernetes import client, config, watch
from colorama import Fore, Back, Style, init

init(autoreset=True)

def get_counters():
  config.load_kube_config()
  v1 = client.CoreV1Api()

  all_pods = v1.list_pod_for_all_namespaces(watch=False)
  res = {}

  for pod in all_pods.items:
    pod_ns = "namespace/"+pod.metadata.namespace
    pod_name = "pod/"+pod.metadata.name
    for container in pod.status.container_statuses:
      cont_name = "image/"+container.name
      if container.restart_count:
         if not pod_ns in res:
            res[pod_ns] = {}
            if not pod_name in res[pod_ns]:
              res[pod_ns][pod_name] = {}
            yield(pod_ns,pod_name,cont_name,container.restart_count)


for (namespace,pod,container,counter) in get_counters():
  print (f"{Fore.GREEN}{namespace} {Fore.YELLOW}{pod} {Fore.CYAN}{container} {Fore.RESET}{counter}")

