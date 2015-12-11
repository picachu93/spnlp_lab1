#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: prelab.py

#####################Importing Libraries#################################
from collections import OrderedDict
from support import *
import fst
from math import log as log10
import operator

#######################Global Declarations###############################
##########filepaths################
#The greek dictionary filepath
el_dict_file = "data/dict/el_caps_noaccent.dict"
#The english dictionary filepath
en_dict_file = "data/dict/en_caps_noaccent.dict"
 #The greek train dataset filepath
gr_train_file = "data/train/train_gr.txt"
#The greeklish train dataset filepath
greng_train_file = "data/train/train_greng.txt"
#The greek test dataset filepath
gr_test_file = "data/test/test_gr.txt"
#The greeklish test dataset filepath
greng_test_file = "data/test/test_greng.txt"
#The spell-checker train data filepath
spell_train_co_file = "data/train/train_co.txt"
spell_train_wr_file = "data/train/train_wr.txt"
#The spell checker test data filepath
spell_test_co_file = "data/test/test_co.txt"
spell_test_wr_file = "data/test/test_wr.txt"

########Character Sets#############
#A set of all the uppercase latin characters
latin_chars = set(get_lang_charset('en'))
#A set of all the greek vowels
gr_vowels = set([u'Α', u'Ε', u'Η', u'Ι',
                 u'Ο', u'Υ', u'Ω'])
#######Symbol Tables###############
#Greek symbol table Σ_gr
sigma_gr = create_symbol_table('gr')
print_symbols(sigma_gr, "out/sigma_gr.txt")
#Latin symbol table Σ_en
sigma_en = create_symbol_table('en')
print_symbols(sigma_en, "out/sigma_en.txt")
#Greeklish symbol table Σ_greng
sigma_greng = create_symbol_table('greng')
print_symbols(sigma_greng, "out/sigma_greng.txt")
#Greeklish+Greek symbol table Σ_other
sigma_other = create_symbol_table('other')
print_symbols(sigma_other, "out/sigma_other.txt")


##############      Main Program    ###########################################
####################     STEP 1   #########################################
#Parse the train data files
words_GR = parse_data(gr_train_file, 'gr')       #Greek train word
words_GRENG = parse_data(greng_train_file)    #Greeklish train words

#Traverse all words of a train dataset and return all possible
#latin - greek 1-1, 1-2 and 2-1 matches
#Also return some statistics for the dataset
def find_matches(words_GR, words_GRENG):
    #matches -> All 1-1 matches
    #greng_bi_matches -> All 2-1 matches
    #gr_bi_matches -> All 1-2 matches
    #gr_freqs -> Greek letter frequency
    #greng_freqs -> Latin letter frequency
    matches, greng_bi_matches, gr_bi_matches, gr_freqs, greng_freqs = \
            {}, {}, {}, {}, {}
    matches_get, greng_bi_matches_get, gr_bi_matches_get, \
            gr_freqs_get, greng_freqs_get = \
                matches.get, greng_bi_matches.get, gr_bi_matches.get, \
                gr_freqs.get, greng_freqs.get

    gr_letter_count, greng_letter_count = 0, 0
    #for every word in the dataset do
    for i in range(len(words_GR)):
        gr_w, greng_w = words_GR[i], words_GRENG[i]
        rev_gr_w, rev_greng_w = words_GR[i][::-1], words_GRENG[i][::-1]
        len_gr, len_greng = len(gr_w), len(greng_w)
        len_to_run = min(len_gr, len_greng)
        #ignore pure english words
        if(gr_w == greng_w): pass
        #for every letter in the current word do
        for l in range(len_to_run):
            gr_l, greng_l = gr_w[l], greng_w[l]
            rev_gr_l, rev_greng_l = rev_gr_w[l], rev_greng_w[l]
            #ignore mistyped latin characters
            if not (gr_l in latin_chars):
                #calculate each greek and latin character frequency
                #might be useful for future improvement
                gr_freqs[gr_l] = gr_freqs_get(gr_l, 1) + 1
                gr_freqs[rev_gr_l] = gr_freqs_get(rev_gr_l, 1) + 1
                gr_letter_count += 2
                greng_freqs[greng_l] = greng_freqs_get(greng_l, 1) + 1
                greng_freqs[rev_greng_l] = greng_freqs_get(rev_greng_l, 1) + 1
                greng_letter_count += 2
                #Align the words to the left and to the right
                #And traverse them forwards and backwards
                #Add a new 1-1 match in matches
                #or increase the count for an existing one
                matches[(greng_l, gr_l)] = matches_get((greng_l, gr_l), 1) + 1
                matches[(rev_greng_l, rev_gr_l)] = \
                        matches_get((rev_greng_l, rev_gr_l), 1) + 1
                #If the greeklish word is bigger than the greek
                #it contains a bigram for sure
                if len_greng > len_gr:
                    greng_bi = greng_w[l] + greng_w[l+1]
                    #a greek vowel is normally not written
                    #as a bigram in greeklish
                    if(not (gr_l in gr_vowels)):
                        #add a new 2-1 match in greng_bi_matches
                        #or increase the count of an existing one
                        #count each rule 2 times since we count
                        #the 1-1 rules 2 times on average
                        greng_bi_matches[(greng_bi, gr_l)] = \
                                greng_bi_matches_get((greng_bi, gr_l), 2) + 2
            #if the greek word is bigger it contains a bigram
            if len_gr > len_greng:
                #add a new 1-2 match in gr_bi_matches
                #or increase the count of an existing one (again by 2)
                gr_bi =  gr_w[l] + gr_w[l+1]
                gr_bi_matches[(greng_l, gr_bi)] = \
                        gr_bi_matches_get((greng_l, gr_bi), 2) + 2
    #divide each letter count by the total amount of letters in each alphabet
    gr_freqs = dict((k, float(v)/gr_letter_count) \
                    for k, v in gr_freqs.iteritems())
    greng_freqs = dict((k, float(v)/greng_letter_count) \
                       for k, v in greng_freqs.iteritems())
    return matches, greng_bi_matches, gr_bi_matches, gr_freqs, greng_freqs



matches, greng_bi_matches, gr_bi_matches, gr_freqs, greng_freqs = \
        find_matches(words_GR, words_GRENG)

#The bigram rules must be thresholded by absolute count
#Since they depend on factors like the individual
#letter frequency and a probabilistic filtering
#would give low cost to 'garbage' rules
#The threshold values were determined by visual inspection
greng_bimatches_filt = dict((k, v) \
                            for k, v in greng_bi_matches.iteritems() if v > 40)
gr_bimatches_filt = dict((k, v) \
                         for k, v in gr_bi_matches.iteritems() if v > 10)
#for visual inspection only
matches_show = dict((k,v) \
                    for k, v in matches.iteritems() if v > 100)
#The 1-1 matches will be filtered by relative count (probabilities)

#sort the frequencies by letters for visual inspection
gr_freqs = OrderedDict(sorted(gr_freqs.items()))
greng_freqs = OrderedDict(sorted(greng_freqs.items()))

all_matches_show = dict(matches_show.items() + \
                        greng_bimatches_filt.items() + \
                        gr_bimatches_filt.items())

print "Most Frequent Rules (By Absolute count):"
print_matches(all_matches_show)
print "\n\n\n"
####################     STEP 2   #########################################
def calc_rules_freq(one_matches, greng_bimatches, gr_bimatches):
    #handle 1-1 and 1-2 matches the same way
    matches = dict(one_matches.items() + gr_bimatches.items())
    count_rules = {}
    chars_processed = set()

    #accumulate the rules that have the same
    #greeklish character as source
    #for example O->Ω and O->O
    for r1, v1 in matches.iteritems():
        if r1[0] in chars_processed: pass
        count_rules[r1[0]] = v1
        for r2, v2 in matches.iteritems():
            #avoid double count
            if r1[0] == r2[0] and r1[1] != r2[1]:
                count_rules[r1[0]] += v2
        #now this greeklish character is counted
        #do not use it again
        chars_processed |= {r1[0]}

    #now handle 2-1 matches
    for r1,v1 in greng_bimatches.iteritems():
        #Add also the count of the individual characters to the sum
        #i.e. : Count(TH) = Count(TH) + Count(T) + Count(H)
        count_rules[r1[0]] = v1 + count_rules[r1[0][0]] + \
                count_rules[r1[0][1]]

    matches = dict(matches.items() + greng_bimatches.items())
    #Frequency(rule) = Count(rule)/Count(rules with same source)
    freq_rules = dict((k, float(v)/count_rules[k[0]]) \
                      for k, v in matches.iteritems())
    return freq_rules, matches



#Function to calculate the cost and filter by a probability value.
#Preserves all bigram rules
def calc_logP_filt(freq_rules, filt_val = 0):
    logP_rules_filt = dict((k, abs(-log10(v))) \
                           for k, v in freq_rules.iteritems() \
                           if v > filt_val or len(k[0]) > 1 or len(k[1]) > 1)
    return logP_rules_filt



#Get the rules and their frequency
freq_rules, matches = calc_rules_freq(matches, \
                                      greng_bimatches_filt, \
                                      gr_bimatches_filt)

#Calculate the cost of  each rule and filter
#Remove rules with frequency < 0.005 (Removes most garbage)
logP_rules_filt = calc_logP_filt(freq_rules, 0.005)
logP_rules = calc_logP_filt(freq_rules) #No filter
#for visual inspection purposes only
logP_rules_filt_show = calc_logP_filt(freq_rules, 0.5)

print("Most Frequent Rules Cost (By Probability):")
print_matches(logP_rules_filt_show)
print "\n\n\n"

####################     STEP 3   #########################################

#Function to create an FST to match
#greeklish letters-bigrams to greek letters-bigrams
def rules_transducer(rules, in_sym = sigma_greng, out_sym = sigma_gr):
    #Create Transducer
    #Input Alphabet : Σ_en
    #Output Alphabet : Σ_gr
    #Semiring : Tropical
    #State(0) : Starting State
    #State(1) : Accepting State (negative cost)
    G = fst.StdTransducer(isyms=in_sym, osyms=out_sym)
    G.add_state()
    G[1].final = -1
    tmp = 2
    G_add_arc = G.add_arc
    for k, v in rules.iteritems():
        #For 1-1 & 1-2 rules create an arc 0->1 with
        #input : greeklish char
        #output : greek char/bigram
        #cost : rule cost
        if len(k[0]) == 1:
            G_add_arc(0, 1, k[0], k[1], v)
        else:
            #For 2-1 rules create an in betwen state
            #pay all the cost to go to the in between state and
            #transform to <epsilon>
            #Then go to accepting state with 0 cost
            #And transform to the greek character
            G_add_arc(0, tmp, k[0][0], fst.EPSILON, v)
            G_add_arc(tmp, 1, k[0][1], k[1], 0)
            tmp += 1
    return G

G = rules_transducer(logP_rules_filt)
print "Created rules transducer G\n"
G.write("out/G_bin.fst")
print "G binaries saved to out/G_bin.fst\n"
print_fst("out/G_bin.fst", "out/G_src.fst", \
          isyms="out/sigma_greng.txt", osyms="out/sigma_gr.txt")
print "\n\n\n"

G_show = rules_transducer(logP_rules_filt_show) #for display purposes only
save_as_pdf(G_show, "out/G_show.pdf")

####################     STEP 4   #########################################
#The cost is calculated as the maximum possible cost rounded up
big_cost = int(0.5 + max(logP_rules.iteritems(), \
                         key=operator.itemgetter(1))[1])
latin_chars = list(latin_chars)
#Define transducer I
#input/output alphabet : Σ_en
#Semiring : Tropical
#State(0) : Starting State
#State(1) : Accepting State
I = fst.StdTransducer(isyms=sigma_en, osyms=sigma_en)
I.add_state()
I[1].final = True

for c in latin_chars:
    #for each latin char c add arc 0->1
    #with input = output = c and cost = big_cost
    I.add_arc(0, 1, c, c, big_cost)

print "Created identity transducer I\n"
save_as_pdf(I, "out/I.pdf")
I.write("out/I_bin.fst")
print "I binaries saved to out/I_bin.fst"
print_fst("out/I_bin.fst", "out/I_src.fst", \
          isyms="out/sigma_en.txt", osyms="out/sigma_en.txt")
print "\n\n\n"

####################     STEP 4   #########################################

#Function that creates an acceptor for a given
#list of words (we pass all the words in the dictionary)
#Adds the arcs manually because using fst.union repeatedly
#is too slow
def dict_acceptor(my_dict, symbols = sigma_gr):
    #Define an Acceptor
    #Input Alphabet : symbols
    #Semiring : Tropical (all weights are 0)
    #State(0) : starting state
    #State(1) : accepting state
    A = fst.StdAcceptor(syms=symbols)
    A.add_state()
    A[1].final = True
    tmp = 2 #current in between state
    A_add_arc = A.add_arc
    for w in my_dict:
        #for every word in my_dict
        #add an <epsilon> arc from 0
        #to a new state tmp (start of the word)
        A_add_arc(0, tmp, fst.EPSILON)
        #create a linear chain for all letters in w
        for l in w:
            A_add_arc(tmp, tmp + 1, l)
            tmp += 1
        #add an <epsilon> arc to the accepting state 1
        A_add_arc(tmp, 1, fst.EPSILON)
        tmp += 1
    return A

####################     STEP 6   #########################################

#funtion to remove epsilon arcs,
#determinize and minimize an FSA
def nfa2min_dfa(A):
    A.remove_epsilon()
    A = A.determinize()
    A.minimize()
    return A

####################     STEP 7   #########################################
#parse the greek and the english dictionary
el_dict = parse_data(el_dict_file, 'gr')
en_dict = parse_data(en_dict_file)

#create the acceptor A1 for the greek dictionary and minimize it
A1 = dict_acceptor(el_dict)
A1 = nfa2min_dfa(A1)
A1.write("out/A1_bin.fst")
print_fst("out/A1_bin.fst", "out/A1_src.fst", \
          isyms="out/sigma_gr.txt")
print "\n\n\n"

#For display purposes only
#Create an acceptor A1_show for 5 words in the greek dictionary
#and display it
el_dict_show = el_dict[55:60]
A1_show = dict_acceptor(el_dict_show)
save_as_pdf(A1_show, "out/A1show_NFA.pdf")

#Minimize A1_show and display it
A1_show = nfa2min_dfa(A1_show)
save_as_pdf(A1_show, "out/A1show_MinDFA.pdf")

#create the acceptor A2 for the english dictionary and minimize it
A2 = dict_acceptor(en_dict, symbols=sigma_en)
A2 = nfa2min_dfa(A2)
A2.write("out/A2_bin.fst")
print_fst("out/A2_bin.fst", "out/A2_src.fst", \
          isyms="out/sigma_en.txt")

#For display purposes only
#Create an acceptor A2_show for 5 words in the english dictionary
#and display it
en_dict_show = en_dict[55:60]
A2_show = dict_acceptor(en_dict_show, sigma_en)
save_as_pdf(A2_show, "out/A2show_NFA.pdf")

#Minimize A2_show and display it
A2_show = nfa2min_dfa(A2_show)
save_as_pdf(A2_show, "out/A2show_MinDFA.pdf")
####################   STEP 8    ################################
#create the union of A1 with A2 
#which is the A12  transducer
A12 = A1.union(A2)
#A12.write("out/A12_bin.fst")
#sort arc for compose compatibility
A12.arc_sort_output() 
#A12 = nfa2min_dfa(A12)
#to display concatenate symbol
#table files for greek and english

#filenames = ['out/sigma_gr.txt','out/sigma_en.txt']
#with open('out/sigma_mix.txt','w') as outfile:
#	for frame in filenames:
#		with open(frame) as infile:
#			outfile.write(infile.read())
#
#A12.write("out/A12_bin.fst")
#print_fst("out/A12_bin.fst","out/A12_src.fst", \
#	  isyms="out/sigma_gr.txt" ) #instead of sigma_mix for compatibility reasons

#compose with G closure
#take greenglish transducer T
G_star = G.closure()
G_star.write("out/G_star_bin.fst")
save_as_pdf(G_star, "out/G_star.pdf")
T = A12.compose(G_star)
#################     STEP 9     #################################
#create an acceptor W for each greeklish  word in 'test_greng.txt'
en_test = parse_data(greng_test_file)     #Greeklish test words
W = dict_acceptor(en_test,symbols = sigma_en)


#################     STEP 10    #################################
#compose W:greeklish test  words with T:greeklish to greek or english 
#WT = W.comose(T)
#and find shortest path
# WT_best = WT.shortest_path()


################      STEP 11    #################################
#

 
