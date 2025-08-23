#!/usr/bin/env python3

import sys
import yaml
import json

try:
  with open(sys.argv[1],"r") as f: document=f.read()
except:
  if (len(sys.argv)>1): sys.exit(0)
  document=sys.stdin

print (json.dumps(yaml.load(document, Loader=yaml.FullLoader),indent=2))
