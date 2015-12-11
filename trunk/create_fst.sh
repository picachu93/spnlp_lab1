#!/bin/bash
fstcompile -isymbols = in_labels.isyms -osymbols = out_labels.osyms A.txt A.fst
fstcompile -isymbols = in_labels.isyms -osymbols = out_labels.osyms B.txt B.fst
 
