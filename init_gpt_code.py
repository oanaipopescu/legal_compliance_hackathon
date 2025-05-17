from rdflib import Graph
from pyshacl import validate

# --- Regulation Graph (RDF)
regulation_ttl = """
@prefix : <http://example.org#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

:PersonalData a rdf:Class .

:GDPR_Encryption_Requirement a :RegulationRule ;
  :appliesTo :PersonalData ;
  :requires :Encryption .
"""

# --- Company Policy Graph (RDF)
policy_ttl = """
@prefix : <http://example.org#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

:CustomerEmail a :PersonalData ;
  :encrypted false .

:PaymentInfo a :PersonalData ;
  :encrypted true .
"""

# --- SHACL Shape (RDF)
shapes_ttl = """
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix : <http://example.org#> .

:PersonalDataShape
  a sh:NodeShape ;
  sh:targetClass :PersonalData ;
  sh:property [
    sh:path :encrypted ;
    sh:hasValue true ;
    sh:message "Personal data must be encrypted to comply with GDPR." ;
  ] .
"""

# --- Load RDF graphs
data_graph = Graph()
data_graph.parse(data=policy_ttl, format="turtle")

shapes_graph = Graph()
shapes_graph.parse(data=shapes_ttl, format="turtle")

# --- Run SHACL Validation
conforms, report_graph, report_text = validate(
    data_graph,
    shacl_graph=shapes_graph,
    inference='rdfs',
    debug=False
)

print(report_text[:1000])  # Display first 1000 characters of the validation report
