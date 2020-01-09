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

import pandas as pd
from datetime import datetime

columnsNames = ['AS', 'TIME', 'TYPE', 'DEST', 'TO', 'FROM', 'NH', 'AS_PATH', 'PREVIOUS_BEST_PATH', 'ACTUAL_BEST_PATH',
                'PROCESSING']


class Log:
    def __init__(self, filepath):
        self.logFilePath = filepath
        self.fileName = filepath.split('/')[-1]
        self.ASNumber = str(int(self.fileName.split('_')[-1].split('.')[0]) + 1)
        self.file = open(self.logFilePath, "r")
        self.df = pd.DataFrame(columns=columnsNames)

    def __del__(self):
        self.file.close()

    def closer(self):
        self.file.close()

    def __str__(self):
        return "Log reader of file: " + str(self.logFilePath)

    def parsLine(self, line):
        datetime_object = datetime.strptime(line.split(' <FATAL> ')[0], '%Y-%m-%d %H:%M:%S.%f')
        attributes_object = line.split(' <FATAL> ')[1][1:-1].split(',')
        attributes_dict = {'AS': [self.ASNumber], 'TIME': [datetime_object]}
        for attr in attributes_object:
            attr = attr.replace('previus_best_path', 'previous_best_path')
            name = attr.replace(' ', '').split(':')[0].upper()
            obj = attr.replace(' ', '').split(':')[1]
            attributes_dict[name] = [obj]
        df2 = pd.DataFrame.from_dict(attributes_dict)
        self.df = self.df.append(df2, sort=False, ignore_index=True)

    def parseFile(self):
        for line in self.file.readlines():
            line = line.strip()
            self.parsLine(line)

    def get_df(self):
        return self.df

    def write_csv(self, out):
        self.df.to_csv(out, sep=',')
