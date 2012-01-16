#!/usr/bin/env python
""" Create an EAD Tag use report 
    Brian Tingle (c) 2012 UC Regents all rights reserved
    BSD license at bottom of file
"""
					# standard modules
import argparse
from collections import Counter
import fnmatch
import glob
import os
import pprint
import sys 
					# Pypi packages
					# http://pypi.python.org/pypi/lxml
from lxml import etree

# load ead.dtd.xml into DTD constant
DTD = etree.parse('ead.dtd.xml').getroot();
# xml version of the DTD created with http://nwalsh.com/perl/dtdparse/

def main(argv=None):
    # argument parser 
    parser = argparse.ArgumentParser(
        description='analyze EAD tag useage',
        epilog='recursively searches "*.xml" files in given dirs for EAD tags')
    parser.add_argument('dir', nargs='+', help='EAD XML corpus directory')
    parser.add_argument('-outfile', nargs='?', type=argparse.FileType('w'),
        help='output tag useage report', default=sys.stdout)
    # parse the args from the command line if none were supplied from the REPL
    if argv is None:
        argv = parser.parse_args()
     
    # set up dictionary to hold the stats
    stats = {}

    # loop through all files
    # http://stackoverflow.com/questions/2212643/
    # multiple dir arguments can be supplied
    for dir in argv.dir:
        # walk through all the files in the directory
        for root, subFolders, files in os.walk(dir):
            # check the file has a .xml extension
            # http://stackoverflow.com/questions/2186525/
            for filename in fnmatch.filter(files, '*.xml'):
                filePath = os.path.join(root, filename)
                analyze_file(filePath, stats)
    pp = pprint.PrettyPrinter(indent=4, stream=argv.outfile)
    pp.pprint(stats)

def analyze_file(file, stats):
    """analze the a file, update stats dictionary"""
    # check that the file is not zero length
    # http://stackoverflow.com/questions/2507808/
    if os.stat(file)[6]==0:
        return
    # open the file
    xml = etree.parse(file)
    # recursivly decend the xml (modifies stats "in place")
    count_elements(xml.getroot(),stats)

def count_elements(node, stats):
    """count elements and attributes used based on DTD"""
    # test that we are an element and not a comment nor processing instruction
    if isinstance(node, (etree._Comment, etree._ProcessingInstruction)):
        return

    # key the hash on the local name of the element
    key = node.xpath('local-name(.)')

    # get stats counter for the current element name, or set the default
    element_stats = stats.setdefault(key,  # <-- element name is dict key
             [0,               # <-- count for this element [0]    corpus
                [Counter(),    # <-- parent elements        [1][0] corpus
                 Counter(),    # <-- child elements         [1][1] dtd
                 Counter(),    # <-- child attributes       [1][2] dtd
                 Counter()]]   # <-- PCDATA                 [1][3] corpus
    )                          #               array address-^--^
             # some counters look for everything possible based on dtd
                            # some counters only observe the input corpus

    ## update the stats data structure
    # increment the count for this element
    stats[key][0] = element_stats[0] + 1                # count for this element 
    # note the parent element
    parent = node.xpath('local-name(..)')
    stats[key][1][0][parent] += 1                       # Counter() [0]
    # count child elements and attributes
    # look up what elements and attributes we might see, based on the DTD
    for element in allowed_elements(key):               # Counter() [1]
        stats[key][1][1][element] += len(node.xpath(element))
    for attribute in allowed_attributes(key):           # Counter() [2]
        stats[key][1][2][attribute] += len(node.xpath(''.join(['@*[local-name()="', attribute, '"]'])))
    # note if there is text()
    pcdata = "PCDATA" if node.xpath('boolean(./text())') else "no text()"
    stats[key][1][3][pcdata] += 1			# Counter() [3]

    ## done counnting this element node, loop through child nodes
    for desc in list(node):
        # recursive call
        count_elements(desc, stats)

# http://stackoverflow.com/questions/815110/
# http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
class memoized(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    """
    def __init__(self, func):
       self.func = func
       self.cache = {}
    def __call__(self, *args):
       try:
          return self.cache[args]
       except KeyError:
          value = self.func(*args)
          self.cache[args] = value
          return value
       except TypeError:
          # uncachable -- for instance, passing a list as an argument.
          # Better to not cache than to blow up entirely.
          return self.func(*args)
    def __repr__(self):
       """Return the function's docstring."""
       return self.func.__doc__
    def __get__(self, obj, objtype):
       """Support instance methods."""
       return functools.partial(self.__call__, obj)

@memoized
def allowed_elements(key):
    """read XML version of the DTD to figure out allowed elements"""
    return DTD.xpath(''.join(["/dtd/element[@name='", key, "']/content-model-expanded//element-name/@name"]))

@memoized
def allowed_attributes(key):
    """read XML version of the DTD to figure out allowed attributes"""
    return DTD.xpath(''.join(["/dtd/attlist[@name='", key, "']/attribute/@name"]))

# main() idiom for importing into read-eval-print loop for debugging 
if __name__ == "__main__":
    sys.exit(main())

"""
   Copyright (c) 2012, Regents of the University of California
   All rights reserved.

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions are
   met:

   - Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.
   - Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.
   - Neither the name of the University of California nor the names of its
     contributors may be used to endorse or promote products derived from
     this software without specific prior written permission.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
   ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
   LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
   CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
   SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
   INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
   ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
   POSSIBILITY OF SUCH DAMAGE.
"""
