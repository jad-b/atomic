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
