#!/usr/bin/env python3

import os
import sys
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
    print (pod.metadata.name,)
    print ("="*(len(pod.metadata.name)+20))
    try:
      response = v1.read_namespaced_pod_log(name=pod.metadata.name,namespace=pod.metadata.namespace)
      for line in response.splitlines():
        print("     ",line)
    except: 
      pass
    
    print ("")

    break

    stream = watch.Watch().stream(v1.list_namespaced_event, 
                                  name=pod.metadata.name, 
                                  namespace=pod.metadata.namespace, 
                                  timeout_seconds=1)
    for event in stream:
      print("     ",event['object'].message)

    print("")
