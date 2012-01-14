#!/usr/bin/env python
""" Create an EAD Tag use report 
    Brian Tingle (c) 2012 UC Regents all rights reserved
    BSD license at bottom of file
"""
import sys
import argparse
import fnmatch
import os
import glob
from lxml import etree


# load ead.dtd.xml into "dtd"
dtd = etree.parse('ead.dtd.xml');

def main(argv=None):
    # argument parser 
    parser = argparse.ArgumentParser(description='analyze EAD tag useage')
    parser.add_argument('dir', nargs='+', 
                     help='EAD XML corpus directory')
    parser.add_argument('-outfile', nargs='?', type=argparse.FileType('w'),
                     help='output tag useage report',
                     default=sys.stdout)

    if argv is None:
        argv = parser.parse_args()
     
    # set up dictionary to hold the stats
    stats = {}

    # loop through all files
    # http://stackoverflow.com/questions/2212643/
    # http://stackoverflow.com/questions/2186525
    for dir in argv.dir:
        for root, subFolders, files in os.walk(dir):
            for filename in fnmatch.filter(files, '*.xml'):
                filePath = os.path.join(root, filename)
                stats = analyze_file(filePath, stats)

def analyze_file(file, stats):
    if os.stat(file)[6]==0:
        return stats
    print file, stats, dtd
    xml = etree.parse(file)
    return stats

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
