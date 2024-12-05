from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, conlist
import psycopg2
from typing import List, Generator, Optional
import os

# Database Configuration
DATABASE_URL = "dbname=postgres user=postgres password=admin host=localhost"
conn = psycopg2.connect(DATABASE_URL)

# FastAPI Initialization
app = FastAPI()

# Pydantic Model
class ConsumerCreate(BaseModel):
    name: str
    address: str
    budget: int

class Consumer(ConsumerCreate):
    consumer_id: str

class ConsumersToDelete(BaseModel):
    consumer_ids: list[str]

class WatchlistItemCreate(BaseModel):
    title_id: str
    priority: int

class WatchlistItem(WatchlistItemCreate):
    watchlist_item_id: str
    watchlist_id: str

class WatchlistItemsToDelete(BaseModel):
    watchlist_item_ids: list[str]

class Title(BaseModel):
    title_id: str
    name: str
    type: Optional[str] = None
    rating: Optional[str] = None
    release_date: Optional[str] = None
    genre: Optional[str] = None
    category: Optional[str] = None
    director: Optional[str] = None

# Dependency to get a new cursor for each request
def get_cursor() -> Generator:
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    finally:
        cursor.close()

# Create Consumer Endpoint
@app.post("/consumers/", response_model=Consumer)
def create_consumer(consumer: ConsumerCreate, cursor = Depends(get_cursor)):
    cursor.execute("INSERT INTO consumer (name, address, budget) VALUES (%s, %s, %s) RETURNING consumer_id", (consumer.name, consumer.address, consumer.budget))
    consumer_id = cursor.fetchone()[0]
    return {"consumer_id": consumer_id, **consumer.model_dump()}

# Get Consumers Endpoint
@app.get("/consumers/", response_model=List[Consumer])
def read_consumers(skip: int = 0, limit: int = 10, cursor = Depends(get_cursor)):
    cursor.execute("SELECT consumer_id, name, address, budget FROM consumer ORDER BY consumer_id OFFSET %s LIMIT %s", (skip, limit))
    consumers = cursor.fetchall()
    return [{"consumer_id": consumer_id, "name": name, "address": address, "budget": budget} for consumer_id, name, address, budget in consumers]

# Delete Multiple Consumers Endpoint
@app.delete("/consumers/", response_model=List[str])
def delete_consumers(consumers_to_delete: ConsumersToDelete, cursor = Depends(get_cursor)):
    cursor.execute("DELETE FROM consumer WHERE consumer_id = ANY(%s::UUID[]) RETURNING consumer_id", (consumers_to_delete.consumer_ids,))
    deleted = cursor.fetchall()
    if not deleted:
        raise HTTPException(status_code=404, detail="Consumers not found")
    return [consumer_id[0] for consumer_id in deleted]

###################################

# Get Watchlist Items for a Consumer Endpoint
@app.get("/watchlists/{consumer_id}", response_model=List[WatchlistItem])
def read_watchlist(consumer_id: str, cursor = Depends(get_cursor)):
    cursor.execute("""
        SELECT wi.watchlist_item_id, wi.watchlist_id, wi.title_id, wi.priority
        FROM watchlist_item wi
        JOIN watchlist w ON wi.watchlist_id = w.watchlist_id
        WHERE w.consumer_id = %s
    """, (consumer_id,))
    watchlist_items = cursor.fetchall()
    return [
        {"watchlist_item_id": wi_id, "watchlist_id": w_id, "title_id": title_id, "priority": priority}
        for wi_id, w_id, title_id, priority in watchlist_items
    ]

# Add Watchlist Item Endpoint
@app.post("/watchlists/{consumer_id}/items", response_model=WatchlistItem)
def create_watchlist_item(consumer_id: str, item: WatchlistItemCreate, cursor = Depends(get_cursor)):
    cursor.execute("SELECT watchlist_id FROM watchlist WHERE consumer_id = %s", (consumer_id,))
    watchlist = cursor.fetchone()
    if not watchlist:
        cursor.execute("INSERT INTO watchlist (consumer_id) VALUES (%s) RETURNING watchlist_id", (consumer_id,))
        watchlist_id = cursor.fetchone()[0]
    else:
        watchlist_id = watchlist[0]
    
    cursor.execute("""
        INSERT INTO watchlist_item (watchlist_id, title_id, priority) 
        VALUES (%s, %s, %s) 
        RETURNING watchlist_item_id
    """, (watchlist_id, item.title_id, item.priority))
    watchlist_item_id = cursor.fetchone()[0]
    return {"watchlist_item_id": watchlist_item_id, "watchlist_id": watchlist_id, **item.model_dump()}

# Delete Multiple Watchlist Items Endpoint
@app.delete("/watchlist_items/", response_model=List[str])
def delete_watchlist_items(items_to_delete: WatchlistItemsToDelete, cursor = Depends(get_cursor)):
    cursor.execute("DELETE FROM watchlist_item WHERE watchlist_item_id = ANY(%s::UUID[]) RETURNING watchlist_item_id", (items_to_delete.watchlist_item_ids,))
    deleted = cursor.fetchall()
    if not deleted:
        raise HTTPException(status_code=404, detail="Watchlist items not found")
    return [item_id[0] for item_id in deleted]


# Get Titles Endpoint
@app.get("/titles/", response_model=List[Title])
def read_titles(skip: int = 0, limit: int = 10, cursor = Depends(get_cursor)):
    cursor.execute("SELECT title_id, name, type, rating, release_date, genre, category, director FROM title OFFSET %s LIMIT %s", (skip, limit))
    titles = cursor.fetchall()
    return [{"title_id": title_id, "name": name, "type": type, "rating": rating, "release_date": release_date, "genre": genre, "category": category, "director": director} for title_id, name, type, rating, release_date, genre, category, director in titles]

# Get Title Details
@app.get("/titles/{title_id}", response_model=Title)
def get_title_name(title_id: str, cursor = Depends(get_cursor)):
    cursor.execute("""
        SELECT *
        FROM title
        WHERE title_id = %s
    """, (title_id,))
    title = cursor.fetchone()[0]
    return {"title_id": title_id, **title.model_dump()}


####################################


# Serve HTML Icon
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("web/favicon.ico")

# Serve HTML Home Page
@app.get("/", response_class=HTMLResponse)
def get_consumer_management():
    with open("web/index.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Serve HTML Consumer Page
@app.get("/consumer", response_class=HTMLResponse)
def get_consumer_management():
    with open("web/consumer.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Serve HTML Watchlist Page
@app.get("/watchlist", response_class=HTMLResponse)
def get_consumer_management():
    with open("web/watchlist.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
