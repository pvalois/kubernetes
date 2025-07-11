#!/usr/bin/env python3 

import sys, os

class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)

sys.stdout = Unbuffered(sys.stdout)

bloc=["---"]

for line in sys.stdin:
   line=line.strip()

   if ("receiveTimestamp" in line): 
      print (line, file=sys.stderr)

   if ("---" in line):
     if ("Evicted" in bloc):
       print ("\n".join(bloc))
     bloc=[]

   bloc.append(line)
  
