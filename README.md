# Postgres Setup

## Usage
To start the database server:

    docker compose up -d

To regenerate the database server with a fresh initialization of the tables and data:

    docker compose down -v

To restart PostgreSQL server without rewriting the database:

    docker compose down

To create Python virtual environment:

    python -m venv venv

To activate Python virtual environment (Windows):

    ./venv/Scripts/Activate.ps1

To install python libraries:

    pip install -r requirements.txt

To store the dataset into the fresh database:

    python .\store_data.py

**To run the web app:**
    
    python .\app.py

User interface can then be accessed at: http://localhost:8000/

_Note: To fetch more data using `fetch_service_shows.py` or `fetch_top_shows.py`, an environment variable RAPID_API_KEY is needed_

## Code Organization

### `app.py`
This file is the primary application backend and web server for the frontend. It also is in charge of all user based transactions to the database.

### `store_data.py`
This script stores the data contained in the `/datascrapes` directory, namely the files following the pattern "top*.json" and "data*.json", into the database, doing the appropriate formatting and adapting as necessary.

### `fetch_service_shows.py`
This script reaches out to the Streaming Availability API for more data based on given filters (in the code) and writes the response to a JSON file for use with `store_data.py`. 

### `fetch_top_shows.py`
Same as `fetch_service_shows.py`, this file reaches out but grabs only the "Top Shows" from a predefined list of streaming services and makes that data available by writing it to a JSON file.

### `/sql`
Files in this directory are SQL scripts. They are nested under `sql/subscripts/`, where `sql/init.sql` calls the various scripts inside the nested directory.

### `/web`
Files in this directory are HTML files. They contain JavaScript and CSS embedded within, and are the source material for the web app's display within a browser.

### `/datascrapes`
Files in this directory are JSON files. They contain data about titles that are then available to store into the database.

### `docker-compose.yaml`
This file is used to define the docker container deployment structure.

### `requirements.txt`
This file is used for ease in installing requisite Python dependencies.

### `store_netflix_data.py`
This file, like `store_data.py`, formats and stores the data contained in `/datascrapes/netflix.json` into the database. This data follows a different format than the rest of the datascrapes/*.json files, so must be handled separately.

## Benchmark Tests
After installing `pgbench` using the following command (using linux or WSL in Windows):

    sudo apt-get install postgresql-contrib

Benchmarks were taken by running the following commmands (with "admin" as the postgres password when prompted):

*for all query types:*

    pgbench -p 5432 -d postgres -h localhost -U postgres -c 90 -T 600 -n

*for read-only/SELECT only queries:*
    
    pgbench -p 5432 -d postgres -h localhost -U postgres -c 90 -T 600 -S -n