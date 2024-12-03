# Postgres Setup

## usage
To start the database server:
`docker compose up`

To regenerate the database server with a fresh initialization of the tables and data:
`docker compose down -v`

To restart PostgreSQL server without rewriting the database:
`docker compose down`