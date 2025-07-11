#!/usr/bin/env python3

import sys
import yaml 
from pprint import pprint


try:
  with open(sys.argv[1],"r") as f: document=f.read()
except:
  if (len(sys.argv)>1): sys.exit(0)
  print ("reading from stdin")
  document=sys.stdin

yamls=[]
yamlstr=""
for line in document.splitlines():
  if (line=="---"): 
    yamls.append(yamlstr)
    yamlstr=""
  yamlstr+=line+"\n"

for yamlstr in yamls:
  try:
    d=yaml.load(yamlstr, Loader=yaml.FullLoader)
    kind=(d["kind"])
    name=(d["metadata"]["name"])
    filename=kind+"-"+name+".yaml"
    f=open(filename,"w+")
    print(yamlstr, file=f)
    f.close()
  except:
    pass
