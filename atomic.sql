CREATE TYPE status_state AS ENUM ('pending', 'started', 'complete');

CREATE TABLE work (
    /* Naming */
    work_id serial PRIMARY KEY,
    title text NOT NULL,
    description text,
    -- details - arbitrary table foreign key
    status status_state DEFAULT 'pending',
    /* Time */
    due timestamp(0) with time zone,
    estimate interval HOUR TO MINUTE,
    /* Relations */
    -- tags/labels: many-to-many
    -- children
    -- links
    priority int DEFAULT 0 CHECK (priority >= 0 and priority <= 10)
);

CREATE TABLE tag (
    tag_id serial PRIMARY KEY,
    tag text NOT NULL
);

/* Many-to-one relationship for tags to work */
CREATE TABLE work_tag (
    tag_id int REFERENCES tag (tag_id) ON UPDATE CASCADE,
    work_id int REFERENCES work (work_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT tag_work_pkey PRIMARY KEY (tag_id, work_id)
);

CREATE TABLE work_lineage (
    parent_id int REFERENCES work (work_id) ON UPDATE CASCADE ON DELETE CASCADE,
    child_id int REFERENCES work (work_id) ON UPDATE CASCADE,
    CONSTRAINT parent_child_pkey PRIMARY KEY (parent_id, child_id)
);

CREATE TABLE work_link (
    source_id int REFERENCES work (work_id) ON UPDATE CASCADE ON DELETE CASCADE,
    dest_id int REFERENCES work (work_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT source_dest_pkey PRIMARY KEY (source_id, dest_id)
);
