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

import argparse
from argparse import ArgumentParser
import os
import shutil
from os import walk
import progressbar
from logFolderToCSV import LogFolder

parser = ArgumentParser()
parser.add_argument("-f", "--folder", dest="logFolder", required=False, type=str,
                    action="store", help="log files folder")
parser.add_argument("-ff", "--folders", dest="logFolderFolder", required=False, type=str,
                    action="store", help="where to find all the logs folders")
parser.add_argument("-o", "--out", dest="csv", required=False, type=str,
                    action="store", help="Folder where to save csv output")
parser.add_argument("-oo", "--outFolder", dest="csvFolder", required=False, type=str,
                    action="store", help="Folder where to save all csv outputs")
parser.add_argument('-w', '--warnings', dest='warn', action='store_true')
parser.add_argument('-nw', '--no-warnings', dest='warn', action='store_false')
parser.set_defaults(feature=False)

args = parser.parse_args()

if not (args.csv or args.csvFolder):
    parser.error('No out provided, you have to choose at least one output arg')
elif args.csv and not args.csvFolder:
    if os.path.exists(args.csv):
        if args.warn:
            raise ValueError('File csv already exists')
        else:
            os.remove(args.csv)
else:
    if os.path.exists(args.csvFolder):
        if args.warn:
            raise ValueError('File csv folder already exists')
        else:
            shutil.rmtree(args.csvFolder)
    os.makedirs(args.csvFolder)
    args.csv = args.csvFolder + "/csv.csv"

if not (args.logFolder or args.logFolderFolder):
    parser.error('No folders provided, you have to choose at least one type of folder to pass')
elif args.logFolder and not args.logFolderFolder:
    logger = LogFolder(args.logFolder)
    logger.sumuplogs()
    logger.write_csv(args.csv)
else:
    if args.csv and not args.csvFolder:
        raise ValueError('Impossible use folder folder with a single output file, you must use -oo')
    else:
        dirNames = list()
        for (dir_path, dir_names, filenames) in walk(args.logFolderFolder):
            dirNames.extend(dir_names)
            break
        with progressbar.ProgressBar(max_value=len(dirNames)) as bar:
            for dir_name in dirNames:
                args.logFolder = args.logFolderFolder + "/" + dir_name
                args.csv = args.csvFolder + "/" + dir_name + ".csv"
                logger = LogFolder(args.logFolder)
                logger.sumuplogs()
                logger.write_csv(args.csv)
                bar.update(bar.value + 1)
