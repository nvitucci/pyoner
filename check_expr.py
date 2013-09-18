import rdflib
from rdflib import RDF, RDFS, OWL

# constructs = 
# 	{'AL': 'AL',
#  	'C': 'C',
#  	'D': '(D)',
#  	'E': 'E',
#  	'EL': 'EL',
#  	'ELPP': 'EL++',
#  	'F': 'F',
# 	'H': 'H',
#  	'I': 'I',
#  	'N': 'N',
#  	'O': 'O',
#  	'Q': 'Q',
#  	'R': 'R',
#  	'S': 'S',
#  	'TRAN': '+',
#  	'U': 'U'
# }

def checkIfOWLLD(ss, ps, os):
	forbiddenPredicates = [
		OWL['complementOf'],
		OWL['disjointUnionOf'],
		OWL['intersectionOf'],
		OWL['unionOf'],
		OWL['oneOf'],
		OWL['allValuesFrom'],
		OWL['hasSelf'],
		OWL['hasValue'],
		OWL['someValuesFrom'],
		OWL['cardinality'],
		OWL['maxCardinality'],
		OWL['minCardinality'],
		OWL['qualifiedMaxCardinality'],
		OWL['qualifiedMinCardinality'],
		OWL['qualifiedCardinality'],
		OWL['hasKey'],
		OWL['propertyChainAxiom'],
		OWL['AllDifferent'],
		OWL['AllDisjointClasses'],
		OWL['AllDisjointProperties'],
		OWL['sourceIndividual'],
		OWL['assertionProperty'],
		OWL['targetIndividual'],
		OWL['targetValue'],
		OWL['ReflexiveProperty']
	]

	matchingPredicates = []

	for fp in forbiddenPredicates:
		if fp in ps or fp in os:
			matchingPredicates.append(fp)
			# raise OntologyNotOWLLD('Ontology not in the OWL-LD profile because of axiom ' + fp)

	if len(matchingPredicates):
		return (False, matchingPredicates)
	else:
		return (True, [])

# Constructs with order
constructs = {
	'AL': ('AL', 1),
	'C': ('C', 2),
	'D': ('(D)', 13),
	'E': ('E', 4),
	'EL': 'EL',
	'ELPP': 'EL++',
	'F': ('F', 11),
	'H': ('H', 6),
	'I': ('I', 8),
	'N': ('N', 9),
	'O': ('O', 7),
	'Q': ('Q', 10),
	'R': ('R', 5),
	'S': ('S', 0),
	'TRAN': ('+', 12),
	'U': ('U', 3)
}

def prune_constructs(c):
	if 'AL' in c:
		if 'E' in c and 'U' in c:
			c.remove('E')
			c.remove('U')
			if 'C' not in c:
				c.add('C')
	if ('N' in c or 'Q' in c) and 'F' in c:
		c.remove('F')
	if 'Q' in c and 'N' in c:
		c.remove('N')
	if 'AL' in c and 'C' in c and 'TRAN' in c:
		c.remove('AL')
		c.remove('C')
		c.remove('TRAN')
		c.add('S')
	if 'R' in c and 'H' in c:
		c.remove('H')

def check(ss, ps, os, constr):
	if OWL['FunctionalProperty'] in os:
		constr.add('F')
	
	if OWL['InverseFunctionalProperty'] in os:
		constr.add('I')
		constr.add('F')
	
	if OWL['TransitiveProperty'] in os:
		constr.add('TRAN')
	
	if OWL['AsymmetricProperty'] in os or OWL['ReflexiveProperty'] in os or OWL['IrreflexiveProperty'] in os:
		constr.add('R')
	
	if OWL['SymmetricProperty'] in os:
		constr.add('I')
	
	#

	if OWL['inverseOf'] in ps:
		constr.add('I')

	if OWL['maxCardinality'] in ps or OWL['minCardinality'] in ps or OWL['cardinality'] in ps:
		constr.add('N')

	if OWL['maxQualifiedCardinality'] in ps or OWL['minQualifiedCardinality'] in ps or OWL['qualifiedCardinality'] in ps:
		constr.add('Q')

	# Differentiate with data oneOf
	#
	# if OWL['oneOf'] in ps:
	#	constr.add('U')
	#	constr.add('O')

	if OWL['intersectionOf'] in ps:
		constr.add('AL')

	if OWL['unionOf'] in ps:
		constr.add('U')

	if OWL['hasValue'] in ps:
		constr.add('E')
		constr.add('O')

	if OWL['hasSelf'] in ps:
		constr.add('R')

	if OWL['disjointWith'] in ps:
		constr.add('C')
	
ont = open('/home/nick/Scaricati/BioStuff/Reactome/biopax-level3.owl', 'r')
g = rdflib.Graph()
g.parse(file=ont)

pred_set = set(g.predicates())
subj_set = set(g.subjects())
obj_set = set(g.objects())

print checkIfOWLLD(subj_set, pred_set, obj_set)

temp_constructs = set()

temp_constructs.add('AL')

check(subj_set, pred_set, obj_set, temp_constructs)
prune_constructs(temp_constructs)

temp_constructs_list = list(temp_constructs)
temp_constructs_list.sort(key=lambda x: constructs[x][1])

print ''.join(temp_constructs_list)
