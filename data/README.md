# Local data workspace
Raw, interim and processed data are excluded from Git. Store immutable originals by dataset/release.
Commit only reviewed metadata without personal data or credentials.

Each acquisition manifest must record dataset_id, release, publisher, landing_url, resolved_download_url,
retrieved_at_utc, local_relative_path, bytes, sha256, license_url, license_review_status,
dictionary_url, coverage, taxonomy and notes. A checksum is evidence of file identity, not validity or permission.

Do not put interview recordings, resumes, API keys or licensed job-posting corpora here.
See [acquisition instructions](../docs/data-acquisition.md).
