Changelog

Purpose
Track who changed what so the team stays updated.

Entry Format
[YYYY-MM-DD] [TYPE] [AUTHOR/INITIALS] [BRANCH] - Description

Types
[INIT]    Initial setup
[ADD]     Added new feature/file
[UPDATE]  Updated existing code/docs
[FIX]     Bug fix
[DB]      Database/schema/query change
[API]     API change
[UI]      Frontend/UI change
[DOCS]    Documentation change
[TEST]    Testing change
[REFACTOR] Code cleanup/restructure

Examples
[2026-05-02] [INIT] [PR] [main] - Created initial project structure
[2026-05-02] [DB] [AK] [db-schema] - Added appointments and slots schema
[2026-05-02] [API] [RS] [backend-auth] - Added basic login endpoint
[2026-05-02] [UI] [SM] [frontend-student] - Added student dashboard page

Changelog Size Rule
- Keep only recent/current sprint changes in this file
- If this file gets too long, move older entries into archive files
- Recommended limit: keep max 7 days OR max 50 entries here
- Archive older entries under changelog/archive/

Archive Format
changelog/archive/YYYY-MM-DD_to_YYYY-MM-DD.md

Branch-Based Option
If the team wants branch-specific changelogs, use:
changelog/branches/main.md
changelog/branches/backend.md
changelog/branches/frontend.md
changelog/branches/db.md

Current Entries

[2026-05-02] [INIT] [TEAM] [main] - Project initialized
[2026-05-02] [INIT] [TEAM] [main] - Base directory structure defined
[2026-05-02] [DOCS] [TEAM] [main] - Added agent instructions, TODO, API notes, DB notes, and project context
[2026-05-02] [DOCS] [TEAM] [main] - Added project README and updated contributor instructions
[2026-05-02] [DOCS] [TEAM] [main] - Updated README database wording before final database selection
[2026-05-02] [DOCS] [TEAM] [main] - Reworked README for public repository presentation
[2026-05-02] [DOCS] [TEAM] [main] - Improved README setup steps and project tree formatting
[2026-05-02] [DOCS] [TEAM] [main] - Added uv installation instructions to README
