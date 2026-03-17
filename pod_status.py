#!/usr/bin/env python3

import os, sys
import pprint
from kubernetes import client, config, watch
from datetime import datetime
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

history={}

while (True):
  for pod in ret.items:
    if (name.lower() in pod.metadata.name.lower()):
      podname=pod.metadata.name;
      container_state = pod.status.container_statuses[-1].state

      if container_state.running:
          color = Fore.GREEN
          status = "running"
      elif container_state.terminated:
          # tu peux aussi récupérer le code de sortie et reason
          reason = container_state.terminated.reason
          if reason:
              status = reason.lower()
          else:
              color = Fore.RED
              status = "terminated"
      elif container_state.waiting:
          reason = container_state.waiting.reason
          if reason:
              status = reason.lower()
          else:
             color = Fore.YELLOW
             status = "waiting"
      else:
          color = Style.Dim
          status = "unknown"
         
      if (podname not in history):
        history[podname]=""

      if (history[podname]!=status):
        print (f'status changed at {datetime.now()} -> {color}{status:^20}{Style.RESET_ALL} {podname:60}')
        history[podname]=status

