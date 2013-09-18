from rdflib import RDF, RDFS, OWL

def checkIfOWLLD(g):
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

  s_set = set(g.subjects())
  p_set = set(g.predicates())
  o_set = set(g.objects())

  for fp in forbiddenPredicates:
    if fp in p_set or fp in o_set:
      matchingPredicates.append(fp)
      # raise OntologyNotOWLLD('Ontology not in the OWL-LD profile because of axiom ' + fp)

  if len(matchingPredicates):
    return (False, matchingPredicates)
  else:
    return (True, [])
