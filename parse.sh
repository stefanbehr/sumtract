#!/usr/bin/env bash

# Calls stanford parser on input file
# $1 is file of sentences to parse

STANFORD_PARSE_DIR="/NLP_TOOLS/parsers/stanford_parser/latest"

java -cp $STANFORD_PARSE_DIR/stanford-parser.jar edu.stanford.nlp.parser.lexparser.LexicalizedParser -outputFormat oneline $STANFORD_PARSE_DIR/englishPCFG.ser.gz $1