#!/usr/bin/env python3

from kubernetes import client, watch

w = watch.Watch()
v1 = client.CoreV1Api()
for ns in w.stream(v1.list_namespace):
    #Le code suivant va être exécuté à chaque namespace détecté, puis à chaque évènement touchant un namespace
    try:
      obj = ns['object']
      print("{}: {}".format(ns['type'], obj.metadata.name))
    except:
      continue
