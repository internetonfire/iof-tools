import glob
import sys
import pandas as pd
from prettytable import PrettyTable
from collections import defaultdict
from pprint import pprint
from policy import policy
from util.routing_table import Route
import code  # code.interact(local=dict(globals(), **locals()))

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

allRTinstallments=[]
ft = PrettyTable()
ft.field_names = ['TIME', 'Y1', 'X2', 'Y2', 'X3', 'Y3', 'X4']
ft.add_row([float('0.000'), '1', '1', '11', '11', '111', '111'])
for node in node2events:
    events = node2events[node]
    inst = events[events.EVENT_TYPE == 'INSTALLED_ROUTE']
    for index, row in inst.iterrows():
        remind = (row.TIME, row.AS_PATH, node)
        allRTinstallments.append(remind)

nodes = ['Y1', 'X2', 'Y2', 'X3', 'Y3', 'X4']
def inst2string(time, aspath, node):
    retval = [time]
    for n in nodes:
        if n != node:
            retval.append('\"\"')
        else:
            r=Route('d', {'AS_PATH': aspath})
            pref=policy(node,r)
            retval.append(bin(pref)[2:])
    return retval

for rti in allRTinstallments:
    ft.add_row(inst2string(*rti))

print("Time progress of route installments after link failure")
ft.sortby = "TIME"
for n in nodes:
    ft.align[n] = "r"
print(ft)

#code.interact(local=dict(globals(), **locals()))


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

'''

def popOldestEvent(node2events):
    



ft.add_row(['st']*6)
lastrow=['st']*6

event=popOldestEvent(node2events):'''
