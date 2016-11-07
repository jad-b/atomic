# todo

'?' means an active question.
'=' means in progress.

* [x] Get all tests passing
* [x] Update FileAPI to use new NodeAPI, EdgeAPI classes
* [x] Utilize the CLI sub-commands to parse shell commands
* [x] Extend Valence through the use of mixins
    * [x] ReloadMixin
    * [x] NodeMixin
    * [x] ShlexMixin
* [x] Parse markdown into node relationships
    - [x] Parse BeautifulSoup tree into tuples
    - [x] Import tuples in through the API
    - [x] Test Markdown => Graph.
* [?] Distinguish between setting a tag and deleting a key = value with "key=''"
    - Tags are KVs with an empty value.
    - Sending `{'tagOrKeyName': None}` indicates deletion requested.
    - Tags are set by '<Name>=' on the CLI
    - `atomic update [--replace] <name> <key=values>... [--rm [k1 t1 k2]...]`
* [ ] Search by attributes
    - Nail down CRUD ops w/ tests
    - Implement DFS & BFS search
    * [ ] Filter returned attributes
* [?] Refactor into packages
    - photon/frontend: what you see; CLI, Shell
    - darkmatter/backend: how you store data; Persistence backends
    - absorb: data intake
    - parse: Because there's a lot of parsing that goes on.

# Good Ideas?
* [] Support the notion of depth
* Create indexes on node variables, like 'name'
    * Could be updated asynchronously
