from itertools import combinations
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, conlist
import psycopg2
from typing import List, Generator, Optional, Tuple
import os

# Database Configuration
DATABASE_URL = "dbname=postgres user=postgres password=admin host=localhost"
conn = psycopg2.connect(DATABASE_URL)

# FastAPI Initialization
app = FastAPI()

# Pydantic Models
class StreamingServiceCreate(BaseModel):
    name: str

class StreamingService(StreamingServiceCreate):
    service_id: str

class StreamingServicesToDelete(BaseModel):
    service_ids: list[str]

class PackageCreate(BaseModel):
    service_id: str
    name: str
    price: Optional[float]
    period: Optional[int]
    ad_supported: Optional[bool]
    deprecated: Optional[bool]

class Package(PackageCreate):
    package_id: str

class PackagesToDelete(BaseModel):
    package_ids: list[str]

class StreamingTitle(BaseModel):
    service_id: str
    title_id: str
    arrival_date: Optional[int] = None
    leaving_date: Optional[int] = None

class ConsumerCreate(BaseModel):
    name: str
    address: str
    budget: int

class Consumer(ConsumerCreate):
    consumer_id: str

class ConsumersToDelete(BaseModel):
    consumer_ids: list[str]

class Subscription(BaseModel):
    consumer_id: str
    package_id: str
    renewal_date: Optional[str] = None

class Watchlist(BaseModel):
    watchlist_id: str
    consumer_id: str

class WatchlistItemCreate(BaseModel):
    title_id: str

class WatchlistItem(WatchlistItemCreate):
    watchlist_item_id: str
    watchlist_id: str

class WatchlistItemsToDelete(BaseModel):
    watchlist_item_ids: list[str]

class TitleCreate(BaseModel):
    title_name: str
    type: Optional[str] = None
    rating: Optional[str] = None
    release_date: Optional[str] = None
    category: Optional[str] = None
    creator: Optional[str] = None

class Title(TitleCreate):
    title_id: str

class TitlesToDelete(BaseModel):
    title_ids: list[str]

# Dependency to get a new cursor for each request
def get_cursor() -> Generator:
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    finally:
        cursor.close()

# Create Streaming Service Endpoint
@app.post("/streamingservices/", response_model=StreamingService)
def create_streaming_service(streaming_service: StreamingServiceCreate, cursor = Depends(get_cursor)):
    cursor.execute("INSERT INTO streaming_service (name) VALUES (%s) RETURNING service_id", (streaming_service.name,))
    service_id = cursor.fetchone()[0]
    return {"service_id": service_id, **streaming_service.model_dump()}

# Get Streaming Services Endpoint
@app.get("/streamingservices/", response_model=List[StreamingService])
def read_streaming_services(skip: int = 0, cursor = Depends(get_cursor)):
    cursor.execute("SELECT service_id, name FROM streaming_service ORDER BY service_id OFFSET %s", (skip,))
    streaming_services = cursor.fetchall()
    return [{"service_id": service_id, "name": name} for service_id, name in streaming_services]

# Delete Multiple Streaming Services Endpoint
@app.delete("/streamingservices/", response_model=List[str])
def delete_streaming_services(streaming_services_to_delete: StreamingServicesToDelete, cursor = Depends(get_cursor)):
    cursor.execute("DELETE FROM streaming_service WHERE service_id = ANY(%s::UUID[]) RETURNING service_id", (streaming_services_to_delete.service_ids,))
    deleted = cursor.fetchall()
    if not deleted:
        raise HTTPException(status_code=404, detail="StreamingServices not found")
    return [service_id[0] for service_id in deleted]


# Function to check if a combination covers all services at least once
def covers_all_titles(title_services, combo):
    covered_titles = set()
    for title_id, details in title_services.items():
        title_services_set = set(service[0] for service in details["services"])
        if title_services_set.intersection(combo):
            covered_titles.add(title_id)
    return len(covered_titles) == len(title_services)

# Get Suggested Streaming Services Endpoint
@app.get("/streamingservices/suggest/{watchlist_id}")
def suggest_streaming_services(watchlist_id: str, cursor = Depends(get_cursor)):
    cursor.execute('''
select s.title_id, t.title_name, ss.service_id, ss.name
	from streaming_service ss 
	join streams s on ss.service_id = s.service_id 
	join title t on t.title_id = s.title_id
	join watchlist_item wi on s.title_id = wi.title_id
	where wi.watchlist_id = %s
	
                   ''', (watchlist_id,))
    pairings = cursor.fetchall()
    title_stream_pairs = [{"title_id": title_id, "title_name": title_name, "service_id": service_id, "service_name": service_name} for title_id, title_name, service_id, service_name in pairings]
    title_id_dict = {pair['title_id']: {'title_name': pair['title_name'], 'services': []} for pair in title_stream_pairs}
    for pair in title_stream_pairs:
        title_id_dict[pair['title_id']]['services'].append((pair['service_name'], pair['service_id']))

    # Extract all unique services
    all_services = set()
    for details in title_id_dict.values():
        for service_name, _ in details["services"]:
            all_services.add(service_name)

    # Generate all combinations of services
    all_combinations = []
    for r in range(1, len(all_services) + 1):
        for combo in combinations(all_services, r):
            if covers_all_titles(title_id_dict, combo):
                all_combinations.append(set(combo))

    sorted_combinations = sorted(all_combinations, key=len)
    return sorted_combinations

###################################

# Get Packages for a Streaming Service Endpoint
@app.get("/packages/{service_id}", response_model=List[Package])
def read_packages(service_id: str, cursor = Depends(get_cursor)):
    cursor.execute("""
        SELECT p.package_id, p.service_id, p.name, p.price, p.period, p.ad_supported, p.deprecated
        FROM package p
        JOIN streaming_service ss ON p.service_id = ss.service_id
        WHERE ss.service_id = %s
    """, (service_id,))
    packages = cursor.fetchall()
    return [
        {"package_id": package_id, "service_id": service_id, "name": name, "price": price, "period": period, "ad_supported": ad_supported, "deprecated": deprecated}
        for package_id, service_id, name, price, period, ad_supported, deprecated in packages
    ]

# Add Package Endpoint
@app.post("/packages/", response_model=Package)
def create_package(new_package: PackageCreate, cursor = Depends(get_cursor)):    
    cursor.execute("""
        INSERT INTO package (service_id, name, price, period, ad_supported, deprecated) 
        VALUES (%s, %s, %s, %s, %s, %s) 
        RETURNING package_id
    """, (new_package.service_id, new_package.name, new_package.price, new_package.period, new_package.ad_supported, new_package.deprecated))
    package_id = cursor.fetchone()[0]
    return {"package_id": package_id, **new_package.model_dump()}

# Delete Multiple Packages Endpoint
@app.delete("/packages/", response_model=List[str])
def delete_packages(packages_to_delete: PackagesToDelete, cursor = Depends(get_cursor)):
    cursor.execute("DELETE FROM package WHERE package_id = ANY(%s::UUID[]) RETURNING package_id", (packages_to_delete.package_ids,))
    deleted = cursor.fetchall()
    if not deleted:
        raise HTTPException(status_code=404, detail="Packages not found")
    return [package_id[0] for package_id in deleted]

###################################

# Get Streaming Title Availability for a Title ID Endpoint
@app.get("/streams/title/{title_id}")
def read_streams(title_id: str, cursor = Depends(get_cursor)):
    cursor.execute("""
        SELECT ss.name, s.service_id, s.title_id, s.arrival_date, s.leaving_date, t.title_name
        FROM streams s
            JOIN title t ON s.title_id = t.title_id
            JOIN streaming_service ss ON s.service_id = ss.service_id       
        WHERE s.title_id = %s
    """, (title_id,))
    streaming_titles = cursor.fetchall()
    return [
        {"service_name": s_name, "service_id": s_id, "title_id": t_id, "arrival_date": arr_date, "leaving_date": leave_date, "title_name": title_name}
        for s_name, s_id, t_id, arr_date, leave_date, title_name in streaming_titles
    ]

# Get Streaming Titles for a Service Endpoint
@app.get("/streams/{service_id}", response_model=List[StreamingTitle])
def read_streams(service_id: str, cursor = Depends(get_cursor)):
    cursor.execute("""
        SELECT s.service_id, s.title_id, s.arrival_date, s.leaving_date
        FROM streams s
        WHERE s.service_id = %s
    """, (service_id,))
    streaming_titles = cursor.fetchall()
    return [
        {"service_id": s_id, "title_id": t_id, "arrival_date": arr_date, "leaving_date": leave_date}
        for s_id, t_id, arr_date, leave_date in streaming_titles
    ]

# Add Streaming Title Endpoint
@app.post("/streams/", response_model=StreamingTitle)
def create_streaming_title(streaming_title: StreamingTitle, cursor = Depends(get_cursor)):
    cursor.execute("""
        INSERT INTO streams (service_id, title_id, arrival_date, leaving_date) 
        VALUES (%s, %s, %s, %s) 
        RETURNING title_id
    """, (streaming_title.service_id, streaming_title.title_id, streaming_title.arrival_date, streaming_title.leaving_date))
    title_id = cursor.fetchone()[0]
    return {**streaming_title.model_dump()}

# Delete Multiple Streaming Titles Endpoint
@app.delete("/streams/", response_model=List[StreamingTitle])
def delete_watchlist_items(items_to_delete: List[StreamingTitle], cursor = Depends(get_cursor)):
    deleted = []
    for deleting_stream in items_to_delete:
        cursor.execute("DELETE FROM streams WHERE service_id = %s AND title_id = %s RETURNING service_id, title_id", (deleting_stream.service_id, deleting_stream.title_id))
        deleted.extend(cursor.fetchall())
    if not deleted:
        raise HTTPException(status_code=404, detail="Watchlist items not found")
    return [{'service_id':del_stream[0], 'title_id':del_stream[1]} for del_stream in deleted]

###################################

# Create Consumer Endpoint
@app.post("/consumers/", response_model=Consumer)
def create_consumer(consumer: ConsumerCreate, cursor = Depends(get_cursor)):
    cursor.execute("INSERT INTO consumer (name, address, budget) VALUES (%s, %s, %s) RETURNING consumer_id", (consumer.name, consumer.address, consumer.budget))
    consumer_id = cursor.fetchone()[0]
    return {"consumer_id": consumer_id, **consumer.model_dump()}

# Get Consumers Endpoint
@app.get("/consumers/", response_model=List[Consumer])
def read_consumers(skip: int = 0, cursor = Depends(get_cursor)):
    cursor.execute("SELECT consumer_id, name, address, budget FROM consumer ORDER BY consumer_id OFFSET %s", (skip,))
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

# Get Subscriptions for a Consumer Endpoint
@app.get("/subscriptions/{consumer_id}", response_model=List[Subscription])
def read_subscriptions(consumer_id: str, cursor = Depends(get_cursor)):
    cursor.execute("""
        SELECT s.consumer_id, s.package_id, s.renewal_date
        FROM subscribes s
        WHERE s.consumer_id = %s
    """, (consumer_id,))
    subscriptions = cursor.fetchall()
    return [
        {"consumer_id": s_id, "package_id": t_id, "renewal_date": arr_date}
        for s_id, t_id, arr_date in subscriptions
    ]

# Add Subscription Endpoint
@app.post("/subscriptions/", response_model=Subscription)
def create_subscription(subscription: Subscription, cursor = Depends(get_cursor)):
    cursor.execute("""
        INSERT INTO subscribes (consumer_id, package_id, renewal_date) 
        VALUES (%s, %s, %s)
        RETURNING package_id
    """, (subscription.consumer_id, subscription.package_id, subscription.renewal_date))
    package_id = cursor.fetchone()[0]
    return {**subscription.model_dump()}

# Delete Multiple Subscriptions Endpoint
@app.delete("/subscriptions/", response_model=List[Subscription])
def delete_subscriptions(items_to_delete: List[Subscription], cursor = Depends(get_cursor)):
    deleted = []
    for deleting_stream in items_to_delete:
        cursor.execute("DELETE FROM subscribes WHERE consumer_id = %s AND package_id = %s RETURNING consumer_id, package_id", (deleting_stream.consumer_id, deleting_stream.package_id))
        deleted.extend(cursor.fetchall())
    if not deleted:
        raise HTTPException(status_code=404, detail="Subscriptions not found")
    return [{'consumer_id':del_subscription[0], 'package_id':del_subscription[1]} for del_subscription in deleted]

###################################

# Get Watchlist ID for a Consumer Endpoint
@app.get("/watchlists/id/{consumer_id}", response_model=Watchlist)
def read_watchlist(consumer_id: str, cursor = Depends(get_cursor)):
    cursor.execute("""
        SELECT w.watchlist_id
        FROM watchlist w
        WHERE w.consumer_id = %s
    """, (consumer_id,))
    watchlist_id = cursor.fetchone()[0]
    return {"watchlist_id": watchlist_id, "consumer_id": consumer_id}

# Get Watchlist Items for a Consumer Endpoint
@app.get("/watchlists/{consumer_id}", response_model=List[WatchlistItem])
def read_watchlist(consumer_id: str, cursor = Depends(get_cursor)):
    cursor.execute("""
        SELECT wi.watchlist_item_id, wi.watchlist_id, wi.title_id
        FROM watchlist_item wi
        JOIN watchlist w ON wi.watchlist_id = w.watchlist_id
        WHERE w.consumer_id = %s
    """, (consumer_id,))
    watchlist_items = cursor.fetchall()
    return [
        {"watchlist_item_id": wi_id, "watchlist_id": w_id, "title_id": title_id}
        for wi_id, w_id, title_id in watchlist_items
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
        INSERT INTO watchlist_item (watchlist_id, title_id) 
        VALUES (%s, %s) 
        RETURNING watchlist_item_id
    """, (watchlist_id, item.title_id))
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

###################################

# Get Titles Endpoint
@app.get("/titles/", response_model=List[Title])
def read_titles(skip: int = 0, cursor = Depends(get_cursor)):
    cursor.execute("SELECT title_id, title_name, type, rating, release_date, category, creator FROM title OFFSET %s", (skip,))
    titles = cursor.fetchall()
    return [{"title_id": title_id, "title_name": title_name, "type": type, "rating": rating, "release_date": release_date, "category": category, "creator": creator} for title_id, title_name, type, rating, release_date, category, creator in titles]

# Create Title Endpoint
@app.post("/titles/", response_model=TitleCreate)
def create_title(title: TitleCreate, cursor = Depends(get_cursor)):
    cursor.execute("INSERT INTO title (title_name, type, rating, release_date, category, creator) VALUES (%s, %s, %s, %s, %s, %s) RETURNING title_id", (title.title_name, title.type, title.rating, title.release_date, title.category, title.creator))
    title_id = cursor.fetchone()[0]
    return {"title_id": title_id, **title.model_dump()}

# Get Title Details
@app.get("/titles/{title_id}", response_model=Title)
def get_title_details(title_id: str, cursor = Depends(get_cursor)):
    cursor.execute("""
        SELECT *
        FROM title
        WHERE title_id = %s
    """, (title_id,))
    title = cursor.fetchone()[0]
    return {"title_id": title_id, **title.model_dump()}

# Delete Multiple Titles Endpoint
@app.delete("/titles/", response_model=List[str])
def delete_titles(titles_to_delete: TitlesToDelete, cursor = Depends(get_cursor)):
    cursor.execute("DELETE FROM title WHERE title_id = ANY(%s::UUID[]) RETURNING title_id", (titles_to_delete.title_ids,))
    deleted = cursor.fetchall()
    if not deleted:
        raise HTTPException(status_code=404, detail="Titles not found")
    return [title_id[0] for title_id in deleted]


####################################


# Serve HTML Icon
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("web/favicon.ico")

# Serve HTML Home Page
@app.get("/", response_class=HTMLResponse)
def get_home_page():
    with open("web/index.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Serve HTML Streaming Service Page
@app.get("/streamingservice", response_class=HTMLResponse)
def get_streaming_service_management():
    with open("web/streaming_service.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Serve HTML Package Page
@app.get("/package", response_class=HTMLResponse)
def get_package_management():
    with open("web/package.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Serve HTML Package Page
@app.get("/stream", response_class=HTMLResponse)
def get_stream_management():
    with open("web/stream.html", "r") as file:
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
def get_watchlist_management():
    with open("web/watchlist.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Serve HTML Subscriptions Page
@app.get("/subscribe", response_class=HTMLResponse)
def get_watchlist_management():
    with open("web/subscribe.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Serve HTML Title Page
@app.get("/title", response_class=HTMLResponse)
def get_title_management():
    with open("web/title.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
