#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Stachl
LICENSE
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
@copyright: Copyright (c) 2011, w3agency.net, Leonardo Maccari
@author: Thomas Stachl <t.stachl@w3agency.net>, Leonardo Maccari leonardo.maccari@disi.unitn.it
@since: Mar 28, 2011
"""


from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError

class InheritConfigParser(SafeConfigParser):
    def get(self, section, option=None, default=""):
        try:
            return SafeConfigParser.get(self, section, option)
        except NoSectionError:
            for s in self._sections:
                if s.find(section) != -1:
                    try:
                        return SafeConfigParser.get(self, s, option)
                    except NoOptionError:
                        return SafeConfigParser.get(self, s.split(":")[1].strip(), option)

    def sections(self):
        real_sections = SafeConfigParser.sections(self)
        parsed_sections = []
        for section in real_sections:
            if ":" not in section:
                parsed_sections.append(section)
            else:
                parsed_sections.append(section.split(":")[0])
        return parsed_sections

    def items(self, section):
        try:
            return SafeConfigParser.items(self, section)
        except NoSectionError:
            for s in self._sections:
                if s.find(section) != -1:
                    # this section name includes the section name we're looking
                    # for
                    base_step = []
                    try:
                        # is it an existing section name? yes, then we
                        # navigated to the highest ancstor, return the contents
                        # of the stanza
                        return SafeConfigParser.items(self, section)
                    except NoSectionError:
                        # no section is named like this, add the content of the
                        # current stanza and climb to the father
                        base_step = SafeConfigParser.items(self, s)
                        return self.items(
                                s.split(":")[1].strip()) + base_step
