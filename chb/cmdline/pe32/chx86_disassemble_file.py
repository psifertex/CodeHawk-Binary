# ------------------------------------------------------------------------------
# Access to the CodeHawk Binary Analyzer Analysis Results
# Author: Henny Sipma
# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016-2020 Kestrel Technology LLC
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
"""Disassembles the file and displays some disassembly statistics.

An objdump-type assembly listing is saved in 
    <x>.ch/analysis/<x>_asm.log
A listing of instructions not included in any function is saved in
    <x>.ch/analysis/<x>_orphan.log
No analysis is performed.
"""

import argparse
import os
import shutil
import subprocess

import chb.util.fileutil as UF
import chb.cmdline.AnalysisManager as AM

def parse():
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('filename',help='file to disassemble')
    parser.add_argument('--xml',help='save disassembly status info in xml',
                            action='store_true')
    parser.add_argument('--reset',action='store_true',
                            help='remove existing analysis results')
    parser.add_argument('--extracthex',action='store_true',
                            help='take input from executable in hex form')
    args = parser.parse_args()
    return args

def extract(path,filename,deps,extracthex):
    try:
        am = AM.AnalysisManager(path,filename,deps)
        chcmd = '-extracthex' if extracthex else '-extract'
        result = am.extract_executable(chcmd=chcmd)
        if not (result == 0):
            print('*' * 80)
            print('Error in extracting executable; please check format')
            print('*' * 80)
            exit(1)
        am.save_extract()
    except subprocess.CalledProcessError as args:
        print(args.output)
        print(args)
        exit(1)
    

if __name__ == '__main__':

    args = parse()

    try:
        (path,filename,deps) = UF.get_path_filename_deps('x86-pe',args.filename)
        if not UF.check_executable(path,filename):
            extract(path,filename,deps,args.extracthex)            
    except UF.CHBError as e:
        print(str(e.wrap()))
        exit(1)
         
    UF.check_analyzer()
    am = AM.AnalysisManager(path,filename,deps=deps)

    if args.reset:
        chdir = UF.get_ch_dir(path,filename)
        if os.path.isdir(chdir):
            print('Removing ' + chdir)
            shutil.rmtree(chdir)
        if not UF.unpack_tar_file(path,filename):
            print('*' * 80)
            print('Error in unpacking tar.gz file with executable content')
            print('*' * 80)
            exit(1)

    try:
        am.disassemble(save_xml=args.xml)
    except subprocess.CalledProcessError as e:
        print(e.output)
        print(e.args)

