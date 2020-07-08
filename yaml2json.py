#!/usr/bin/env python

import sys
import yaml
import json
from collections import OrderedDict

try:
  with open(sys.argv[1],"r") as f: document=f.read()
except:
  if (len(sys.argv)>1): sys.exit(0)
  print ("reading from stdin")
  document=sys.stdin

print (json.dumps(yaml.load(document),indent=2))
