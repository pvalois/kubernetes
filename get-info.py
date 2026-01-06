#!/usr/bin/env python3

import os, sys, json, datetime
from kubernetes import client, config, watch

config.load_kube_config()

try:
  name=sys.argv[1]
except:
  name=""

v1 = client.CoreV1Api()
ret = v1.list_pod_for_all_namespaces(watch=False)

def json_default(obj):
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

filtered = [
    pod.to_dict()
    for pod in ret.items
    if name.lower() in pod.metadata.name.lower()
]

print(json.dumps(filtered, default=json_default, indent=2))
