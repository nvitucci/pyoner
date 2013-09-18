import sys, rdflib, re
from rdflib import OWL, RDFS, RDF
from pyke import knowledge_engine

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

def triple_with_ns(t, nsmgr):
    t_ns = []
    for e in t:
        if type(e) == rdflib.URIRef:
            t_ns.append(nsmgr.normalizeUri(e))
        else:
            t_ns.append('"' + e.toPython() + '"')
    return tuple(t_ns)

# ont = open('/home/nick/work/ontoforce/ontologies/public/v2/ontoforce_integration_ont_v2.ttl', 'r')
# ont_inf = open('/tmp/inf_ont.ttl')

# ont = open('test.ttl', 'r')
ont = open(sys.argv[1], 'r')
g = rdflib.Graph()
g.parse(file=ont, format='turtle')
ont.close()

ont_inf = open('test_inf.ttl', 'r')
g_inf = rdflib.Graph()
g_inf.parse(file=ont_inf, format='turtle')
ont_inf.close()

# Join namespaces

namespaces = {}

for n in g.namespace_manager.namespaces():
	if len(n[0]):
		namespaces[n[0]] = n[1]
	else:
		namespaces['default'] = n[1]

for i, v in enumerate(g_inf.namespace_manager.namespaces()):
	if v[1] not in namespaces.values():
		namespaces['added' + str(i)] = v[1]

nsmgr = rdflib.namespace.NamespaceManager(rdflib.Graph())

for k, v in namespaces.iteritems():
	nsmgr.bind(k, v)

g.namespace_manager = nsmgr
g_inf.namespace_manager = nsmgr

# Sets containing the triples with their qnames

t_set = set()
t_inf_set = set()
for t in g:
	t_set.add(triple_with_ns(t, nsmgr))
for t in g_inf:
	t_inf_set.add(triple_with_ns(t, nsmgr))

# nsmgr = rdflib.namespace.NamespaceManager(rdflib.Graph())
# g.namespace_manager = nsmgr

# Check if the ontology is in OWL-LD, if not "correct" it

ss = set(g.subjects())
ps = set(g.predicates())
os = set(g.objects())

if not checkIfOWLLD(ss, ps, os)[0]:
	# raise Exception('Ontology not in OWL-LD!')
	toRem = []
	for t in g:
		if type(t[0]) == rdflib.term.BNode or type(t[1]) == rdflib.term.BNode or type (t[2]) == rdflib.term.BNode:
			toRem.append(t)

	for r in toRem:
		g.remove(r)

# g.commit()

ss = set(g.subjects())
ps = set(g.predicates())
os = set(g.objects())

# Write to temp file

# tmp = open('ontology.kfb', 'w')

# for t in g:														
# 	nt = []
# 	for i in t:
# 		if type(i) == rdflib.term.URIRef:
# 			nt.append(g.namespace_manager.normalizeUri(i))
# 		elif type(i) == rdflib.term.Literal:
# 			nt.append('"' + i + '"')
# 	tmp.write('triple(\'' + nt[0] + '\', \'' + nt[1] + '\', \'' + nt[2] + '\')\n')
# 
# tmp.close()
# 
# engine = knowledge_engine.engine('.')
# engine.activate('fc_owlld')
# 
# kb = engine.get_kb('ontology')
# # kb.dump_specific_facts()
# 
# triples = kb.engine.knowledge_bases['ontology'].entity_lists['triple']
# 
# g2 = rdflib.Graph()
# g2.namespace_manager = nsmgr
# 
# namespaces = {}
# for n in g.namespaces():
# 	namespaces[n[0]] = rdflib.Namespace(n[1])
# 
# if 'owl' not in namespaces.keys():
# 	namespaces['owl'] = OWL
# if 'rdfs' not in namespaces.keys():
# 	namespaces['rdfs'] = RDFS
# if 'rdf' not in namespaces.keys():
# 	namespaces['rdf'] = RDF

# Assert facts in PyKE

engine = knowledge_engine.engine('.')
for t in t_set:
	engine.assert_('ontology', 'triple', t)

# Run inference

engine.activate('fc_owlld')
triples = engine.knowledge_bases['ontology'].entity_lists['triple'].case_specific_facts

# Build set with inference results

pyke_t_set = set()
for t in triples:
	pyke_t_set.add(t)

# Convert results of inference to a graph: TODO from here

g_new = rdflib.Graph()
g_new.namespace_manager = nsmgr

for t in triples:
	converted_triple_array = []

	for f in t:
		try:                                                      
			converted_triple_array.append(rdflib.util.to_term(f))
		except:
			# a = re.compile("^[a-zA-Z0-9]+:.*$")
			a = re.compile("^[^:]+:.*$")

			if a.match(f):
				ns = f.split(':')[0]
				e = f.split(':')[1]
				converted_triple_array.append(namespaces[ns] + str(e))

	converted_triple = tuple(converted_triple_array)
	g_new.add(converted_triple)

ont_pyke = open(sys.argv[2], 'w')
ont_pyke.write(g_new.serialize(format='turtle'))
ont_pyke.close()

# print g2.serialize(format='nt')

# print len(g), len(g_inf), len(triples.case_specific_facts), len(g2)
# print namespaces
# 
# t1 = set(g)
# t2 = set(g_inf)
# 
# print len(t1.intersection(t2)), len(t2.intersection(t1)), len(t1.difference(t2)), len(t2.difference(t1))
# 
# # for i in t1.difference(t2):
# for i in t2.difference(t1):
# 	for f in i:
# 		if type(f) == rdflib.URIRef:
# 			print nsmgr.normalizeUri(f),
# 		else:
# 			print '"' + rdflib.Literal(f) + '"',
# 	print
