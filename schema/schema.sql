CREATE SCHEMA online_platform;

CREATE TABLE online_platform.students (
    id    SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    name  TEXT,

    UNIQUE(email)
);

CREATE TABLE online_platform.lessons (
    id         SERIAL PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    end_time   TIMESTAMP NOT NULL,

    CHECK(start_time <= end_time)
);

CREATE TABLE online_platform.tasks (
    id          SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    type        TEXT NOT NULL,
    cost        INTEGER NOT NULL DEFAULT 10,
    solution    TEXT
);

CREATE TABLE online_platform.lesson_task (
    lesson_id INTEGER REFERENCES online_platform.lessons(id),
    task_id   INTEGER REFERENCES online_platform.tasks(id),
    task_cost INTEGER NULL,
    n_views   INTEGER NOT NULL DEFAULT 1,

    PRIMARY KEY(lesson_id, task_id)
);

CREATE TABLE online_platform.solutions (
    time           TIMESTAMP DEFAULT current_timestamp,
    content        TEXT NOT NULL,
    student_id     INTEGER REFERENCES online_platform.students(id),
    task_id        INTEGER,
    lesson_id      INTEGER,
    mark           INTEGER NOT NULL DEFAULT 0,

    PRIMARY KEY(student_id, task_id, lesson_id),
    FOREIGN KEY(lesson_id, task_id) REFERENCES online_platform.lesson_task(lesson_id, task_id)
);

CREATE OR REPLACE FUNCTION online_platform.mark_not_exceed_max() RETURNS trigger AS $func$
    BEGIN
        IF (NEW.mark > (SELECT task_cost FROM online_platform.lesson_task
            WHERE task_id = new.task_id AND lesson_id = new.lesson_id))
        THEN
            RAISE EXCEPTION "Solution must not exceed max task grade for lesson";
        END IF;
        RETURN new;
    END;
$func$ LANGUAGE plpgsql;

CREATE TRIGGER mark_trigger
BEFORE INSERT ON online_platform.solutions
FOR EACH ROW EXECUTE PROCEDURE mark_not_exceed_max();
