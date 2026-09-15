# Security

JobFit is a portfolio project and should be hardened before production use.

## Configuration

- Never commit a real `SECRET_KEY`.
- Use a long random `SECRET_KEY` through environment variables.
- Use HTTPS in production.
- Prefer managed PostgreSQL with restricted credentials.
- Rotate credentials if they are exposed.
- Keep dependencies updated and review CI failures before merging changes.

## Authentication

The API uses signed JWT bearer tokens. Tokens should be treated as credentials and should not be stored in public logs or repositories.

## Reporting a vulnerability

Please open a private contact with the repository owner rather than publishing exploit details in a public issue.
