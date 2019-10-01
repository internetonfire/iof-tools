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

from os import listdir
from os.path import isfile, join
import pandas as pd
from logToCSV import Log

columnsNames = ['AS', 'TIME', 'TYPE', 'DEST', 'TO', 'FROM', 'NH', 'AS_PATH', 'PREVIOUS_BEST_PATH', 'ACTUAL_BEST_PATH',
                'PROCESSING']


class LogFolder:
    def __init__(self, folderpath):
        self.logFolderPath = folderpath
        self.fileList = [self.logFolderPath + "/" + f for f in listdir(self.logFolderPath) if isfile(join(self.logFolderPath, f))]
        self.df = pd.DataFrame(columns=columnsNames)

    def sumuplogs(self):
        for file in self.fileList:
            print(file)
            log = Log(file)
            log.parseFile()
            self.df = self.df.append(log.get_df(), sort=False, ignore_index=True)
        self.df = self.df.sort_values(by='TIME')

    def write_csv(self, csv):
        self.df.to_csv(csv, sep=',', na_rep="None", index_label="IDX")

    def reconfid(self):
        return self.df.loc[self.df['TYPE'] == 'RECONF'].index

    def iloc_test(self, id):
        print(self.df.iloc[id])
