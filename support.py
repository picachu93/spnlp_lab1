#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: support.py

#####################Importing Libraries#################################
from codecs import open as codecs_open
from itertools import chain as itertools_chain
import fst
import subprocess



#Return all uppercase chars for a given language
def get_lang_charset(lang = "gr"):
    if lang == 'gr':
        return [u'Α', u'Β', u'Γ', u'Δ', u'Ε', u'Ζ', \
                u'Η', u'Θ', u'Ι', u'Κ', u'Λ', u'Μ', \
                u'Ν', u'Ξ', u'Ο', u'Π', u'Ρ', u'Σ', \
                u'Τ', u'Υ', u'Φ', u'Χ', u'Ψ', u'Ω']
    elif lang == 'en':
        return map(chr, range(65, 91))
    elif lang == 'greng':
        tmp = map(chr, range(65, 91))
        tmp.append('0')
        tmp.append('3')
        tmp.append('8')
        tmp.append('9')
        return tmp
    else:
        tmp = map(chr, range(65, 91))
        tmp.append('0')
        tmp.append('3')
        tmp.append('8')
        tmp.append('9')
	tmp1 =  [u'Α', u'Β', u'Γ', u'Δ', u'Ε', u'Ζ', \
                u'Η', u'Θ', u'Ι', u'Κ', u'Λ', u'Μ', \
                u'Ν', u'Ξ', u'Ο', u'Π', u'Ρ', u'Σ', \
                u'Τ', u'Υ', u'Φ', u'Χ', u'Ψ', u'Ω']

        return tmp + tmp1


#Parse a space separated data file
#Return a list of all the words in the file
#Trim the first unicode character if the file is in greek
def parse_data(input_file, lang = 'en'):
    temp_list = []
    append = temp_list.append
    lines = codecs_open(input_file, 'r', 'utf8').readlines()
    for word in itertools_chain.from_iterable(
        line.split() for line in lines):
        append(word)
    if lang == 'gr':
        temp_list[0] = temp_list[0][1:]
    return temp_list

#print the devised rules
def print_matches(my_dict):
    for k, v in my_dict.iteritems():
        print k[0] + "->" + k[1] + "  " + str(v)

def save_as_pdf(fst, filename):
    dot_file = filename + ".dot"
    f = open(dot_file, 'w')
    print >>f, fst.draw()
    f.close()
    dotcmd = "dot -Tpdf -o" + filename + " " + dot_file + " && rm " + dot_file
    p = subprocess.Popen(dotcmd , shell=True, \
                         stdout=subprocess.PIPE, \
                         stderr=subprocess.PIPE)
    p.wait()


def print_symbols(symbols, filename):
    f = open(filename, 'w+')
    for s, sid in symbols.items():
      print >>f, u'{} {}\n'.format(s, sid).encode('utf-8')
    f.close()


#Create a greek / english or empty symbol table
#to be used be an FSA or an FST
def create_symbol_table(charset = 'gr'):
    sigma = fst.SymbolTable(epsilon=fst.EPSILON)
    symbols = get_lang_charset(charset)
    for c in symbols:
        sigma[c] = ord(c)
    return sigma


def print_fst(binfst, filename, \
              isyms="out/sigma_greng.txt", \
              osyms=""):
    printcmd = "fstprint --isymbols=" + isyms
    if not osyms.strip() : printcmd += " --osymbols=" + osyms
    printcmd += " " + binfst + "  " + filename
    p = subprocess.Popen(printcmd, shell=True, \
                         stdout=subprocess.PIPE, \
                         stderr=subprocess.PIPE)
    p.wait()

