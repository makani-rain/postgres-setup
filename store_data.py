import json
import psycopg2

# Database Configuration
DATABASE_URL = "dbname=postgres user=postgres password=admin host=localhost"
conn = psycopg2.connect(DATABASE_URL)

services = ['netflix',
            'prime',
            'disney',
            'apple',
            'hbo']

def clean_str(in_str) -> str:
    if in_str is None:
        return None
    return in_str.strip().replace("'", "''")

def store_data_in_db(service_name, data):
    cursor = conn.cursor()
    title_ids = []
    for title_details in data:
        title = clean_str(title_details['title'])
        type = clean_str(title_details['showType'])
        # rating = clean_str(title_details['rating'])
        titlereleased = clean_str(str(title_details['releaseYear']) if 'releaseYear' in title_details else f"{title_details['firstAirYear']}-{title_details['lastAirYear']}")
        category = clean_str(', '.join([x['id'] for x in title_details['genres']]))
        director = clean_str(', '.join(title_details['creators'])) if 'creators' in title_details else ''
        # language = clean_str(title_details['language'])

        cursor.execute('''
INSERT INTO title (title_name, type, release_date, category, director) 
    VALUES (%s, %s, %s, %s, %s) RETURNING title_id
''', (title, type, titlereleased, category, director))
        title_id = cursor.fetchone()[0]
        
        services_streaming_title = []
        streaming_opts = title_details['streamingOptions']['us']
        for streaming_opt in streaming_opts:
            if streaming_opt['type'] == 'subscription':
                opt_service_name = streaming_opt['service']['id']
                opt_arrival_date = streaming_opt['availableSince']
                opt_leave_date = None
                if streaming_opt['expiresSoon'] == 'true':
                    opt_leave_date = streaming_opt['expiresOn']
                services_streaming_title.append((opt_service_name, opt_arrival_date, opt_leave_date))
        title_ids.append((title_id, services_streaming_title))
    
    print(f'Obtained {len(title_ids)} title IDs')

    for title_id in title_ids:
        if title_id[1] != []:
            print(f'title_id={title_id}')
            for svc in title_id[1]:
                svc_name = svc[0]
                cursor.execute('''
INSERT INTO streaming_service (name)
    VALUES (%s)
    ON CONFLICT (name) DO UPDATE
    SET name = EXCLUDED.name
    RETURNING service_id
        ''', (svc_name,))
                service_id = cursor.fetchone()[0]

                print(f'Stored {svc_name} into DB ({service_id})')

                cursor.execute('''
INSERT INTO streams (service_id, title_id, arrival_date, leaving_date) 
    VALUES (%s, %s, %s, %s) ON CONFLICT (service_id, title_id) DO NOTHING
    RETURNING title_id
        ''', (service_id, title_id[0], svc[1], svc[2]))

                print('Stored (service_id, title_id) into streams')

    conn.commit()
    cursor.close()

def update_packages():
    packages = [
        {
            'name': 'Standard w/ads',
            'price': 6.99,
            'period': 1,
            'ad_supported': True
        },
        {
            'name': 'Standard',
            'price': 15.49,
            'period': 1,
            'ad_supported': False
        },
        {
            'name': 'Premium',
            'price': 22.99,
            'period': 1,
            'ad_supported': False
        }
    ]

    package_ids = []
    for package in packages:
        cursor.execute('''
INSERT INTO package (service_id, name, price, period, ad_supported) 
    VALUES (%s, %s, %s, %s, %s) RETURNING package_id
''', (service_id, package['name'], package['price'], package['period'], package['ad_supported']))
        
        package_ids.append(cursor.fetchone()[0])

    print(f'Obtained {len(package_ids)} package IDs')


    conn.commit()
    cursor.close()

def clear_tables():
    
    cursor = conn.cursor()
    cursor.execute('DELETE FROM package')
    cursor.execute('DELETE FROM streams')
    cursor.execute('DELETE FROM title')
    cursor.execute('DELETE FROM streaming_service')
   
    conn.commit()
    cursor.close()

def test_db(data):
    for _ in range(1000):
        store_data_in_db(data)
        clear_tables()

if __name__=='__main__':
    for service in services:

        with open(f'datascrapes/top{service}.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        store_data_in_db(service, data)
