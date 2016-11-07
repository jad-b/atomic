atomic
=====

Does a node, by any other name, make more sense to a lay-person?

- __node__: a point at which lines or pathways intersect or branch; a central or connecting point
- __item__: an individual article or unit, especially one that is part of a list, collection, or
  set
- __thing__:
    - an object that one need not, cannot, or does not wish to give a specific name to.
    - *an action, activity, event, thought, or utterance*
    - used euphemistically to refer to a man's penis.
- __object__: a material thing that can be seen and touched

"Thing" may be a winner.


## Interfaces
At its heart, `atomic` is a standard API for graph operations. What makes
it different from libraries like `networkx`, which it uses to represent the
graph in memory, is its ability to implement this API
across different data stores, as well as a building - block approach to adding
features. The latter means that higher - level operations, like search algorithms,
are built atop of primitive operations, like retrieve, update, and delete. Thus,
you only have to re - implement the lowest - level API to take advantage of
higher - level functionality, albeit naively.

## Layout
```
* api
    * spec
    * file
    * postgres
    * http
* client
    * cli
    * shell
* graph
    * node
    * serial
    * algo
* utils
    * display
    * log
    * parse
```
