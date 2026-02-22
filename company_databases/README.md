# Company Databases Directory

This directory contains separate SQLite databases for each company.
Each company has complete data isolation with its own database file.

## Structure
- Each company gets a file named: `{company_database_name}.db`
- Example: `acme-corp_a1b2c3d4.db`

## Benefits
- Complete data isolation between companies
- Independent backups per company
- Scalable architecture
- Easy to migrate individual companies

## Note
This directory is automatically managed by the system.
Do not manually edit or delete database files.
