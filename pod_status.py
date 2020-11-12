#!/usr/bin/env python3

import os, sys
import pprint
from kubernetes import client, config, watch

try:
  name=sys.argv[1]
except:
  name=""

#Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()
ret = v1.list_pod_for_all_namespaces(watch=False)
for pod in ret.items:
  if (name.lower() in pod.metadata.name.lower()):
    print ("="*(len(pod.metadata.name)+20))
    print (pod.metadata.name)
    print ("="*(len(pod.metadata.name)+20))
    print (pod.status.container_statuses)
    if (pod.status.reason is not None): 
      print (pod.status.reason,end="\n")
    print ("")

