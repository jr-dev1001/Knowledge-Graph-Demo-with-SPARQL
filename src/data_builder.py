# src/data_builder.py
from rdflib import Graph, Namespace, RDF, RDFS, Literal
from faker import Faker
import random

def build_dummy_graph(n_people: int = 6, n_companies: int = 2, seed: int | None = None) -> Graph:
    if seed is not None:
        Faker.seed(seed)
    fake = Faker()
    g = Graph()
    EX = Namespace("http://example.org/")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")

    g.bind("ex", EX)
    g.bind("foaf", FOAF)
    g.bind("rdfs", RDFS)
    g.bind("rdf", RDF)

    # Create companies
    companies = []
    for i in range(1, n_companies + 1):
        c = EX[f"Company{i}"]
        g.add((c, RDF.type, EX.Company))
        g.add((c, RDFS.label, Literal(fake.company())))
        companies.append(c)

    # Create people
    people = []
    for i in range(1, n_people + 1):
        p = EX[f"Person{i}"]
        g.add((p, RDF.type, FOAF.Person))
        g.add((p, FOAF.name, Literal(fake.name())))
        g.add((p, EX.age, Literal(fake.random_int(18, 75))))
        g.add((p, EX.worksAt, random.choice(companies)))
        people.append(p)

    # Link people with foaf:knows
    for i in range(len(people)):
        g.add((people[i], FOAF.knows, people[(i + 1) % len(people)]))

    return g
