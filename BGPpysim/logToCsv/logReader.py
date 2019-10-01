#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
#
# Copyright (C) 2019  Mattia Milani <mattia.milani@studenti.unitn.it>

from argparse import ArgumentParser
from logFolderToCSV import LogFolder

parser = ArgumentParser()
parser.add_argument("-f", "--folder", dest="logFolder", required=True, type=str,
                    action="store", help="log files folder")
parser.add_argument("-o", "--out", dest="csv", required=True, type=str,
                    action="store", help="CSV file out")

args = parser.parse_args()

logger = LogFolder(args.logFolder)

logger.sumuplogs()
logger.write_csv(args.csv)
id = logger.reconfid()
print(id)
logger.iloc_test(id)
