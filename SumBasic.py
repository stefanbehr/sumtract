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
    @return raw_sentences -- list of raw sentences
    @return processed_sentences -- list of processed sentences

    """

    stopwords = nltk.corpus.stopwords.words('english') + ['n']
    stemmer = nltk.stem.PorterStemmer()
    tokenize = nltk.word_tokenize

    raw_sentences, processed_sentences = [], []
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
            raw_sentences.append(clean(line))

        # update frequency
        for word in sentence:
            distribution[word] += 1
            total += 1

    # convert frequency distribution to probability distribution
    for word in distribution: distribution[word] = distribution[word]/total

    return distribution, raw_sentences, processed_sentences

def summarize(distribution, raw_sentences, processed_sentences, N):
    """
    Runs SumBasic algorithm on sentences and returns summary as a list 
    of raw sentences.

    @param distribution -- probability distribution over words
    @param raw_sentences -- list of raw sentences
    @param processed_sentences -- list of processed sentences
    @param N -- maximum length of summary in words

    @return summary -- summary as a list of cleaned sentences

    """

    summary = []
    length = 0

    while length < N and len(processed_sentences) > 0:

        # find highest probability word and sentences containing that word
        word = find_best_word(distribution)
        candidates = [sentence for sentence in processed_sentences if word in sentence]

        # get sentence with highest average word probability and its original form
        sentence = weight_sentences(distribution, candidates)
        original = raw_sentences[processed_sentences.index(sentence)]

        # summary length should not exceed N
        if len(original.split()) + length >= N: break

        # remove sentences from consideration and add to summary
        processed_sentences.remove(sentence)
        raw_sentences.remove(original)
        length += len(original.split())
        summary.append(original)

        # downweight words
        for word in sentence: distribution[word] = distribution[word]**2

    return summary

def find_best_word(distribution):
    """
    Returns the highest probability word given the distribution.

    @param distribution -- probability distribution over words
    
    @return best_word -- word with highest probability

    """

    best_word, max_prob = '', 0

    for word in distribution:
        if distribution[word] > max_prob:
            max_prob = distribution[word]
            best_word = word

    return best_word

def weight_sentences(distribution, sentences):
    """
    Finds average word probability per sentence and returns highest.

    @param distribution -- probability distribution over words
    @param sentences -- list of sentences

    @return best_sentence -- sentence with highest average word probability

    """
    
    best_sentence, best_average = '', 0

    for sentence in sentences:
        average = sum([distribution[word] for word in sentence])/len(sentence)
        if average > best_average:
            best_average = average
            best_sentence = sentence

    return best_sentence

def clean(sentence):
    """
    Cleans given sentence for use in a summary.

    @param sentence -- sentence to clean

    @return sentence -- cleaned sentence

    """

    punc = re.compile(r' +(;|:|\?|!|\.|,|%|\'\')')
    clitics = re.compile(r' +(\'s|\'re|n\'t|\'ve|\'m|\'ll|\'d)')

    sentence = sentence.strip()
    sentence = re.sub(punc, r'\1', sentence)     # attach punc to previous word
    sentence = re.sub(r'\\/', '/', sentence)     # slash attaches to left and right words
    sentence = re.sub(r'\$ +', '$', sentence)    # attach $ to next word
    sentence = re.sub(r'`+|\'\'', '', sentence)  # remove quotes
    sentence = re.sub(clitics, r'\1', sentence)  # attach clitics to previous word
    sentence = re.sub(r' +', r' ', sentence)     # delete extra spaces

    return sentence

def main():
    """
    Reads in sentences, uses SumBasic to find sentences for summary, prints
    summary to console.

    """
    
    import argparse, sys
    
    args = argparse.ArgumentParser()
    args.add_argument('sentences', help='file of line-separated sentences to summarize')
    args.add_argument('N', help='number of words in summary', type=int)
    args.parse_args()
    
    N = int(sys.argv[2])
    
    if N < 1:
        sys.stderr.write('N must be greater than 0. No output produced.')
        sys.exit()
    
    distribution, raw_sentences, processed_sentences = get_sentences(sys.argv[1])
    summary = summarize(distribution, raw_sentences, processed_sentences, N)
    for s in summary: sys.stdout.write(s + ' ')
    sys.stdout.write('\n')

if __name__=='__main__':
    main()
