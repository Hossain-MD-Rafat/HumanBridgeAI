-- SQLite local foundation schema. Enable foreign keys on every connection.
-- Source snapshots and method versions are immutable; acquire bytes before inserting a release.
PRAGMA foreign_keys = ON;

CREATE TABLE dataset_release (
    release_id TEXT PRIMARY KEY,
    dataset_id TEXT NOT NULL,
    version TEXT NOT NULL,
    source_url TEXT NOT NULL,
    retrieved_at_utc TEXT NOT NULL,
    sha256 TEXT NOT NULL CHECK (
        length(sha256) = 64 AND sha256 NOT GLOB '*[^0-9a-f]*'
    ),
    license_note TEXT NOT NULL,
    UNIQUE (dataset_id, version, sha256)
);

CREATE TABLE occupation (
    release_id TEXT NOT NULL REFERENCES dataset_release(release_id),
    occupation_code TEXT NOT NULL,
    taxonomy TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    PRIMARY KEY (release_id, occupation_code)
);

CREATE TABLE task (
    release_id TEXT NOT NULL,
    occupation_code TEXT NOT NULL,
    task_id TEXT NOT NULL,
    statement TEXT NOT NULL,
    task_type TEXT,
    PRIMARY KEY (release_id, occupation_code, task_id),
    FOREIGN KEY (release_id, occupation_code)
        REFERENCES occupation(release_id, occupation_code)
);

CREATE TABLE scale (
    release_id TEXT NOT NULL REFERENCES dataset_release(release_id),
    scale_id TEXT NOT NULL,
    name TEXT NOT NULL,
    minimum REAL,
    maximum REAL,
    PRIMARY KEY (release_id, scale_id),
    CHECK (minimum IS NULL OR maximum IS NULL OR minimum < maximum)
);

-- Generic source elements cover skills, abilities, knowledge, context and activities.
CREATE TABLE element (
    release_id TEXT NOT NULL REFERENCES dataset_release(release_id),
    element_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    PRIMARY KEY (release_id, element_id)
);

CREATE TABLE occupation_element_rating (
    release_id TEXT NOT NULL,
    occupation_code TEXT NOT NULL,
    element_id TEXT NOT NULL,
    scale_id TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT '',
    value REAL,
    quality_flag TEXT,
    PRIMARY KEY (release_id, occupation_code, element_id, scale_id, category),
    FOREIGN KEY (release_id, occupation_code)
        REFERENCES occupation(release_id, occupation_code),
    FOREIGN KEY (release_id, element_id)
        REFERENCES element(release_id, element_id),
    FOREIGN KEY (release_id, scale_id)
        REFERENCES scale(release_id, scale_id)
);

CREATE TABLE task_rating (
    release_id TEXT NOT NULL,
    occupation_code TEXT NOT NULL,
    task_id TEXT NOT NULL,
    scale_id TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT '',
    value REAL,
    quality_flag TEXT,
    PRIMARY KEY (release_id, occupation_code, task_id, scale_id, category),
    FOREIGN KEY (release_id, occupation_code, task_id)
        REFERENCES task(release_id, occupation_code, task_id),
    FOREIGN KEY (release_id, scale_id)
        REFERENCES scale(release_id, scale_id)
);

-- Crosswalk source is separate from the source/target taxonomy versions.
-- allocation_weight is NULL unless an actual, justified allocation is available.
CREATE TABLE occupation_crosswalk (
    mapping_release_id TEXT NOT NULL REFERENCES dataset_release(release_id),
    source_taxonomy TEXT NOT NULL,
    source_code TEXT NOT NULL,
    target_taxonomy TEXT NOT NULL,
    target_code TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    allocation_weight REAL CHECK (
        allocation_weight IS NULL OR allocation_weight BETWEEN 0 AND 1
    ),
    PRIMARY KEY (
        mapping_release_id, source_taxonomy, source_code,
        target_taxonomy, target_code
    )
);

CREATE TABLE geography (
    geography_id TEXT NOT NULL,
    boundary_vintage TEXT NOT NULL,
    geography_type TEXT NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (geography_id, boundary_vintage)
);

CREATE TABLE labor_statistic (
    release_id TEXT NOT NULL REFERENCES dataset_release(release_id),
    taxonomy TEXT NOT NULL,
    occupation_code TEXT NOT NULL,
    geography_id TEXT NOT NULL,
    boundary_vintage TEXT NOT NULL,
    universe TEXT NOT NULL,
    metric TEXT NOT NULL,
    period TEXT NOT NULL,
    unit TEXT NOT NULL,
    value REAL,
    quality_flag TEXT,
    PRIMARY KEY (
        release_id, taxonomy, occupation_code, geography_id,
        boundary_vintage, universe, metric, period
    ),
    FOREIGN KEY (geography_id, boundary_vintage)
        REFERENCES geography(geography_id, boundary_vintage)
);

CREATE TABLE county_observation (
    release_id TEXT NOT NULL REFERENCES dataset_release(release_id),
    county_fips TEXT NOT NULL CHECK (
        length(county_fips) = 5 AND county_fips NOT GLOB '*[^0-9]*'
    ),
    boundary_vintage TEXT NOT NULL,
    variable_id TEXT NOT NULL,
    universe TEXT NOT NULL,
    estimate REAL,
    margin_of_error REAL CHECK (margin_of_error IS NULL OR margin_of_error >= 0),
    quality_flag TEXT,
    PRIMARY KEY (release_id, county_fips, boundary_vintage, variable_id),
    FOREIGN KEY (county_fips, boundary_vintage)
        REFERENCES geography(geography_id, boundary_vintage)
);

CREATE TABLE analysis_run (
    run_id TEXT PRIMARY KEY,
    method_version TEXT NOT NULL,
    capability_date TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    parameters_json TEXT NOT NULL
);

CREATE TABLE analysis_run_input (
    run_id TEXT NOT NULL REFERENCES analysis_run(run_id),
    release_id TEXT NOT NULL REFERENCES dataset_release(release_id),
    PRIMARY KEY (run_id, release_id)
);

CREATE TABLE task_score (
    run_id TEXT NOT NULL,
    release_id TEXT NOT NULL,
    occupation_code TEXT NOT NULL,
    task_id TEXT NOT NULL,
    ai_exposure REAL CHECK (ai_exposure IS NULL OR ai_exposure BETWEEN 0 AND 100),
    human_dependency REAL CHECK (
        human_dependency IS NULL OR human_dependency BETWEEN 0 AND 100
    ),
    workflow TEXT NOT NULL CHECK (
        workflow IN ('automate_candidate', 'augment', 'human_led', 'insufficient_evidence')
    ),
    components_json TEXT NOT NULL,
    evidence_json TEXT NOT NULL,
    uncertainty_note TEXT NOT NULL,
    PRIMARY KEY (run_id, release_id, occupation_code, task_id),
    FOREIGN KEY (run_id, release_id) REFERENCES analysis_run_input(run_id, release_id),
    FOREIGN KEY (release_id, occupation_code, task_id)
        REFERENCES task(release_id, occupation_code, task_id)
);

CREATE TABLE transition (
    run_id TEXT NOT NULL,
    release_id TEXT NOT NULL,
    source_code TEXT NOT NULL,
    target_code TEXT NOT NULL,
    rank INTEGER NOT NULL CHECK (rank BETWEEN 1 AND 5),
    score REAL,
    components_json TEXT NOT NULL,
    explanation_json TEXT NOT NULL,
    constraints_json TEXT NOT NULL,
    PRIMARY KEY (run_id, release_id, source_code, target_code),
    UNIQUE (run_id, release_id, source_code, rank),
    CHECK (source_code <> target_code),
    FOREIGN KEY (run_id, release_id) REFERENCES analysis_run_input(run_id, release_id),
    FOREIGN KEY (release_id, source_code)
        REFERENCES occupation(release_id, occupation_code),
    FOREIGN KEY (release_id, target_code)
        REFERENCES occupation(release_id, occupation_code)
);
