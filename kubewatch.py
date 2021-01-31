#!/usr/bin/env python3

import os
import sys
from kubernetes import client, config, watch

config.load_kube_config(
    os.path.join(os.environ["HOME"], '.kube/config'))

v1 = client.CoreV1Api()

try: 
  ns=sys.argv[1]
except:
  ns="default"

stream = watch.Watch().stream(v1.list_namespaced_pod, ns)
for event in stream:
    print("Event: %s %s" % (event['type'], event['object'].metadata.name))
