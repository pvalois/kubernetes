#!/usr/bin/env python

import sys
import yaml
import json
from collections import OrderedDict

try:
  document=open(sys.argv[1],"r") 
except:
  if (len(sys.argv)>1): sys.exit(0)
  document=sys.stdin

now=0
cpt=0
buffer=['','','','','','','','','','','','','','','','','','','']
last=""

for line in document.readlines():

  keep=line.lstrip().rstrip()  
  indent=len(line) - len(keep)
  if (keep[0]=="-"): indent+=2


  if (indent>now):
    now=indent
    cpt+=1

  if (indent<now): 
    now=indent
    cpt-=1

  buffer[cpt]=keep

  if (indent<=now): 
    compose=";".join(buffer[1:cpt+1])
    #print (compose)
    if (last not in compose): 
      print (last) 
    last=compose
    
if (last not in compose): last
