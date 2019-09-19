import glob
import sys
import code  # code.interact(local=dict(globals(), **locals()))
import pandas as pd
from prettytable import PrettyTable
from collections import defaultdict
from pprint import pprint

folder = sys.argv[1]

upC, instC = 0, 0
maxtime = float("-inf")
node2events = {}

for file in glob.glob(folder+"/*.csv"):
    node = file.split('/')[-1].strip('_log.csv')
    if node == 'X1':
        continue
    data = pd.read_csv(file, sep='|')
    updatesCounter = len(data[data.EVENT_TYPE == 'UpdateRX'])
    routeInstallmentCounter = len(data[data.EVENT_TYPE == 'INSTALLED_ROUTE'])
    upC += updatesCounter
    instC += routeInstallmentCounter
    maxtime = max(maxtime, max(data.TIME))
    node = file.split('/')[-1].strip('_log.csv')
    node2events[node] = data


t = PrettyTable()
t.field_names = ["#Updates", "#ROUTE_INSTALLMENTs", "CONV_TIME"]
t.add_row([upC, instC, maxtime])
print(t)


'''import matplotlib.pyplot as plt
import numpy as np

colors = ['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#a65628','#f781bf','#999999']

counter = 0
for node in node2events:
    events = node2events[node]
    uprx=events[events.EVENT_TYPE=='UpdateRX']
    instrt=events[events.EVENT_TYPE=='INSTALLED_ROUTE']
    plt.plot(uprx.TIME, [counter]*len(uprx.TIME), '+', c=colors[counter], markersize=12)
    plt.plot(instrt.TIME, [counter]*len(instrt.TIME), 'X', c=colors[counter])
    counter+=1
plt.show()'''

code.interact(local=dict(globals(), **locals()))

def popOldestEvent(node2events):
    


ft = PrettyTable()
ft.field_names=['Y1', 'X2', 'Y2', 'X3', 'Y3', 'X4']
ft.add_row(['st']*6)
lastrow=['st']*6

event=popOldestEvent(node2events):
