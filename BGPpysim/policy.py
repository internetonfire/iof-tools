'''
Here the policy used by all nodes to compute
the routes' preference is defined...
Change the function if you want to implement a different policy!
The current policy implements exactly the 'binary' policy
of the Fabrikant-Rexford paper

The preference table in the policy function lists the binary labels of paths before
X1 changes the advertisment of d.
- X1 starts advertising d via the AS_PATH = 'X1' which initially costs 11
- Then X1 will advertise d via the AS_PATH = 'P,X1' (prepending), which model the
change of cost between X1 and d. The cost will become 01... the cost of those paths starting with 01
...
'''

#aspath = rxaaspath ^ rxID
from util.routing_table import Route
import code  # code.interact(local=dict(globals(), **locals()))


def policy(nodeID, route):
    LOWEST_PREF = 0
    if 'AS_PATH' not in route.attr:
        return LOWEST_PREF
    aspath = route.as_path()+ ',' + nodeID
    state = 'START'
    bs = ""
    for c in aspath.split(","):
        if state == 'START' and 'P' in c:
            state = 'M'
        elif state == 'START' and 'X' in c:
            bs += '1'
            state = 'R'
        elif state == 'M' and 'X' in c:
            bs += '0'
            state = 'R'
        elif state == 'R' and 'X' in c:
            bs += '1'
        elif state == 'R' and 'Y' in c:
            bs += '0'
            state = 'MX'
        elif state == 'MX' and 'X' in c:
            state = 'R'

    '''for c in aspath.split(","):
        if state == 'START' and 'X' in c:
            bs += '1'
            state = 'A'
        elif state == 'START' and 'P' in c:
            state = 'B'
        elif state == 'A' and 'X' in c:
            bs += '1'
        elif state == 'A' and 'Y' in c:
            state = 'B'
        elif state == 'B' and 'X' in c:
            bs += '0'
            state = 'C'
        elif state == 'C' and 'X' in c:
            bs += '1'
            state = 'A'
            '''
    #code.interact(local=dict(globals(), **locals()))
    if state=='MX':
        bs=bs[:-1]
    #code.interact(local=dict(globals(), **locals()))
    return int('0b'+bs, 2)


def test():
    route = Route('dest', {'AS_PATH': 'P,X1,X2,Y2,X3,Y3'})
    cost = policy('X4', route)
    bincost = bin(cost)[2:]
    assert bincost == 0


if __name__ == "__main__":
    # test()
    route = Route('dest', {'AS_PATH': 'P,X1,X2,Y2,X3,Y3'})
    nodeid='X4'
    while(1):
        cost = policy(nodeid, route)
        bincost = bin(cost)[2:]
        print("The cost of", route.attr['AS_PATH'], 'for', nodeid, "is:")
        print("DEC =", cost, "\tBIN =", bincost)
        #print("insert new AS_PATH to continue.")
        print('new nodeid')
        nodeid = input()
        print('new aspath')
        route.attr['AS_PATH'] = input()


'''# Preference Table
    prefTab = {
        'X1': 11,
        'X1,Y1': 10,
        'X1,X2': 111,
        'X1,X2,Y2': 110,
        'X1,Y1,X2': 101,
        'X1,Y1,X2,Y2': 100,
        'X1,X2,X3': 1111,
        'X1,X2,X3,Y3': 1110,
        'X1,X2,Y2,X3': 1101,
        'X1,X2,Y2,X3,Y3': 1100,
        'X1,Y1,X2,X3': 1011,
        'X1,Y1,X2,X3,Y3': 1010,
        'X1,Y1,X2,Y2,X3': 1001,
        'X1,Y1,X2,Y2,X3,Y3': 1000,
    }

    if not aspath.startswith('X1,X1'):
        return int('0b'+str(prefTab[aspath]), 2)
    else:
        fakepath = ",".join(aspath.split(',')[1:])
        fakecost = str(prefTab[fakepath])
        #code.interact(local=dict(globals(), **locals()))
        return int('0b'+'0'+fakecost[1:], 2)'''
