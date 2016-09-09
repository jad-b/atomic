# todo

* [ ] Refactor Shell (Valence) to use an API layer
* [ ] Extend Valence through the use of mixins
    * [ ] ReloadMixin
    * [ ] NodeMixin
* [x] Trim unneeded Graph work


### Old
* [ ] Save|Load TODOs to|from file
* [ ] List TODO's
    * [ ] Show all TODOs in hierarchy
        * [ ] Shows all un-done TODOs
        * [ ] `-a`, `--all` shows all TODOs

* [ ] Save TODO
    * [ ] `add` adds a TODO f/ CLI
    * [ ] Create TODO ArgumentParser
        * Inherit f/ using `parents=` kwarg or as a subparser
    * [ ] Store items by serially-increasing integer


        Schema:
            id          int       `--id, -i`
            name        string    `--name, -n`
            time        timedelta `--time, -t`
            done        bool      `--done, -d`
            description string    `--desc`
            # Hidden metadata
            modified    datetime

* [ ] Update TODO
    * [ ] Address TODO by name or integer ID
    * [ ] Accept CLI flags for modifying attributes

* [ ] Remove TODO
    * [ ] Remove a leaf TODO
    * [ ] Remove a non-leaf TODO
