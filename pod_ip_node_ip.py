#!/usr/bin/env python3

import os, sys
import pprint
from kubernetes import client, config, watch
from colorama import Fore, Back, Style, init

init(autoreset=True)

try:
  name=sys.argv[1]
except:
  name=""

#Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()
ret = v1.list_pod_for_all_namespaces(watch=False)

for pod in sorted(ret.items, key=lambda x: x.metadata.name):
  if (name.lower() in pod.metadata.name.lower()):
      print (f'{Fore.CYAN}{pod.metadata.name:50} {Fore.GREEN}{pod.status.host_ip:16} {Fore.RESET}{pod.status.pod_ip:16}')

