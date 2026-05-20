-- Remove the unused future-scope password reset token table from older local databases.
DROP TABLE IF EXISTS password_reset_tokens;
