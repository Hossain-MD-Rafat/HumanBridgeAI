-- Preserve rating quality metadata and typed preparation facts from actual sources.
ALTER TABLE task ADD COLUMN source_metadata_json TEXT NOT NULL DEFAULT '{}';
ALTER TABLE task_rating ADD COLUMN source_metadata_json TEXT NOT NULL DEFAULT '{}';
ALTER TABLE occupation_element_rating ADD COLUMN source_metadata_json TEXT NOT NULL DEFAULT '{}';

CREATE TABLE source_occupation (
    release_id TEXT NOT NULL REFERENCES dataset_release(release_id),
    code TEXT NOT NULL,
    taxonomy TEXT NOT NULL,
    title TEXT NOT NULL,
    PRIMARY KEY (release_id, code)
);

CREATE TABLE preparation_requirement (
    release_id TEXT NOT NULL,
    occupation_code TEXT NOT NULL,
    education TEXT,
    related_experience TEXT,
    on_job_training TEXT,
    PRIMARY KEY (release_id, occupation_code),
    FOREIGN KEY (release_id, occupation_code) REFERENCES source_occupation(release_id, code)
);

CREATE TABLE occupation_job_zone (
    release_id TEXT NOT NULL,
    occupation_code TEXT NOT NULL,
    job_zone INTEGER NOT NULL CHECK (job_zone BETWEEN 1 AND 5),
    source_metadata_json TEXT NOT NULL,
    PRIMARY KEY (release_id, occupation_code),
    FOREIGN KEY (release_id, occupation_code) REFERENCES occupation(release_id, occupation_code)
);

CREATE TABLE related_occupation (
    release_id TEXT NOT NULL,
    source_code TEXT NOT NULL,
    target_code TEXT NOT NULL,
    relation_tier TEXT NOT NULL,
    relation_index INTEGER NOT NULL,
    PRIMARY KEY (release_id, source_code, target_code),
    FOREIGN KEY (release_id, source_code) REFERENCES occupation(release_id, occupation_code),
    FOREIGN KEY (release_id, target_code) REFERENCES occupation(release_id, occupation_code)
);

CREATE TABLE occupation_alias (
    release_id TEXT NOT NULL,
    occupation_code TEXT NOT NULL,
    alias TEXT NOT NULL,
    source_codes TEXT,
    PRIMARY KEY (release_id, occupation_code, alias),
    FOREIGN KEY (release_id, occupation_code) REFERENCES occupation(release_id, occupation_code)
);
