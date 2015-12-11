#!/bin/bash
fsttopsort A12_bin.fst A12_sorted_bin.fst
fsttopsort G_star_bin.fst G_star_sorted_bin.fst
fstcompose A12_sorted_bin.fst G_star_sorted_bin.fst > T_bin.fst
