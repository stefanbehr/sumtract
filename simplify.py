# -*- coding: utf-8 -*-

# Stefan Behr and Kathryn Nichols
# LING 571
# Project 2
# Code for Task 3

import argparse, nltk
from Queue import Queue

def detect_isa(tree, index):
	"""
	Detect whether or not the node at the given 
	index in the given tree contains an example 
	of intra-sentential attribution. If so, return 
	the index of the subtree containing the 
	attributed clause. Else, raise an exception?
	"""
	S_detector = label_detector("S")
	node = tree[index]
	if not S_detector(node):
		raise DetectionError("node at index {0} is not an S node".format(str(index)))
	else:
		detected_attr_verbs = find_nodes(node, is_attributive_verb)
		detected_S_subtrees = find_nodes(node, S_detector)

	valid_verbs = []
	# for each attributive verb index found, check if any found
	# S node's index is a prefix to it, which means the S
	# intervenes between the verb and root
	for verb_index in detected_attr_verbs:
		if not reduce(lambda p, q: p or q, map(lambda t: has_prefix(verb_index, t), detected_S_subtrees), False):
			valid_verbs.append(verb_index)
	if len(valid_verbs) == 0:
		raise DetectionError("no valid attributive verb node found below index {0}".format(index))
	else:
		isa_indices = []
		# make verb indices absolute relative to root of tree
		valid_verbs = [index + verb_index for verb_index in valid_verbs]
		for verb_index in valid_verbs:
			# for each candidate, check if it has a 
			# sister S node to the right. if so, that's 
			# the result index.
			# otherwise, check for an SBAR to the right, 
			# if there is one, return index of its second child 
			# if it's an S
			verb_parent_index = verb_index[:-1]		# index of parent of verb
			rel_verb_index = verb_index[-1]			# index of verb relative to its parent
			verb_parent = tree[verb_parent_index]
			# iterate over siblings to right of verb; once you find S, or 
			# SBAR with nested [(IN that)] (S ...), record index of the S
			for rel_sibling_index in range(rel_verb_index + 1, len(verb_parent)):
				sibling_node = verb_parent[rel_sibling_index]
				try:
					sibling_label = sibling_node.node
				except:
					continue
				if sibling_label == "S":
					isa_indices.append(verb_parent_index + (rel_sibling_index,))
					break
				elif sibling_label == "SBAR":
					try:
						sibling_first_child = sibling_node[0]
						sibling_first_child_label = sibling_first_child.node
					except (AttributeError, IndexError, TypeError) as e:
						continue
					if sibling_first_child_label == "S":
						isa_indices.append(verb_parent_index + (rel_sibling_index, 0))
						break
					elif sibling_first_child_label == "IN":
						try:
							sibling_first_child_child = sibling_first_child[0]
						except (IndexError, TypeError) as e:
							continue
						if sibling_first_child_child in ["that", "That"]:
							try:
								sibling_second_child = sibling_node[1]
								sibling_second_child_label = sibling_second_child.node
							except (AttributeError, IndexError, TypeError) as e:
								continue
							if sibling_second_child_label == "S":
								isa_indices.append(verb_parent_index + (rel_sibling_index, 1))
								break
						else:
							continue
		return isa_indices

def has_prefix(t1, t2):
	"""
	Returns true if tuple t1 has tuple t2 as a prefix 
	(i.e., if the elements of t2 align with t1[:len(t2)])
	"""
	return (len(t1) >= len(t2) and 
		(len(t2) == 0 or (t1[0] == t2[0] and 
			has_prefix(t1[1:], t2[1:]))))


def find_nodes(tree, predicate):
	"""
	Returns a list of node indices in given tree 
	for all nodes for which the given predicate evaluates 
	to true
	"""
	indices = []
	for index in tree.treepositions()[1:]:
		if predicate(tree[index]):
			indices.append(index)
	return indices

def label_detector(label):
	"""
	Given a label, generates a function which, given a node, 
	determines whether or not the node has the label
	"""
	def detector(node):
		try:
			node_label = node.node
		except AttributeError:
			return False
		else:
			return node_label == label
	return detector

def is_attributive_verb(node):
	"""
	Returns true if a given node is a verb 
	and has a terminal child that is an 
	attributive verb
	"""
	verb_labels = ["VB", "VBD", "VBZ", "VBN"]
	verb_list = WordList("attribution.txt")
	try:
		node_label = node.node
	except AttributeError:
		return False
	else:
		try:
			first_child = node[0]
		except:
			return False
		return (node_label in verb_labels and 
			type(first_child) is not nltk.Tree and 
			first_child in verb_list)


def detector_generator(clause_type):
	"""
	Given a clause_type, returns a closure including 
	the clause_type variable, which triggers different 
	clause detection behaviors in the function part of 
	the closure
	"""

	def detector(tree, index):
		"""
		"Now I am become Death, the destroyer of worlds."
		"""
		detected = False
		node = tree[index]
		if clause_type == "noun_appositive":
			try:
				# node is NP, two adjacent left siblings are 
				# NP and (, ,), right sibling is (, ,)
				parent_index = index[:-1]
				parent_node = tree[parent_index]

				rel_node_index = index[-1]

				left_siblings = parent_node[:rel_node_index]
				right_sibling = parent_node[rel_node_index + 1]

				node_label = node.node

				detected = (left_siblings[-2].node == "NP" and 
					left_siblings[-1].node == "," and 
					node_label == "NP" and 
					right_sibling.node == ",")
			except:
				try:
					# node has PRN label, 1st child is NP
					node_label = node.node
					detected = (node_label == "PRN" and
						node[1].node == "NP")
				except:
					pass
		elif clause_type == "lead_adverbial":
			try:
				# node is RB or ADVP and is first 
				# child of an S
				node_label = node.node
				
				parent_index = index[:-1]
				parent_node = tree[parent_index]
				parent_label = parent_node.node

				rel_node_index = index[-1]

				detected = ((node_label == "RB" or node_label == "ADVP" or node_label == "CC") and 
					parent_label == "S" and 
					rel_node_index == 0)
			except:
				pass
		elif clause_type == "gerundive":
			try:
				# node is a vp
				# it is leftmost child
				# its parent is S
				# it has a leftmost descendant VBG
				node_label = node.node
				rel_node_index = index[-1]

				parent_index = index[:-1]
				parent_node = tree[parent_index]
				parent_label = parent_node.node

				detected = (node_label == "VP" and 
					rel_node_index == 0 and 
					parent_label == "S" and 
					has_left_descendant(node, "VBG"))
			except:
				pass
		elif clause_type == "nonrestrictive_relative":
			# delete SBAR nodes whose first child is a WHNP 
			# whose first child is a WP or WP$
			try:
				node_label = node.node
			except AttributeError:
				pass
			else:
				if node_label == "SBAR":
					try:
						first_child = node[0]
						first_child_label = first_child.node
					except (AttributeError, IndexError, TypeError) as e:
						pass
					else:
						if first_child_label == "WHNP":
							try:
								first_child_child = first_child[0]
								first_child_child_label = first_child_child.node
							except (AttributeError, IndexError, TypeError) as e:
								pass
							else:
								detected = (first_child_child_label == "WP" or 
									first_child_child_label == "WP$")
		return detected
	return detector

def has_left_descendant(tree, label):
	"""
	Given a tree and node label, 
	returns true if the leftmost path in 
	the tree contains a node with the 
	given label.
	"""
	try:
		root_label = tree.node
	except AttributeError:
		# reached leaf
		return False
	try:
		left_child = tree[0]
	except IndexError:
		return False
	return root_label == label or has_left_descendant(left_child, label)

class DetectionError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class SetQueue(Queue):
	"""
	Queue which prevents already seen items from being 
	enqueued again.

	Credit for this data structure implementation goes to 
	stackoverflow.com users Lukáš Lalinský and Paul McGuire:
	http://stackoverflow.com/a/1581937
	"""
	def _init(self, maxsize):
		Queue._init(self, maxsize)
		self.all_items = set()
	def _put(self, item):
		if item not in self.all_items:
			Queue._put(self, item)
			self.all_items.add(item)

class WordList:
	"""
	WordList class for reading in and iterating 
	over word lists
	"""
	def __init__(self, fpath):
		with open(fpath) as f:
			self.words = f.read().strip().split("\n")

	def __iter__(self):
		return iter(self.words)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="A parse tree simplification script")
	parser.add_argument("parse_path", action="store", help="Path to file of parses for simplification")
	parser.add_argument("output_path", action="store", help="Path for storing simplified sentences")
	args = parser.parse_args()

	candidates = SetQueue()	# holds candidates for simplification
	clause_types = ["noun_appositive", "lead_adverbial", "gerundive", "nonrestrictive_relative", "intrasentential_attribution"]

	# read in parses, convert, store
	with open(args.parse_path) as parse_file:
		for line in parse_file:
			line = line.strip()
			if line:
				# convert to frozen tree, add to set
				candidates.put(nltk.ImmutableTree(line))

	# check candidate parses for simplification until exhausted
	while not candidates.empty():
		tree = candidates.get()
		# iterate over node indices except root
		for abs_node_index in tree.treepositions()[1:]:
			# iterate through clause detection functions
			for clause_type in clause_types:
				if clause_type == "intrasentential_attribution":
					try:
						# check if current subtree is the start of an intrasentential
						# attribution, and grab all attributions within it
						attributed_node_indices = detect_isa(tree, abs_node_index)
					except:
						continue
					else:
						for attributed_node_index in attributed_node_indices:
							# raise each attributed node to the node 
							# that starts the ida (one at a time), and 
							# enqueue each new version of the tree
							simplified = nltk.Tree.convert(tree)
							simplified[abs_node_index] = simplified[attributed_node_index]
							candidates.put(simplified.freeze())
				else:
					detector = detector_generator(clause_type)
					if detector(tree, abs_node_index):
						parent_index = abs_node_index[:-1]		# absolute node index is tuple of len > 0, index of parent is tuple of all but last element
						child_index = abs_node_index[-1]
						simplified = nltk.Tree.convert(tree)	# get unfrozen copy of tree for mutation
						simplified[parent_index].pop(child_index)	# pop index must be int, so we pop correct child of parent instead of child directly
						candidates.put(simplified.freeze())

	# set of items enqueued onto SetQueue, consists 
	# only of original parses and simplifications
	simplifications = candidates.all_items

	with open(args.output_path, "w") as output_file:
		for tree in simplifications:
			print >> output_file, " ".join(tree.leaves())