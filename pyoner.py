import sys, rdflib, re
import checkProfile
from rdflib import OWL, RDFS, RDF
from pyke import knowledge_engine

def triple_with_ns(t, nsmgr):
	t_ns = []
	for e in t:
		if type(e) == rdflib.URIRef:
			t_ns.append(nsmgr.normalizeUri(e))
		elif type(e) == rdflib.BNode:
			t_ns.append('_' + e.toPython())		
		else:
			t_ns.append('"' + e.toPython() + '"')
	return tuple(t_ns)

# ont = open('test.ttl', 'r')
if len(sys.argv) > 3:
	profile = sys.argv[3]
else:
	profile = 'LD'

print 'Chosen profile: ' + profile

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

# Check if the ontology is in OWL-LD, if not "correct" it

if profile == 'LD':
	if not checkProfile.checkIfOWLLD(g)[0]:
		# raise Exception('Ontology not in OWL-LD!')

		# only removes blank nodes
		toRem = []
		for t in g:
			if type(t[0]) == rdflib.term.BNode or type(t[1]) == rdflib.term.BNode or type (t[2]) == rdflib.term.BNode:
				toRem.append(t)

		for r in toRem:
			g.remove(r)

# Assert facts in PyKE

engine = knowledge_engine.engine('.')
for t in t_set:
	engine.assert_('ontology', 'triple', t)

# Run inference

if profile == 'LD':
	engine.activate('fc_owlld')
elif profile == 'RL':
	engine.activate('fc_owlrl')

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
			# print f + ' ---> ' + str(type(rdflib.util.to_term(f)))
		except:
			# a = re.compile("^[a-zA-Z0-9]+:.*$")
			ns_re = re.compile("^[^:]+:.*$")

			if ns_re.match(f):
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
