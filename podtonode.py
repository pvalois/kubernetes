#!/usr/bin/env python3

import os
from kubernetes import client, config, watch

#Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()

ret = v1.list_pod_for_all_namespaces(watch=False)
for pod in ret.items:
  #print (vars(pod.metadata))
  print("%-60s\t%10s\t%s" % (pod.metadata.name, 
                        pod.status.phase,
                        pod.status.pod_ip))
