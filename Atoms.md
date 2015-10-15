atomic
======

The next smallest piece of work you can do.


Some terminology used in this document:

__simple__ Undivided; one thing.
__complex__ Made up of more than one thing. They may not be complicated things, but they are numerous.


General breakdown of any piece of work:

// Naming
1. Name of work
1. Description of work
1. Details...Location, stuff, whatever. Independent variables?
1. Status
// Time
1. Due Date
1. Time estimate
// Relations
1. Tags/Labels
1. Children it's composed of
1. Parent(s) it composes?
1. Arbitrary linkages (Dependencies, relates to, all that stuff.)
1. Priority

__Name of work__ One-liner summary.
__Description of work__ Detailed body with whatever info's required.
__Details...__ File attachments, geolocation data, whatever else is desired.
__Status__ Is it done? Are you working on it?

__Due date__ When this thing actually needs to be done. Inherited from parent.
__Time estimate__ Because things take time.

__Tags/Labels__ Because tags are great.
__Children__ The whole idea of `atomic` is that things are decomposable into sub-entities. This shows that link.
__Parents?__ It'd make sense that multiple things could depend on the same sub-unit of work. Since complex work has its time estimate derived from its
atoms, all parents are already dynamic.
__Linkages__ Could be another set of tags with a really-long-and-human-unfriendly-naming scheme. Or you deal with the cascading CRUD operations - DB much?
__Priority__ A relation stronger than tags, because it allows for sorting.


## Implementation

Obviously, this data could be well represented by a RDBMS.

However, dealing with m2m linking tables is more work than I want right now.
Instead, I will attempt to deal with it solely in Python, and DB it later.

All nodes will be stored in a B-Tree backed list, provided by the `blist`
library.

