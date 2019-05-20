#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import getopt



class parameters():
    """ configuration parameters storage class."""

    def __init__(self, programName, neededParams):
        """ initialize the parameter class. needeParams/optionalParams are lists
        of couples in the form:
        "command line option"->[optionName, wantsValue,
                   defaultValue, usageMessage, type]
        optional parameters should always use False as default value, so they
        return False on getParam().

        ***Use only one-letter options***
        """

        self.parserString = ""
        self.neededParamsNames = {}
        self.neededParams = {}

        self.programName = programName

        self.setParams(neededParams)

    def setParams(self, neededParams):
        for p in neededParams:
            self.neededParamsNames[p[0]] = p[1]
            if p[1][1]:
                self.parserString += p[0][1]+":"
            else:
                self.parserString += p[0][1]

    def checkNeededParams(self):
        """ check if all needed params have been set """
        for clp, value in self.neededParamsNames.items():
            if value[0] not in self.neededParams:
                print >> sys.stderr, clp+" is a mandatory parameter "
                self.printUsage()
                sys.exit(1)

    def checkCorrectness(self):
        """ do some consistence checks here for the configuration parameters """
        self.checkNeededParams()
        if self.getParam("help"):
            return False
        return True

    def printUsage(self):
        """ print the usage of the program """
        print >> sys.stderr
        print >> sys.stderr, "usage ", self.programName+":"
        for pname, pvalue in self.neededParamsNames.items():
            print >> sys.stderr, " ", pname, pvalue[3]

    def getParam(self, paramName):
        """ return a configuration parameter """
        for pname, pvalue in self.neededParamsNames.items():
            if pvalue[0] == paramName:
                if paramName in self.neededParams:
                    return self.neededParams[paramName]

        print >> sys.stderr, "Coding error: param", paramName, "is not",\
            "among the available options"
        sys.exit(1)

    def printConf(self):
        """ just print all the configuration for debug """
        print ""
        for pname, pvalue in self.neededParams.items():
            print pname, pvalue

    def parseArgs(self):
        """ argument parser """
        try:
            opts, args = getopt.getopt(sys.argv[1:], self.parserString)
        except getopt.GetoptError, err:
            print >> sys.stderr,  str(err)
            self.printUsage()
            sys.exit(2)
        for option, v in opts:
            if option == "-h":
                self.printUsage()
                sys.exit(2)
            if option in self.neededParamsNames.keys():
                optionValue = self.neededParamsNames[option]
                if optionValue[1]:
                    self.neededParams[optionValue[0]] = optionValue[4](v)
                else:
                    self.neededParams[optionValue[0]] = True
            else:
                assert False, "unhandled option"
