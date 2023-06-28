#!/usr/bin/env python3

import os, sys
import pprint
from kubernetes import client, config, watch
from datetime import datetime

try:
  name=sys.argv[1]
except:
  print ("please add a pod name or pod name part as argument")
  exit (0)

#Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()
ret = v1.list_pod_for_all_namespaces(watch=False)

history={}

while (True):
  for pod in ret.items:
    if (name.lower() in pod.metadata.name.lower()):
      podname=pod.metadata.name;
      status=pod.status.container_statuses[-1].state;

      if (podname not in history):
        history[podname]=""

      if (history[podname]!=status):
        print (podname,"status changed at",datetime.now(),"\n")
        print (status)
        print ()
        history[podname]=status

