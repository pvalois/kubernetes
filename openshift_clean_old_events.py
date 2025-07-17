#!/usr/bin/env python3

import os
import subprocess
import json
import datetime

#oc get events -o json -A | jq -r '"oc delete events \(.items[].metadata.name) -n \(.items[].metadata.namespace)"'

result=os.popen("oc get events -o json -A").read()
data=json.loads(result)

for item in data['items']:
  ns=(item['involvedObject']['namespace'])
  name=(item['metadata']['name'])
  timestamp=(item['lastTimestamp'])
  try:
    dt=datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
  except:
    continue
  if (datetime.datetime.now()-dt > datetime.timedelta(days=1)):
    print ("oc delete events %s -n %s" %(name,ns))
