#!/bin/sh

# Kathryn Nichols
# Stefan Behr

# Task 1
python2.7 texttile.py sotu2013.txt >tiles.txt

# Task 2
sh parse.sh sotu2013.txt >parses.txt

# Task 3
python2.7 simplify.py parses.txt simplifications.txt

# Task 4/5
if [ ! -d system_summaries ]
then
    mkdir system_summaries
fi

python2.7 SumBasic.py simplifications.txt 100 system_summaries >summary_100.txt
python2.7 SumBasic.py simplifications.txt 200 system_summaries >summary_200.txt
python2.7 SumBasic.py simplifications.txt 500 system_summaries >summary_500.txt

# Task 6
/NLP_TOOLS/summarizers/rouge/latest/ROUGE-1.5.5.pl -e /NLP_TOOLS/summarizers/rouge/latest/data -f A -a -x -s -m -2 4 -u settings.xml >evaluation.out

# Task 7
python2.7 twitter_simplify.py parses.txt twitter_simplifications.txt
python2.7 SumBasic_tweet.py twitter_simplifications.txt 140 >tweet.txt
