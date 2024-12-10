# Postgres Setup

## usage
To start the database server:
`docker compose up -d`

To regenerate the database server with a fresh initialization of the tables and data:
`docker compose down -v`

To restart PostgreSQL server without rewriting the database:
`docker compose down`

To install python libraries:
`pip install -r requirements.txt`

To store the dataset into the fresh database:
`python .\store_data.py`

To run the web app:
`python .\app.py`

User interface can then be accessed at: http://localhost:8000/

_Note: To fetch more data using `fetch_service_shows.py` or `fetch_top_shows.py`, an environment variable RAPID_API_KEY is needed_