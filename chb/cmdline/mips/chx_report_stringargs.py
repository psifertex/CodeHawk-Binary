#!/usr/bin/env python3
# ------------------------------------------------------------------------------
# Access to the CodeHawk Binary Analyzer Analysis Results
# Author: Henny Sipma
# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016-2020 Kestrel Technology LLC
# Copyright (c) 2020      Henny Sipma
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ------------------------------------------------------------------------------
"""Script to list the strings referenced in functions.

This script lists strings that are referenced in functions to enable 
function maching between a binary and its (conjectured) source code 
(the CodeHawk C analyzer can produce a similar list for source code 
as a reference). 
"""

import argparse
import json

import chb.app.AppAccess as AP
import chb.util.fileutil as UF

def parse():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('filename',help='name of executable to be analyzed')
    parser.add_argument('--target',help='restrict output to these call targets')
    args = parser.parse_args()
    return args

def get_function_name(app,faddr):
    if app.has_function_name(faddr):
        return app.get_function_name(faddr) + ' (' + faddr + ')'
    else:
        return faddr

if __name__ == '__main__':

    args = parse()

    try:
        (path,filename) = UF.get_path_filename('mips-elf',args.filename)
        UF.check_analysis_results(path,filename)
    except UF.CHBError as e:
        print(str(e.wrap()))
        exit(1)

    app = AP.AppAccess(path,filename,mips=True)
    callinstrs = app.get_app_calls()

    if args.target:
        result = {}  # faddr -> instrs
        for faddr in sorted(callinstrs):
            for i in callinstrs[faddr]:
                if i.has_string_arguments() and str(i.get_call_target()) == args.target:
                    result.setdefault(faddr,[])
                    result[faddr].append(i)

        for faddr in sorted(result):
            print('\n' + get_function_name(app,faddr))
            print('-' * 80)
            for i in result[faddr]:
                print('  ' + i.iaddr + '  ' + i.get_annotation())

    else:
        callees = {} # target -> [ instruction ]

        for faddr in sorted(callinstrs):
            print('\n' + get_function_name(app,faddr))
            print('-' * 80)
            for i in callinstrs[faddr]:
                if i.has_string_arguments():
                    callee = str(i.get_call_target())
                    callees.setdefault(callee,[])
                    callees[callee].append(i)
                    print('  ' + str(i))


        print('Callees')
        print('=' * 80)
        for callee in sorted(callees):
            print('\n' + callee)
            print('-' * 80)
            for i in sorted(callees[callee],key=lambda i:i.get_annotation()):
                print('  (' + str(i.mipsfunction.faddr) + ','
                      + str(i.iaddr) + ')   ' + i.get_annotation())
    
