# Claude Science database schema

This document records the structure of the Claude Science local database: the table definitions, the column lists, the enum values observed in the enum columns, and the file layout around the database. It holds no row data. It was read on 2026-11-08 from a copy of the database, opened read-only and immutable. Regenerate the sections above the file layout with `python skills/migrating-from-claude-science/scripts/dump_claude_science_schema.py --db <copy> --out docs/science-ultrapowers/claude-science-schema.md`; the script keeps the hand-written file layout section.

## Tables

### projects

```sql
CREATE TABLE `projects` (
	`id` text(255) PRIMARY KEY NOT NULL,
	`name` text(255),
	`description` text,
	`context` text,
	`created_at` integer NOT NULL,
	`updated_at` integer NOT NULL,
	`user_id` text(255),
	`uploads_frame_id` text(36), `memory_enabled` integer, `archived_at` integer, `artifacts_rev` integer DEFAULT 0 NOT NULL, `default_use_case_id` text,
	FOREIGN KEY (`uploads_frame_id`) REFERENCES `frames`(`id`) ON UPDATE no action ON DELETE set null
)
```

| cid | name | type | notnull | default | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | id | text(255) | 1 |  | 1 |
| 1 | name | text(255) | 0 |  | 0 |
| 2 | description | TEXT | 0 |  | 0 |
| 3 | context | TEXT | 0 |  | 0 |
| 4 | created_at | INTEGER | 1 |  | 0 |
| 5 | updated_at | INTEGER | 1 |  | 0 |
| 6 | user_id | text(255) | 0 |  | 0 |
| 7 | uploads_frame_id | text(36) | 0 |  | 0 |
| 8 | memory_enabled | INTEGER | 0 |  | 0 |
| 9 | archived_at | INTEGER | 0 |  | 0 |
| 10 | artifacts_rev | INTEGER | 1 | 0 | 0 |
| 11 | default_use_case_id | TEXT | 0 |  | 0 |

### memories

```sql
CREATE TABLE `memories` (
	`id` text(36) PRIMARY KEY NOT NULL,
	`user_id` text(255) NOT NULL,
	`body` text NOT NULL,
	`subject_project_id` text(255),
	`subject_artifact_id` text(36),
	`subject_version_id` text(36),
	`subject_frame_id` text(36),
	`source_frame_id` text(36),
	`origin` text NOT NULL,
	`evidence` text DEFAULT 'stated' NOT NULL,
	`superseded_by` text(36),
	`created_at` integer NOT NULL,
	`updated_at` integer NOT NULL,
	`last_surfaced_at` integer, `category_id` text(36) REFERENCES memory_categories(`id`) ON DELETE SET NULL, `use_case_id` text, `use_case_program` text,
	FOREIGN KEY (`subject_project_id`) REFERENCES `projects`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`subject_artifact_id`) REFERENCES `artifacts`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`subject_version_id`) REFERENCES `artifact_versions`(`id`) ON UPDATE no action ON DELETE set null,
	FOREIGN KEY (`subject_frame_id`) REFERENCES `frames`(`id`) ON UPDATE no action ON DELETE set null,
	FOREIGN KEY (`source_frame_id`) REFERENCES `frames`(`id`) ON UPDATE no action ON DELETE set null,
	FOREIGN KEY (`superseded_by`) REFERENCES `memories`(`id`) ON UPDATE no action ON DELETE set null
)
```

| cid | name | type | notnull | default | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | id | text(36) | 1 |  | 1 |
| 1 | user_id | text(255) | 1 |  | 0 |
| 2 | body | TEXT | 1 |  | 0 |
| 3 | subject_project_id | text(255) | 0 |  | 0 |
| 4 | subject_artifact_id | text(36) | 0 |  | 0 |
| 5 | subject_version_id | text(36) | 0 |  | 0 |
| 6 | subject_frame_id | text(36) | 0 |  | 0 |
| 7 | source_frame_id | text(36) | 0 |  | 0 |
| 8 | origin | TEXT | 1 |  | 0 |
| 9 | evidence | TEXT | 1 | 'stated' | 0 |
| 10 | superseded_by | text(36) | 0 |  | 0 |
| 11 | created_at | INTEGER | 1 |  | 0 |
| 12 | updated_at | INTEGER | 1 |  | 0 |
| 13 | last_surfaced_at | INTEGER | 0 |  | 0 |
| 14 | category_id | text(36) | 0 |  | 0 |
| 15 | use_case_id | TEXT | 0 |  | 0 |
| 16 | use_case_program | TEXT | 0 |  | 0 |

### user_agents

```sql
CREATE TABLE `user_agents` (
	`id` text(36) PRIMARY KEY NOT NULL,
	`user_id` text(255) NOT NULL,
	`name` text(32) NOT NULL,
	`display_name` text(255) NOT NULL,
	`description` text NOT NULL,
	`system_prompt` text NOT NULL,
	`icon_key` text(64) DEFAULT 'lightning' NOT NULL,
	`color_key` text(64) DEFAULT 'accent-main' NOT NULL,
	`tags` text DEFAULT '[]' NOT NULL,
	`skill_names` text DEFAULT '[]' NOT NULL,
	`enabled` integer DEFAULT true NOT NULL,
	`created_at` integer NOT NULL,
	`updated_at` integer NOT NULL
, `skill_tombstones` text DEFAULT '[]' NOT NULL, `connector_tombstones` text DEFAULT '[]' NOT NULL, unrestricted INTEGER NOT NULL DEFAULT 0, `created_by` text, `created_in_frame_id` text, `created_in_project_id` text, `modified_by` text, `modified_in_frame_id` text, `modified_in_project_id` text, `modified_at` integer)
```

| cid | name | type | notnull | default | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | id | text(36) | 1 |  | 1 |
| 1 | user_id | text(255) | 1 |  | 0 |
| 2 | name | text(32) | 1 |  | 0 |
| 3 | display_name | text(255) | 1 |  | 0 |
| 4 | description | TEXT | 1 |  | 0 |
| 5 | system_prompt | TEXT | 1 |  | 0 |
| 6 | icon_key | text(64) | 1 | 'lightning' | 0 |
| 7 | color_key | text(64) | 1 | 'accent-main' | 0 |
| 8 | tags | TEXT | 1 | '[]' | 0 |
| 9 | skill_names | TEXT | 1 | '[]' | 0 |
| 10 | enabled | INTEGER | 1 | true | 0 |
| 11 | created_at | INTEGER | 1 |  | 0 |
| 12 | updated_at | INTEGER | 1 |  | 0 |
| 13 | skill_tombstones | TEXT | 1 | '[]' | 0 |
| 14 | connector_tombstones | TEXT | 1 | '[]' | 0 |
| 15 | unrestricted | INTEGER | 1 | 0 | 0 |
| 16 | created_by | TEXT | 0 |  | 0 |
| 17 | created_in_frame_id | TEXT | 0 |  | 0 |
| 18 | created_in_project_id | TEXT | 0 |  | 0 |
| 19 | modified_by | TEXT | 0 |  | 0 |
| 20 | modified_in_frame_id | TEXT | 0 |  | 0 |
| 21 | modified_in_project_id | TEXT | 0 |  | 0 |
| 22 | modified_at | INTEGER | 0 |  | 0 |

### frames

```sql
CREATE TABLE `frames` (
	`id` text(36) PRIMARY KEY NOT NULL,
	`parent_frame_id` text(36),
	`root_frame_id` text(36),
	`agent_name` text(255) NOT NULL,
	`status` text(50) NOT NULL,
	`input_data` text,
	`output_data` text,
	`context_data` text,
	`model` text(255),
	`effort` text(20),
	`input_tokens` integer,
	`output_tokens` integer,
	`total_cost` real,
	`created_at` integer NOT NULL,
	`updated_at` integer NOT NULL,
	`completed_at` integer,
	`project_id` text(255),
	`name` text(255),
	`conversation_type` text(50) NOT NULL,
	`artifact_id` text(36),
	`task_summary` text,
	`mentioned_artifact_ids` text,
	`specialists_used` text,
	`is_hidden` integer, status_description text, compute_enabled TEXT, `delegate_name` text(255), `cache_read_tokens` integer, `cache_write_tokens` integer, `last_user_message_at` integer, last_extract_msg_idx integer, `root_seq` integer DEFAULT 0 NOT NULL, `aux_input_tokens` integer, `aux_output_tokens` integer, `aux_cache_read_tokens` integer, `aux_cache_write_tokens` integer, `aux_cost` real, `token_class_usage` text, `starred_at` integer, `compute_route` text,
	FOREIGN KEY (`parent_frame_id`) REFERENCES `frames`(`id`) ON UPDATE no action ON DELETE set null,
	FOREIGN KEY (`root_frame_id`) REFERENCES `frames`(`id`) ON UPDATE no action ON DELETE set null,
	FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`) ON UPDATE no action ON DELETE cascade
)
```

| cid | name | type | notnull | default | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | id | text(36) | 1 |  | 1 |
| 1 | parent_frame_id | text(36) | 0 |  | 0 |
| 2 | root_frame_id | text(36) | 0 |  | 0 |
| 3 | agent_name | text(255) | 1 |  | 0 |
| 4 | status | text(50) | 1 |  | 0 |
| 5 | input_data | TEXT | 0 |  | 0 |
| 6 | output_data | TEXT | 0 |  | 0 |
| 7 | context_data | TEXT | 0 |  | 0 |
| 8 | model | text(255) | 0 |  | 0 |
| 9 | effort | text(20) | 0 |  | 0 |
| 10 | input_tokens | INTEGER | 0 |  | 0 |
| 11 | output_tokens | INTEGER | 0 |  | 0 |
| 12 | total_cost | REAL | 0 |  | 0 |
| 13 | created_at | INTEGER | 1 |  | 0 |
| 14 | updated_at | INTEGER | 1 |  | 0 |
| 15 | completed_at | INTEGER | 0 |  | 0 |
| 16 | project_id | text(255) | 0 |  | 0 |
| 17 | name | text(255) | 0 |  | 0 |
| 18 | conversation_type | text(50) | 1 |  | 0 |
| 19 | artifact_id | text(36) | 0 |  | 0 |
| 20 | task_summary | TEXT | 0 |  | 0 |
| 21 | mentioned_artifact_ids | TEXT | 0 |  | 0 |
| 22 | specialists_used | TEXT | 0 |  | 0 |
| 23 | is_hidden | INTEGER | 0 |  | 0 |
| 24 | status_description | TEXT | 0 |  | 0 |
| 25 | compute_enabled | TEXT | 0 |  | 0 |
| 26 | delegate_name | text(255) | 0 |  | 0 |
| 27 | cache_read_tokens | INTEGER | 0 |  | 0 |
| 28 | cache_write_tokens | INTEGER | 0 |  | 0 |
| 29 | last_user_message_at | INTEGER | 0 |  | 0 |
| 30 | last_extract_msg_idx | INTEGER | 0 |  | 0 |
| 31 | root_seq | INTEGER | 1 | 0 | 0 |
| 32 | aux_input_tokens | INTEGER | 0 |  | 0 |
| 33 | aux_output_tokens | INTEGER | 0 |  | 0 |
| 34 | aux_cache_read_tokens | INTEGER | 0 |  | 0 |
| 35 | aux_cache_write_tokens | INTEGER | 0 |  | 0 |
| 36 | aux_cost | REAL | 0 |  | 0 |
| 37 | token_class_usage | TEXT | 0 |  | 0 |
| 38 | starred_at | INTEGER | 0 |  | 0 |
| 39 | compute_route | TEXT | 0 |  | 0 |

### frame_messages

```sql
CREATE TABLE `frame_messages` (
	`frame_id` text(36) NOT NULL,
	`idx` integer NOT NULL,
	`msg_json` text NOT NULL, `msg_uuid` TEXT,
	PRIMARY KEY(`frame_id`, `idx`),
	FOREIGN KEY (`frame_id`) REFERENCES `frames`(`id`) ON UPDATE no action ON DELETE cascade
)
```

| cid | name | type | notnull | default | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | frame_id | text(36) | 1 |  | 1 |
| 1 | idx | INTEGER | 1 |  | 2 |
| 2 | msg_json | TEXT | 1 |  | 0 |
| 3 | msg_uuid | TEXT | 0 |  | 0 |

### artifacts

```sql
CREATE TABLE `artifacts` (
	`id` text(36) PRIMARY KEY NOT NULL,
	`project_id` text(255) NOT NULL,
	`root_frame_id` text(36) NOT NULL,
	`frame_id` text(36),
	`filename` text(255) NOT NULL,
	`created_at` integer NOT NULL,
	`latest_version_id` text(36),
	`is_user_upload` integer NOT NULL,
	`is_ephemeral` integer NOT NULL,
	`folder_id` text(36),
	`sort_order` integer NOT NULL,
	`priority` text(20) DEFAULT 'unknown' NOT NULL, superseded_by_artifact_id text, `consumed_at` integer, `is_branch_mint` integer DEFAULT false NOT NULL, `agent_rename_history` text, `retention` text,
	FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`latest_version_id`) REFERENCES `artifact_versions`(`id`) ON UPDATE no action ON DELETE set null,
	FOREIGN KEY (`folder_id`) REFERENCES `artifact_folders`(`id`) ON UPDATE no action ON DELETE set null
)
```

| cid | name | type | notnull | default | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | id | text(36) | 1 |  | 1 |
| 1 | project_id | text(255) | 1 |  | 0 |
| 2 | root_frame_id | text(36) | 1 |  | 0 |
| 3 | frame_id | text(36) | 0 |  | 0 |
| 4 | filename | text(255) | 1 |  | 0 |
| 5 | created_at | INTEGER | 1 |  | 0 |
| 6 | latest_version_id | text(36) | 0 |  | 0 |
| 7 | is_user_upload | INTEGER | 1 |  | 0 |
| 8 | is_ephemeral | INTEGER | 1 |  | 0 |
| 9 | folder_id | text(36) | 0 |  | 0 |
| 10 | sort_order | INTEGER | 1 |  | 0 |
| 11 | priority | text(20) | 1 | 'unknown' | 0 |
| 12 | superseded_by_artifact_id | TEXT | 0 |  | 0 |
| 13 | consumed_at | INTEGER | 0 |  | 0 |
| 14 | is_branch_mint | INTEGER | 1 | false | 0 |
| 15 | agent_rename_history | TEXT | 0 |  | 0 |
| 16 | retention | TEXT | 0 |  | 0 |

### artifact_versions

```sql
CREATE TABLE `artifact_versions` (
	`id` text(36) PRIMARY KEY NOT NULL,
	`artifact_id` text(36) NOT NULL,
	`version_number` integer NOT NULL,
	`frame_id` text(36),
	`content_type` text(100) NOT NULL,
	`size_bytes` integer NOT NULL,
	`checksum` text(64) NOT NULL,
	`storage_path` text(512) NOT NULL,
	`created_at` integer NOT NULL,
	`extracted_code` text,
	`code_description` text,
	`lineage_messages` text,
	`agent_name` text(255),
	`language` text(50),
	`is_intermediate` integer NOT NULL,
	`dependency_mappings` text,
	`environment_snapshot` text,
	`annotations` text,
	`parent_version_id` text(36), `lineage_snapshot_hash` text(64), `env_snapshot_hash` text(64), `producing_cell_id` text(36), `cell_sources` text, `is_checkpoint` integer DEFAULT 0,
	FOREIGN KEY (`artifact_id`) REFERENCES `artifacts`(`id`) ON UPDATE no action ON DELETE cascade
)
```

| cid | name | type | notnull | default | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | id | text(36) | 1 |  | 1 |
| 1 | artifact_id | text(36) | 1 |  | 0 |
| 2 | version_number | INTEGER | 1 |  | 0 |
| 3 | frame_id | text(36) | 0 |  | 0 |
| 4 | content_type | text(100) | 1 |  | 0 |
| 5 | size_bytes | INTEGER | 1 |  | 0 |
| 6 | checksum | text(64) | 1 |  | 0 |
| 7 | storage_path | text(512) | 1 |  | 0 |
| 8 | created_at | INTEGER | 1 |  | 0 |
| 9 | extracted_code | TEXT | 0 |  | 0 |
| 10 | code_description | TEXT | 0 |  | 0 |
| 11 | lineage_messages | TEXT | 0 |  | 0 |
| 12 | agent_name | text(255) | 0 |  | 0 |
| 13 | language | text(50) | 0 |  | 0 |
| 14 | is_intermediate | INTEGER | 1 |  | 0 |
| 15 | dependency_mappings | TEXT | 0 |  | 0 |
| 16 | environment_snapshot | TEXT | 0 |  | 0 |
| 17 | annotations | TEXT | 0 |  | 0 |
| 18 | parent_version_id | text(36) | 0 |  | 0 |
| 19 | lineage_snapshot_hash | text(64) | 0 |  | 0 |
| 20 | env_snapshot_hash | text(64) | 0 |  | 0 |
| 21 | producing_cell_id | text(36) | 0 |  | 0 |
| 22 | cell_sources | TEXT | 0 |  | 0 |
| 23 | is_checkpoint | INTEGER | 0 | 0 | 0 |

### artifact_dependencies

```sql
CREATE TABLE `artifact_dependencies` (
	`id` text(36) PRIMARY KEY NOT NULL,
	`artifact_version_id` text(36) NOT NULL,
	`depends_on_version_id` text(36) NOT NULL,
	`reference_name` text(255),
	`created_at` integer NOT NULL,
	FOREIGN KEY (`artifact_version_id`) REFERENCES `artifact_versions`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`depends_on_version_id`) REFERENCES `artifact_versions`(`id`) ON UPDATE no action ON DELETE cascade
)
```

| cid | name | type | notnull | default | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | id | text(36) | 1 |  | 1 |
| 1 | artifact_version_id | text(36) | 1 |  | 0 |
| 2 | depends_on_version_id | text(36) | 1 |  | 0 |
| 3 | reference_name | text(255) | 0 |  | 0 |
| 4 | created_at | INTEGER | 1 |  | 0 |

### artifact_folders

```sql
CREATE TABLE `artifact_folders` (
	`id` text(36) PRIMARY KEY NOT NULL,
	`project_id` text(255) NOT NULL,
	`parent_id` text(36),
	`name` text(255) NOT NULL,
	`sort_order` integer NOT NULL,
	`root_frame_id` text(36),
	`is_conversation_folder` integer NOT NULL,
	`is_user_uploads_folder` integer NOT NULL,
	`created_at` integer NOT NULL,
	`updated_at` integer NOT NULL,
	FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`parent_id`) REFERENCES `artifact_folders`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`root_frame_id`) REFERENCES `frames`(`id`) ON UPDATE no action ON DELETE set null
)
```

| cid | name | type | notnull | default | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | id | text(36) | 1 |  | 1 |
| 1 | project_id | text(255) | 1 |  | 0 |
| 2 | parent_id | text(36) | 0 |  | 0 |
| 3 | name | text(255) | 1 |  | 0 |
| 4 | sort_order | INTEGER | 1 |  | 0 |
| 5 | root_frame_id | text(36) | 0 |  | 0 |
| 6 | is_conversation_folder | INTEGER | 1 |  | 0 |
| 7 | is_user_uploads_folder | INTEGER | 1 |  | 0 |
| 8 | created_at | INTEGER | 1 |  | 0 |
| 9 | updated_at | INTEGER | 1 |  | 0 |

### verification_checks

```sql
CREATE TABLE "verification_checks" (
	`id` text(36) PRIMARY KEY NOT NULL,
	`root_frame_id` text(36) NOT NULL,
	`artifact_version_id` text(36),
	`claim_id` text(36),
	`claim` text,
	`verdict` text NOT NULL CHECK (`verdict` IN ('pass','warn','fail','inconclusive')),
	`severity` text(16),
	`evidence` text,
	`rebuttal` text,
	`reviewer_idx` integer,
	`reviewer_model` text(64),
	`reviewer_frame_id` text(36),
	`reviewer_kind` text(16),
	`source_ref` text NOT NULL,
	`resolution` text,
	`status` text NOT NULL DEFAULT 'open' CHECK (`status` IN ('open','claimed','resolved','unaddressed')),
	`reflag_count` integer,
	`created_at` integer NOT NULL,
	FOREIGN KEY (`root_frame_id`) REFERENCES `frames`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`claim_id`) REFERENCES `session_claims`(`id`) ON UPDATE no action ON DELETE set null
)
```

| cid | name | type | notnull | default | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | id | text(36) | 1 |  | 1 |
| 1 | root_frame_id | text(36) | 1 |  | 0 |
| 2 | artifact_version_id | text(36) | 0 |  | 0 |
| 3 | claim_id | text(36) | 0 |  | 0 |
| 4 | claim | TEXT | 0 |  | 0 |
| 5 | verdict | TEXT | 1 |  | 0 |
| 6 | severity | text(16) | 0 |  | 0 |
| 7 | evidence | TEXT | 0 |  | 0 |
| 8 | rebuttal | TEXT | 0 |  | 0 |
| 9 | reviewer_idx | INTEGER | 0 |  | 0 |
| 10 | reviewer_model | text(64) | 0 |  | 0 |
| 11 | reviewer_frame_id | text(36) | 0 |  | 0 |
| 12 | reviewer_kind | text(16) | 0 |  | 0 |
| 13 | source_ref | TEXT | 1 |  | 0 |
| 14 | resolution | TEXT | 0 |  | 0 |
| 15 | status | TEXT | 1 | 'open' | 0 |
| 16 | reflag_count | INTEGER | 0 |  | 0 |
| 17 | created_at | INTEGER | 1 |  | 0 |

### execution_log

```sql
CREATE TABLE `execution_log` (
	`id` text(36) PRIMARY KEY NOT NULL,
	`frame_id` text(36) NOT NULL,
	`cell_index` integer NOT NULL,
	`kernel_id` text(36) NOT NULL,
	`conda_env` text(255) NOT NULL,
	`language` text(16) NOT NULL,
	`source` text NOT NULL,
	`stdout` text,
	`stderr` text,
	`exit_status` text(16) NOT NULL,
	`created_at` integer NOT NULL,
	`files_written` text,
	`error_lineno` integer, `kernel_kind` text(16), `origin` text DEFAULT 'agent' NOT NULL, `detection` text, `files_read` text, `user_intervention` text,
	FOREIGN KEY (`frame_id`) REFERENCES `frames`(`id`) ON UPDATE no action ON DELETE cascade
)
```

| cid | name | type | notnull | default | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | id | text(36) | 1 |  | 1 |
| 1 | frame_id | text(36) | 1 |  | 0 |
| 2 | cell_index | INTEGER | 1 |  | 0 |
| 3 | kernel_id | text(36) | 1 |  | 0 |
| 4 | conda_env | text(255) | 1 |  | 0 |
| 5 | language | text(16) | 1 |  | 0 |
| 6 | source | TEXT | 1 |  | 0 |
| 7 | stdout | TEXT | 0 |  | 0 |
| 8 | stderr | TEXT | 0 |  | 0 |
| 9 | exit_status | text(16) | 1 |  | 0 |
| 10 | created_at | INTEGER | 1 |  | 0 |
| 11 | files_written | TEXT | 0 |  | 0 |
| 12 | error_lineno | INTEGER | 0 |  | 0 |
| 13 | kernel_kind | text(16) | 0 |  | 0 |
| 14 | origin | TEXT | 1 | 'agent' | 0 |
| 15 | detection | TEXT | 0 |  | 0 |
| 16 | files_read | TEXT | 0 |  | 0 |
| 17 | user_intervention | TEXT | 0 |  | 0 |

### directory_attachments

```sql
CREATE TABLE `directory_attachments` (
	`server_uuid` text(36) NOT NULL,
	`agent_name` text(255) NOT NULL,
	`user_id` text(255) NOT NULL,
	`created_at` integer NOT NULL, "excluded_tools" text NOT NULL DEFAULT '[]',
	PRIMARY KEY(`server_uuid`, `agent_name`, `user_id`)
)
```

| cid | name | type | notnull | default | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | server_uuid | text(36) | 1 |  | 1 |
| 1 | agent_name | text(255) | 1 |  | 2 |
| 2 | user_id | text(255) | 1 |  | 3 |
| 3 | created_at | INTEGER | 1 |  | 0 |
| 4 | excluded_tools | TEXT | 1 | '[]' | 0 |

### capability_settings

```sql
CREATE TABLE `capability_settings` (
	`user_id` text(255) NOT NULL,
	`kind` text(32) NOT NULL,
	`key` text(255) NOT NULL,
	`enabled` integer DEFAULT true NOT NULL,
	`updated_at` integer NOT NULL,
	PRIMARY KEY(`user_id`, `kind`, `key`)
)
```

| cid | name | type | notnull | default | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | user_id | text(255) | 1 |  | 1 |
| 1 | kind | text(32) | 1 |  | 2 |
| 2 | key | text(255) | 1 |  | 3 |
| 3 | enabled | INTEGER | 1 | true | 0 |
| 4 | updated_at | INTEGER | 1 |  | 0 |

### compaction_archives

```sql
CREATE TABLE `compaction_archives` (
	`id` text(36) PRIMARY KEY NOT NULL,
	`frame_id` text(36) NOT NULL,
	`compaction_index` integer NOT NULL,
	`message_count` integer NOT NULL,
	`token_count` integer,
	`summary` text NOT NULL,
	`messages` text NOT NULL,
	`created_at` integer NOT NULL,
	FOREIGN KEY (`frame_id`) REFERENCES `frames`(`id`) ON UPDATE no action ON DELETE cascade
)
```

| cid | name | type | notnull | default | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | id | text(36) | 1 |  | 1 |
| 1 | frame_id | text(36) | 1 |  | 0 |
| 2 | compaction_index | INTEGER | 1 |  | 0 |
| 3 | message_count | INTEGER | 1 |  | 0 |
| 4 | token_count | INTEGER | 0 |  | 0 |
| 5 | summary | TEXT | 1 |  | 0 |
| 6 | messages | TEXT | 1 |  | 0 |
| 7 | created_at | INTEGER | 1 |  | 0 |

### user_secrets

```sql
CREATE TABLE `user_secrets` (
	`id` text(36) PRIMARY KEY NOT NULL,
	`user_id` text(255) NOT NULL,
	`name` text(128) NOT NULL,
	`provider` text(16) NOT NULL,
	`encrypted_value` text NOT NULL,
	`credential_type` text(32),
	`buckets` text,
	`region` text(64),
	`description` text(256),
	`created_at` integer NOT NULL,
	`updated_at` integer NOT NULL
)
```

| cid | name | type | notnull | default | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | id | text(36) | 1 |  | 1 |
| 1 | user_id | text(255) | 1 |  | 0 |
| 2 | name | text(128) | 1 |  | 0 |
| 3 | provider | text(16) | 1 |  | 0 |
| 4 | encrypted_value | TEXT | 1 |  | 0 |
| 5 | credential_type | text(32) | 0 |  | 0 |
| 6 | buckets | TEXT | 0 |  | 0 |
| 7 | region | text(64) | 0 |  | 0 |
| 8 | description | text(256) | 0 |  | 0 |
| 9 | created_at | INTEGER | 1 |  | 0 |
| 10 | updated_at | INTEGER | 1 |  | 0 |

## Observed enum values

- `memories.origin`: `agent_tool`, `extractor`
- `memories.evidence`: `observed`, `stated`
- `verification_checks.status`: `resolved`, `unaddressed`
- `verification_checks.verdict`: `fail`, `pass`, `warn`
- `frames.status`: `cancelled`, `completed`, `failed`
- `frames.conversation_type`: `agent`, `uploads`
- `artifacts.retention`: `NULL`
- `capability_settings.kind`: `skill`

## File layout

Written by hand from inspecting one installation. Names and shapes only; no values.

### Config home

The config home is `%USERPROFILE%\.claude-science\`. It holds:

- `config.toml`. Keys: `data_dir` (where the data directory lives; the migration reads it), `last_move_from` (the previous data directory after a move; the migration reads it), and, names only, `data_dir_from`, `data_dir_move_entries`, `data_dir_move_copied`, `data_dir_move_from_registered`, `last_move_from_registered`. Every key is a string.
- `active-org.json`. Keys: `org_uuid` (names the active org), and, names only, `org_name`, `account_uuid`, `login_owner_data_dir`. Every value is a string.
- `encryption.key*` (never read; there may be a `.dpapi` companion).
- `last-data-dir-move.json`, written by a data-directory move (absent on the recording machine, whose move is recorded in `config.toml` instead); the migration reads `config.toml` first.

### Data directory

The data directory is the `data_dir` of `config.toml` (a default under the config home when the key is absent). It holds:

- `orgs/<org_uuid>/`, one folder per account the machine signed into; several can exist, and `active-org.json` names the active one.
- `mcp/directory-cache.json`: an object with `fetchedAt` (integer), `accountId` (string) and `connectors` (list of objects). Each connector has the keys `id`, `name`, `source`, `authState`, `transport`, `backendUrl`, `iconUrl` (strings) and `hidden`, `isOrgProvisioned` (booleans).
- `runtime/`, plus other working folders the migration does not read.
- A top-level `operon-cli.db`, `preferences.json` and `skills/` can also sit directly in the data directory, beside `orgs/`; the org folder is the one the migration reads.

### Per org folder

- `operon-cli.db`, plus `operon-cli.db-wal` and `operon-cli.db-shm` when present. The database is large (hundreds of MB); open only a copy.
- `preferences.json`, plain JSON (see below).
- `artifacts/<project_id>/<artifact_id>/v<8-hex>_<filename>`: one file per artifact version.
- `skills/<name>/`: published skills.
- Other entries the migration does not read: `compaction-history/`, `marketplace-plugins/`, `staging/`, `tool-results/`, `workspaces/`, `models-last-good.json`, `install-id`; an org under an organization policy also has `org_policy.json` and `org_policy.contact`.

### Host-linked artifacts

An artifact version whose `storage_path` starts with `~/` is a host file, not a copy in the artifact tree. The text after `~/` is a Windows path, in the form `~/<drive>:/...`. The file may be missing when the drive is not mounted.

### preferences.json

Shape only, from one installation. A value that is a path, a domain or an id is never recorded.

- `approvalGrants`: object with the keys `always`, `alwaysOrigins`, `project`.
  - `always`: object with the keys `allow`, `deny`, `ask`. Each is an object; `allow` has the keys `host` and `network`, each a list of strings. In the sample `deny` and `ask` were empty objects.
  - `project`: object keyed by `<project_id>`. Each value is an object with the keys `allow`, `deny`, `ask`; `allow` had the keys `credential_access`, `customize_mutation`, `local_exec`, each a list of strings.
  - `alwaysOrigins`: object with the keys `host` and `network`. Each is an object keyed by an origin string (for `host`, a mode prefix such as `rw:` followed by a Windows path; for `network`, a domain); each value is an object with the string keys `userId`, `rootFrameId`, `projectId`.
- `hostGrants`: list; empty in the sample, so the element shape was not observed.
- `userAllowedDomains`: list; empty in the sample, so the element shape was not observed (expected: strings).
- `builtinAllowlistDisabledGroups`: list of strings.
- `autoMode`: boolean.
- `gpuEnabled`: boolean.
- `reviewerModel`: string.
- `memoryEnabled`: boolean.

All eight keys were present. The file has many other keys (internal flags beginning with `_`, onboarding, connector pins and so on) that the migration ignores.

### Value formats

Types only.

- `user_agents.skill_names`: SQLite text; after `json.loads` a Python list of strings.
- `memories.created_at`: SQLite integer; every row is epoch milliseconds (13 digits), not ISO text.
- `created_at` of `artifacts`, `artifact_versions`, `verification_checks`, `execution_log` and `frames`, and `frames.updated_at`: SQLite integers, epoch milliseconds (13 digits).
- `artifact_versions.dependency_mappings`: SQLite text (JSON); `artifact_versions.environment_snapshot`: NULL or text (JSON).

### Published skills

`orgs/<org_uuid>/skills/<name>/SKILL.md`, with the skill's other files beside it (`LICENSE.txt`, `templates/`, ...). Bundled, example and lab skills all appear here by name.
