#!/usr/bin/env python3

import os
import sys
import pprint
from kubernetes import client, config, watch
import argparse

parser=argparse.ArgumentParser()
parser.add_argument("--tail", type=int, default=200, help="Get the last [n] lines")
parser.add_argument("--filter", type=str, default=None, help="Pod name filter")
parser.add_argument("-g", "--grep",  type=str, default=None, help="Message filter")
parser.add_argument("-n","--namespace", type=str, default="", help="Namespace filter")
args=parser.parse_args()

name=args.filter if args.filter else ""

#Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()
ret = v1.list_pod_for_all_namespaces(watch=False)

for pod in ret.items:
  if (args.namespace and pod.metadata.namespace != args.namespace): continue
  if (name.lower() in pod.metadata.name.lower()):
    print (f"Logs et events du pod {pod.metadata.name}")
    print()

    blob=[]
    try:
      response = v1.read_namespaced_pod_log(name=pod.metadata.name,namespace=pod.metadata.namespace)
      for line in response.splitlines():
        if (args.grep==None or args.grep.lower() in line.lower()):
          blob.append(f"     {line}")
    except: 
      pass

    print("\n".join(blob[-args.tail:]))

    blob=[]
    try:
      stream = watch.Watch().stream(v1.list_namespaced_event, 
                                    name=pod.metadata.name, 
                                    namespace=pod.metadata.namespace, 
                                    timeout_seconds=1)
      for event in stream:
        line=event['object'].message
        if (args.grep==None or args.grep.lower() in line.lower()):
          blob.append(f"     {line}")
    except:
      pass

    print("\n".join(blob[-args.tail:]))

