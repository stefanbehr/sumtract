#!/usr/bin/env python2.7

# Stefan Behr and Kathryn Nichols
# LING 571
# Project 2
# Code for Task 3

import argparse, nltk
from Queue import Queue

def detect(tree, index, clause_type):
	if clause_type == "":
		return tree[index] not in tree.leaves() and tree[index].node == "NP"

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="A parse tree simplification script")
	parser.add_argument("parse_path", action="store", help="Path to file of parses for simplification")
	parser.add_argument("output_path", action="store", help="Path for storing simplified sentences")
	args = parser.parse_args()

	q = Queue()	# holds candidates for simplification
	s = set()	# holds simplified parses for output

	clause_types = [""]

	# read in parses, convert, store
	with open(args.parse_path) as parse_file:
		for line in parse_file:
			line = line.strip()
			if line:
				# convert to tree, enqueue
				q.put(nltk.Tree(line))

	# check candidate parses for simplification until exhausted
	while not q.empty():
		tree = q.get()
		s.add(tree.freeze())	# freeze to hash
		# iterate over node indices except root
		for abs_node_index in tree.treepositions()[1:]:
			# iterate through clause detection functions
			for clause_type in clause_types:
				if detect(tree, abs_node_index, clause_type):
					parent_index = abs_node_index[:-1]		# absolute node index is tuple of len > 0, index of parent is tuple of all but last element
					child_index = abs_node_index[-1]
					simplified = tree.copy(deep=True)
					simplified[parent_index].pop(child_index)	# pop index must be int, so we pop correct child of parent instead of child directly
					q.put(simplified)

	with open(args.output_path, "w") as output_file:
		for tree in s:
			print >> output_file, " ".join(tree.leaves())