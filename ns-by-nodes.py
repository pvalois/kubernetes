#!/usr/bin/env python3

import os
import sys
import pprint
import json
from dumper import dump
from kubernetes import client, config, watch
from pprint import pprint

kubecmd="kubectl"
command=" ".join(sys.argv[2:])

#Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()
ret = v1.list_pod_for_all_namespaces(watch=False)

a={}
for pod in ret.items:
  nodename=pod.spec.node_name
  namespace=pod.metadata.namespace
  keyname=nodename+" "+namespace

  try:
    a[keyname]+=1
  except:
    a[keyname]=1

olds=""
for key in sorted(a):
  s=key.split(" ")[0]
  if (s!=olds):
    print ()
    olds=s
  print (key,a[key])
