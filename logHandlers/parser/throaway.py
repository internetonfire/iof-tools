import pandas as pd
framelist = []
for i in range(10, 102, 10):
    print(i)
    p = pd.read_pickle('/home/leonardo/progetti/2019/Fed4Fire/data/RES-{}-DPC.pickle'.format(i))
    try:
        p.index.set_levels([i], level=0, inplace=True)
        framelist.append(p)
    except ValueError:
        pass
pp = pd.concat(framelist)
print(pp)
pp.to_pickle('/tmp/RES-DPC.pickle')



