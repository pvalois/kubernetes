#!/usr/bin/env python3

import os
from kubernetes import client, config, watch

#Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()
print("Listing pods in pending state :\n")

ret = v1.list_pod_for_all_namespaces(watch=False)
for pod in ret.items:
  if (pod.status.phase == 'Pending'):
    print ("%-30s : %s," %(pod.metadata.name,pod.status.conditions[0].message))
