#!/usr/bin/env python

import subprocess
from argparse import ArgumentParser
import sys
import logging
import logging.handlers
from datetime import datetime
from time import sleep

if __name__ == "__main__":

  parser = ArgumentParser()

  my_log = logging.getLogger('MyLog')
  my_log.setLevel(logging.INFO)
  handlerlocale = logging.StreamHandler(stream=sys.stdout)
  my_log.addHandler(handlerlocale)

  parser.add_argument("-b", "--birdc", dest="bpath",
                      default="/users/mne/iof-bird-daemon/", action="store",
                      help="Path to the birdc binary")
  parser.add_argument("-n", "--node", dest="npath",
                      default="", action="store",
                      help="Node socket path")

  args = parser.parse_args()
  bird_path = args.bpath
  node_path = args.npath

  if bird_path[:-1] != '/':
    bird_path += '/'
  bird_path += 'birdc'


  while 1:
    d = []
    obj = {}
    output = subprocess.check_output([bird_path,'-s',node_path,' show route all'],universal_newlines=True)
    #output = subprocess.check_output(['cat','test1.out'],universal_newlines=True)
    for l in output.split('\n'):
      if len(l) == 0:
        break
      if l[0].isdigit():
        # Nuova destinazione
        if obj:
          d.append(obj)
        obj = {}
        obj['dest'] = l.split(' ')[0]
        obj['paths'] = []
      else:
        if "BGP.as_path" in l:
          obj['paths'].append(l.split(':')[1][1:])

    logme = {}
    logme['timestamp'] = str(datetime.now())
    logme['routes'] = d
    my_log.info("%s",logme)
    sleep(1)