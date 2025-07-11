#!/usr/bin/env python3

import os
import sys
import pprint
from kubernetes import client, config, watch

try:
  name=sys.argv[1]
except:
  name=""

kubecmd="microk8s kubectl"
command=" ".join(sys.argv[2:])

#Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()
ret = v1.list_pod_for_all_namespaces(watch=False)
for pod in ret.items:
  if (name.lower() in pod.metadata.name.lower()):
    print (kubecmd+" exec -t -i -n "+pod.metadata.namespace+" "+pod.metadata.name+" -- "+command)
    os.system (kubecmd+" exec -t -i -n "+pod.metadata.namespace+" "+pod.metadata.name+" -- "+command)
