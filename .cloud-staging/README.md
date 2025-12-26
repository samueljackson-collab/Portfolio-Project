# Cloud Content Staging Area

**Purpose:** Temporary location for organizing content from cloud sources before integrating into portfolio projects.

## Directory Structure

```
.cloud-staging/
├── google-drive/          # Content from Google Drive
├── claude-projects/       # Notes/code from Claude conversations
├── local-backups/         # Content from local backup archives
├── other-sources/         # Dropbox, OneDrive, etc.
└── README.md             # This file
```

## Usage

### 1. Import Stage
Place downloaded content in appropriate subdirectories

### 2. Review Stage
Review content for:
- Sensitive data (sanitize)
- Relevance (keep/discard)
- Mapping (which project?)

### 3. Integration Stage
Move content to appropriate project directories:
- `projects/XX-category/PRJ-XXX/assets/`

### 4. Cleanup Stage
Once integrated and committed, delete from staging

## Notes

- This directory is temporary
- Add `.cloud-staging/` to `.gitignore` if it contains sensitive data
- Delete staged content after integration is complete
