atomic
=====
Complexity divided.

## What it has/can do
* Provide a simple API for overlaying Graph interactions on top of data sources:
  databases, third-party APIs, web crawling, and simple in-memory graphs.
* Keep a schema as arbitrary as JSON, or tightly-defined as a Python class.
* "Walk" your graph with custom operations.
* Built-in notions of sequencing & hierarchy, w/ common operations on such
  provided.

## Where It Could Go
* Add operations for partitioning graphs
* Event-driven architecture makes it easy for multiple actors to work on the
* Partition your graph across distributed backends.
* Supports the interaction of separate graphs
* "Optimistic" asynchronous indexing speeds up writes & reads.


## Interfaces
At its heart, `atomic` is a standard API for graph operations. What makes
it different from libraries like `networkx`, which it uses to represent the
graph in memory, is its ability to implement this API
across different data stores, as well as a building - block approach to adding
features. The latter means that higher - level operations, like search algorithms,
are built atop of primitive operations, like retrieve, update, and delete. Thus,
you only have to re - implement the lowest - level API to take advantage of
higher - level functionality, albeit naively.

## Extending the Model
In Atomic, all  a nodes or edge _has_ to have is a unique identifier. Beyond
that ID, it's an arbitrary flat collection of key-value pairs. However, Nodes
and Edges commonly represent something in the real world, with specific values
and behaviors that are much richer than bags of key-values. That's why the Node and Edge
classes are supplied. While these classes simply set the keys and ID as attributes,
they provide a starting point for inheritance or composition to provide
"gradual" schema enforcement. With this, representing a ToDo item is easy;
subclass Node, set required attributes as arguments in `__init__`, and you're
now free to add methods and schema validation as you wish. As long your object can
become JSON when `to_json` is called, you maintain compatibility.


## Terminology
Since we're dealing with graphs, we have nodes and edges. A Node is a vertice
within the graph, and commonly represents a noun, but can also be used to
represent actions. An Edge is a relationship between two Nodes, and can also be
made to represent an action.

### On the Word "Node"
Does a node, by any other name, make more sense to a lay-person?

- __entity__: a thing with distinct and independent existence.
- __node__: a point at which lines or pathways intersect or branch; a central or connecting point
- __item__: an individual article or unit, especially one that is part of a list, collection, or
  set
- __thing__:
    - an object that one need not, cannot, or does not wish to give a specific name to.
    - *an action, activity, event, thought, or utterance*
    - used euphemistically to refer to a man's penis.
- __object__: a material thing that can be seen and touched

"Thing" may be a winner.
