#!/usr/bin/env python3

import os
from kubernetes import client, config, watch

config.load_kube_config(
    os.path.join(os.environ["HOME"], '.kube/config'))

v1 = client.CoreV1Api()

stream = watch.Watch().stream(v1.list_namespaced_pod, "default")
for event in stream:
    print("Event: %s %s" % (event['type'], event['object'].metadata.name))
