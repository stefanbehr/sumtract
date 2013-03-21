#!/bin/sh

# Kathryn Nichols
# Stefan Behr
# task 7, extra credit pipeline

# get parses
sh parse.sh sotu2013.txt >parses.txt

# get all simplifications of sentences from parses, including twitter simplification
python2.7 twitter_simplify.py parses.txt twitter_simplifications.txt

# run simplifications through modified SumBasic to get tweet
python2.7 SumBasic_tweet.py twitter_simplifications.txt 140 >tweet.txt
