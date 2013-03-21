#!/usr/bin/env python2.7

import argparse, nltk, simplify
from Queue import Queue

def search(tree, predicate):
	"""
	Return true if tree contains node for which 
	predicate evaluates to true, false otherwise
	"""
	node_indices = tree.treepositions()
	for node_index in node_indices:
		if predicate(tree, node_index):
			return True
	return False

def isX(label):
	def detector(tree):
		return tree.node == label
	return detector

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Clause detection script")
	parser.add_argument("tree_path", action="store", help="Path to file of trees for searching")
	parser.add_argument("clause_type", action="store", help="Type of phrase to look for")
	parser.add_argument("--pt", action="store_true", help="Include this flag to have trees added to output", default=False)
	parser.add_argument("--os", action="store_true", help="Include this flag to omit sentences from output", default=False)
	parser.add_argument("-m", action="store", type=int, default=10000, help="Set tree printing margin, default=10000")
	args = parser.parse_args()

	if args.clause_type == "intrasentential_attribution":
		def isa_detector(tree, index):
			try:
				movement_nodes = simplify.detect_isa(tree, index)
			except:
				return False
			else:
				return len(movement_nodes) > 0
		detector = isa_detector
	else:
		detector = simplify.detector_generator(args.clause_type)

	with open(args.tree_path) as tree_file:
		for tree in tree_file:
			tree = tree.strip()
			if tree:
				tree = nltk.Tree(tree)

				if search(tree, detector):
					# print "*** {0} clause found ***".format(args.clause_type)
					if not args.os:
						print " ".join(tree.leaves())
					if args.pt:
						print tree.pprint(margin=args.m)