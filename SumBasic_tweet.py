# -*- coding: utf-8 -*-
"""
Kathryn Nichols
LING 571
Project 2

Uses SumBasic algorithm to summarize a text.

"""

from __future__ import division
from collections import defaultdict
import nltk
import re

def get_sentences(filename):
    """
    Removes stopwords from, stems and tokenizes sentences.
    Computes probability distribution over words.

    @param filename -- name of file containing sentences

    @return distribution -- probability distribution of words
    @return tweets -- list of clean sentences
    @return processed_sentences -- list of processed sentences

    """

    stopwords = nltk.corpus.stopwords.words('english') + ['n']
    stemmer = nltk.stem.PorterStemmer()
    tokenize = nltk.word_tokenize

    tweets, processed_sentences = [], []
    distribution = defaultdict(int)
    total = 0

    for line in open(filename):
        line = line.strip()
        if not line: continue

        # remove non-alphanumeric symbols, stem, tokenize, stopwordize
        sentence = re.sub(r'\W', ' ', line).lower()
        sentence = [stemmer.stem(word) for word in tokenize(sentence) \
                    if not word in stopwords]

        # store sentences if not empty
        if sentence:
            processed_sentences.append(sentence)
            tweets.append(twitterize(line))

        # update frequency
        for word in sentence:
            distribution[word] += 1
            total += 1

    # convert frequency distribution to probability distribution
    for word in distribution: distribution[word] = distribution[word]/total

    return distribution, tweets, processed_sentences

def summarize(distribution, tweets, processed_sentences, N):
    """
    Recursively runs SumBasic algorithm on sentences.

    @param distribution -- probability distribution over words
    @param tweets -- list of clean sentences
    @param processed_sentences -- list of processed sentences
    @param N -- maximum length of summary in words

    @return -- summary pieces as strings

    """

    if N == 0 or N == 1: return ''

    # sort words by probability
    words = sorted(distribution, key=distribution.get, reverse=True)

    for word in words:

        # get candidate sentences containing word
        candidates = [sentence for sentence in processed_sentences if word in sentence]
        
        # sort candidates by average probability
        candidates = sentence_averages(distribution, candidates)

        for candidate in candidates:
            tweet = tweets[processed_sentences.index(candidate)]
            processed_sentences.remove(candidate)
            tweets.remove(tweet)

            # if sentence fits, add sentence to summary
            if len(tweet) <= N:    
        
                # update distribution
                for word in candidate: distribution[word] = distribution[word]**2

                return tweet + ' ' + summarize(distribution, \
                        tweets, processed_sentences, (N - len(tweet)))
       
    return ''


def sentence_averages(distribution, sentences):
    """
    Finds average word probability per sentence and returns highest.

    @param distribution -- probability distribution over words
    @param sentences -- list of sentences

    @return averages -- sentences sorted by average probability

    """
    
    scores = defaultdict(float)
    index = 0

    for sentence in sentences:
        scores[index] = sum([distribution[word] for word in sentence])/len(sentence)
        index += 1

    averages = [sentences[index] for index in sorted(scores, key=scores.get, reverse=True)]

    return averages

def twitterize(sentence):
    """
    Cleans and twitterizes given sentence for use in a summary.

    @param sentence -- sentence to clean

    @return sentence -- cleaned and twitterized sentence

    """

    sentence = convert_numbers(sentence)

    punc = re.compile(r' +(\.|%|\?)')
    clitics = re.compile(r' +(\'s|\'re|n\'t|\'ve|\'m|\'ll|\'d)')

    # clean up a bit
    sentence = sentence.strip()
    sentence = re.sub(punc, r'\1', sentence)      # attach punc to previous word
    sentence = re.sub(r'[:;!,]', r' ', sentence)  # delete some punctuation
    sentence = re.sub(r'\\/', '/', sentence)      # slash attaches to left and right words
    sentence = re.sub(r'\$ +', '$', sentence)     # attach $ to next word
    sentence = re.sub(r'`+|\'\'', r'', sentence)  # remove quotes
    sentence = re.sub(clitics, r'\1', sentence)   # attach clitics to previous word
    sentence = re.sub(r' - ', r'-', sentence)     # remove space around hyphens

    # twitterize
    sentence = re.sub(r'(eight|ate|ait)(\b|ed|d)', r'8\2', sentence)
    sentence = re.sub(r'for', r'4', sentence)
    sentence = re.sub(r'minute', r'min', sentence)
    sentence = re.sub(r'hour', r'hr', sentence)
    sentence = re.sub(r'says', r'sez', sentence)
    sentence = re.sub(r'[Yy]ou\'re|\b[Yy]our\b', r'Ur', sentence)
    sentence = re.sub(r'\b[Yy]ou\b', r'U', sentence)
    sentence = re.sub(r'[Ww]ere|[Ww]e\'re', r'wr', sentence)
    sentence = re.sub(r'\b[Tt]o\b|[Tt]oo', r'2', sentence)
    sentence = re.sub(r'[Bb]e', r'B', sentence)
    sentence = re.sub(r'\b[Aa]re\b|\b[Oo]ur\b', r'R', sentence)
    sentence = re.sub(r'[Gg]reat', r'gr8', sentence)
    sentence = re.sub(r'[Tt]hey\'re|[Tt]heir|[Tt]here', r'thr', sentence)
    sentence = re.sub(r' is', r"'s", sentence)
    sentence = re.sub(r'cannot', r"can't", sentence)
    sentence = re.sub(r'[Ww]hy', r'Y', sentence)
    sentence = re.sub(r'[Nn]ever', r'nvr', sentence)
    sentence = re.sub(r'[Ll]ike', r'lk', sentence)
    sentence = re.sub(r'[Tt]hanks', r'thx', sentence)
    sentence = re.sub(r'[Pp]lease', r'pls', sentence)
    sentence = re.sub(r'\bin\b|\band\b', r'n', sentence)
    sentence = re.sub(r'[Dd]ollar|[Dd]ollars', r'$', sentence)
    sentence = re.sub(r'[Pp]ercent|[Pp]ercentage', r'%', sentence)
    sentence = re.sub(r'er ', r'r ', sentence)
    sentence = re.sub(r'tion', r'tn', sentence)
    sentence = re.sub(r'[Yy]ear', r'yr', sentence)

    sentence = re.sub(r' +', r' ', sentence)     # delete extra spaces

    return sentence

def convert_numbers(sentence):
    """
    Shortens word numbers or converts to digits. 

    """
    
    # replace some patterns
    sentence = re.sub(r'[Zz]ero', r'0', sentence)
    sentence = re.sub(r'[Hh]undreds', r'100s', sentence)
    sentence = re.sub(r'[Tt]ousands', r'1000s', sentence)
    sentence = re.sub(r'[Mm]illion', r'mil', sentence)
    sentence = re.sub(r'[Bb]illion', r'bil', sentence)
    sentence = re.sub(r'-', r' - ', sentence)
    sentence = sentence.split()

    # 1-19
    lower = {'one':'1', 'two':'2', 'three':'3', 'four':'4', 'five':'5', 'six':'6', \
                 'seven':'7', 'eight':'8', 'nine':'9', 'ten':'10', 'eleven':'11',\
                 'twelve':'12', 'thirteen':'13', 'fourteen':'14', 'fifteen':'15', \
                 'sixteen':'16', 'seventeen':'17', 'eighteen':'18', 'nineteen':'19'}
    
    # 20-90
    upper = {'twenty':'2', 'thirty':'3', 'fourty':'4', 'fifty':'5',\
                   'sixty':'6', 'seventy':'7', 'eighty':'8', 'ninety':'9'}

    number_strings, indices = scrape_number_clauses(sentence, upper, lower)
    places = format_numbers(number_strings, upper, lower)
    numbers = translate_numbers(places)

    # replace number words in original text
    for i in range(len(indices)): sentence[indices[i]] = numbers[i]

    # return to string format with spaces
    output = ''
    for word in sentence: output += ' ' + word

    return output

def scrape_number_clauses(sentence, upper, lower):
    """
    Retrieves number clauses from given sentence.

    @param sentence -- sentence as list
    @param upper -- dictionary of numbers 20-90
    @param lower -- dictionary of numbers 1-19

    @return number_strings -- list of lists of number clauses
    @return indices -- indices of beginning of number clauses in sentence

    """

    number_strings, indices = [], []
    index = 0

    while index < len(sentence):
        substring = []
        first = True
        
        # capture number sequence
        while index < len(sentence) and \
                (sentence[index].lower() in lower\
                or sentence[index].lower() in upper\
                or sentence[index].lower() in ['hundred', 'thousand'] \
                or (sentence[index] in ['-', 'and'] and not first)):

            # first number word in clause, store index
            if first:
                indices.append(index)
                first = False

            if sentence[index] not in ['-', 'and']:
                substring.append(sentence[index].lower())

            # remove number words from text
            sentence[index] = ''
            index += 1

        if substring: number_strings.append(substring)

        index += 1

    return number_strings, indices

def format_numbers(number_strings, upper, lower):
    """
    Finds hundred-thousands-, ten-thousands-, thousands-, hundreds-,
    tens- and ones-place digits in number clause.

    @param number_strings -- list of lists of numbers in word clauses
    @param upper -- dictionary of numbers 20-90
    @param lower -- dictionary of numbers 1-19

    @return places -- list of dictionaries of number places

    """

    places = []

    for string in number_strings:

        nums = {'hundredthousands':'','tenthousands':'','thousands':'', \
                    'hundreds':'', 'tens':'', 'ones':''}
        index = 0

        # add digits to places
        while index < len(string):

            # next words are hundred and thousand
            if index < (len(string) - 2) and string[index + 1] == 'hundred'\
                  and string[index + 2] == 'thousand':
                  nums['hundredthousands'] = lower[string[index]]
                  index += 2

            # next word is hundred
            elif index < (len(string) - 1) and string[index + 1] == 'hundred':
                nums['hundreds'] = lower[string[index]]
                index += 1

            # next word is thousand
            elif index < (len(string) - 1) and string[index + 1] == 'thousand':

                # shift numbers already processed
                if nums['tens']:
                    nums['tenthousands'] = nums['tens']
                    nums['tens'] = ''
                if nums['hundreds']:
                    nums['hundredthousands'] = nums['hundreds']
                    nums['hundreds'] = ''

                # current word is tens- or ones-place
                if string[index] in upper: nums['tenthousands'] = upper[string[index]]
                elif string[index] in lower: nums['thousands'] = lower[string[index]]
                
                # current word is 'hundred'
                elif string[index] == 'hundred': nums['hundredthousands'] = '1'

                index += 1
            
            # word is tens-place
            elif string[index] in upper: nums['tens'] = upper[string[index]]

            # word is ones-place
            elif string[index] in lower: nums['ones'] = lower[string[index]]

            # just hundred and/or thousand (preceded by 'a', 'few', e.g.)
            elif string[index] == 'hundred': nums['hundreds'] = '1'
            elif string[index] == 'thousand': nums['thousands'] = '1'
            else: sys.stderr.out('unparsable string ' + str(string))

            index += 1

        places.append(nums)

    return places

def translate_numbers(places):
    """
    Converts number places to strings of digits.

    @param places -- list of dictionaries of number places

    @return numbers -- list of numbers as digit strings

    """
    
    numbers = []

    for nums in places:
        number = nums['hundredthousands']

        if nums['hundredthousands'] and not nums['tenthousands']: number += '0'
        else: number += nums['tenthousands']

        if (nums['hundredthousands'] or nums['tenthousands']) \
                and not nums['thousands']: number += '0'
        else: number += nums['thousands']

        if (nums['hundredthousands'] or nums['tenthousands'] or\
                nums['thousands']) and not nums['hundreds']: number += '0'
        else: number += nums['hundreds']

        if (nums['hundredthousands'] or nums['tenthousands'] or \
                nums['thousands'] or nums['hundreds']) and not nums['tens']: number += '0'
        else: number += nums['tens']

        if (nums['hundredthousands'] or nums['tenthousands'] or \
                nums['thousands'] or nums['hundreds'] or nums['tens']) and\
                not nums['ones']: number += '0'
        else: number += nums['ones']

        numbers.append(number)
    
    return numbers

def main():
    """
    Reads in sentences, twitterizes sentences, uses SumBasic to find 
    sentences for summary, prints summary to console.

    """
    
    import argparse, sys
    
    args = argparse.ArgumentParser()
    args.add_argument('sentences', help='file of line-separated sentences to summarize')
    args.add_argument('N', help='number of characters in summary', type=int)
    args.parse_args()
    
    N = int(sys.argv[2])
    
    if N < 1:
        sys.stderr.write('N must be greater than 0. No output produced.')
        sys.exit()
    
    distribution, tweets, processed_sentences = get_sentences(sys.argv[1])
    print summarize(distribution, tweets, processed_sentences, N)

if __name__=='__main__':
    main()

