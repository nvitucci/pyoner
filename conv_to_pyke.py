import sys, rdflib, re
from rdflib import OWL, RDFS, RDF
from pyke import knowledge_engine

def field_with_ns(f, nsmgr):
	if type(f) == rdflib.URIRef:
		return nsmgr.normalizeUri(f)
	elif type(f) == rdflib.BNode:
		return '_' + f.toPython()
	else:
		return '"' + f.toPython() + '"'

def triple_with_ns(t, nsmgr):
  t_ns = []
  for e in t:
		t_ns.append(field_with_ns(e, nsmgr))
  return tuple(t_ns)

if len(sys.argv) < 2:
	print "Usage: " + sys.argv[0] + " <ontology_file>"
	sys.exit()

ont = open(sys.argv[1], 'r')
g = rdflib.Graph()
g.parse(file=ont, format='turtle')
ont.close()

namespaces = {}

for n in g.namespace_manager.namespaces():
  if len(n[0]):
    namespaces[n[0]] = n[1]
  else:
    namespaces['default'] = n[1]

nsmgr = rdflib.namespace.NamespaceManager(rdflib.Graph())

for k, v in namespaces.iteritems():
  nsmgr.bind(k, v)

g.namespace_manager = nsmgr

# Sets containing the triples with their qnames

t_set = set()
for t in g:
  t_set.add(triple_with_ns(t, nsmgr))

for t in t_set:
  # print sys.argv[1].split('/')[-1].split('.')[0] + '_pyke' + '.triple'+ str(t)
  print 'triple' + str(t)

# Add special triples for BNodes

bnodes = set([x for t in g for x in t if type(x) == rdflib.BNode])

root_bn = set()

for n in bnodes:
	if len([x[0] for x in g.predicate_objects(n) if x[0] in [RDF['first'], RDF['rest']]]): # the blank nodes is part of a list
		ts = [x for x in g.transitive_subjects(RDF['rest'], n)] # the blank node is not 'rest' for any other node
		if len(ts) == 1 and ts[0] == n:
			root_bn.add(n)

lists = {}

for n in root_bn:
    # lists[n] = [x for x in g.transitive_objects(n, RDF['rest']) if x != RDF['nil'] and x != n]
		lists[n] = [field_with_ns(x[1], nsmgr) for o in g.transitive_objects(n, RDF['rest']) for x in g.predicate_objects(o) if x[0] == RDF['first'] and x[1] != RDF['nil']]
		# lists[n] = [field_with_ns(x[1], nsmgr) for o in g.transitive_objects(n, RDF['rest']) for x in g.predicate_objects(o)]

for n in lists:
	print 'triple(' + 'u\'_' + n + "\', u\'pyoner:_list\', " + str(tuple(lists[n])) + ')'

