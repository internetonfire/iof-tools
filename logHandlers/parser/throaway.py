#==============================================================================
# Copyright (C) 2019-2024 Mattia Milani, Leonardo Maccari, Luca Baldesi, Lorenzo Ghiro, Michele Segata, Marco Nesler 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#==============================================================================
import pandas as pd
framelist = []
for i in range(10, 102, 10):
    print(i)
    p = pd.read_pickle('/home/leonardo/progetti/2019/Fed4Fire/data/RES-{}-DPC.pickle'.format(i))
    try:
        p.index.set_levels([i], level=0, inplace=True)
        framelist.append(p)
    except ValueError:
        print("Problems with {}".format(i))
        pass
pp = pd.concat(framelist)
print(pp)
pp.to_pickle('/tmp/RES-DPC.pickle')



