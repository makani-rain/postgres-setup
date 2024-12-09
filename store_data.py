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


netflix_packages = [
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

hulu_packages = [
    {
        'name': 'Hulu w/ads',
        'price': 9.99,
        'period': 1,
        'ad_supported': True
    },
    {
        'name': 'Hulu',
        'price': 18.99,
        'period': 1,
        'ad_supported': False
    }
]

disney_packages = [
    {
        'name': 'Disney+ Basic',
        'price': 7.99,
        'period': 1,
        'ad_supported': True
    },
    {
        'name': 'Disney+ Premium',
        'price': 13.99,
        'period': 1,
        'ad_supported': False
    }
]

apple_packages = [
    {
        'name': 'Apple TV+',
        'price': 9.99,
        'period': 1,
        'ad_supported': False
    }
]

prime_packages = [
    {
        'name': 'Prime Video w/Amazon Prime Membership',
        'price': 14.99,
        'period': 1,
        'ad_supported': True
    },
    {
        'name': 'Prime Video',
        'price': 8.99,
        'period': 1,
        'ad_supported': True
    },
    {
        'name': 'Prime Video w/Amazon Prime Membership ad-free',
        'price': 17.99,
        'period': 1,
        'ad_supported': False
    },
    {
        'name': 'Prime Video ad-free',
        'price': 11.99,
        'period': 1,
        'ad_supported': False
    }
]

peacock_packages = [
    {
        'name': 'Premium',
        'price': 7.99,
        'period': 1,
        'ad_supported': True
    },
    {
        'name': 'Premium',
        'price': 79.99,
        'period': 12,
        'ad_supported': True
    },
    {
        'name': 'Premium Plus',
        'price': 13.99,
        'period': 1,
        'ad_supported': False
    },
    {
        'name': 'Premium Plus',
        'price': 139.99,
        'period': 12,
        'ad_supported': False
    }
]

paramount_packages = [
    {
        'name': 'Paramount+ Essential',
        'price': 7.99,
        'period': 1,
        'ad_supported': True
    },
    {
        'name': 'Paramount+ Essential',
        'price': 59.99,
        'period': 12,
        'ad_supported': True
    },
    {
        'name': 'Paramount+ with SHOWTIME',
        'price': 12.99,
        'period': 1,
        'ad_supported': False
    },
    {
        'name': 'Paramount+ with SHOWTIME',
        'price': 119.99,
        'period': 12,
        'ad_supported': False
    }
]

max_packages = [
    {
        'name': 'With Ads',
        'price': 9.99,
        'period': 1,
        'ad_supported': True
    },
    {
        'name': 'With Ads',
        'price': 99.99,
        'period': 12,
        'ad_supported': True
    },
    {
        'name': 'Ad-Free',
        'price': 16.99,
        'period': 1,
        'ad_supported': False
    },
    {
        'name': 'Ad-Free',
        'price': 169.99,
        'period': 12,
        'ad_supported': False
    },
    {
        'name': 'Ultimate Ad-Free',
        'price': 20.99,
        'period': 1,
        'ad_supported': False
    },
    {
        'name': 'Ultimate Ad-Free',
        'price': 209.99,
        'period': 12,
        'ad_supported': False
    }
]


all_packages = {
    "Netflix": {
        "packages": netflix_packages,
        "inserted": False
    },
    "Hulu": {
        "packages": hulu_packages,
        "inserted": False
    },
    "Disney+": {
        "packages": disney_packages,
        "inserted": False
    },
    "Apple TV": {
        "packages": apple_packages,
        "inserted": False
    },
    "Prime Video": {
        "packages": prime_packages,
        "inserted": False
    },
    "Peacock": {
        "packages": peacock_packages,
        "inserted": False
    },
    "Paramount+": {
        "packages": paramount_packages,
        "inserted": False
    },
    "Max": {
        "packages": max_packages,
        "inserted": False
    }
}


def clean_str(in_str) -> str:
    if in_str is None:
        return None
    return in_str.strip().replace("'", "''")

def store_data_in_db(data):
    cursor = conn.cursor()
    title_ids = []
    for title_details in data:
        title = clean_str(title_details['title'])
        type = clean_str(title_details['showType'])
        # rating = clean_str(title_details['rating'])
        titlereleased = clean_str(str(title_details['releaseYear']) if 'releaseYear' in title_details else f"{title_details['firstAirYear']}-{title_details['lastAirYear']}")
        category = clean_str(', '.join([x['id'] for x in title_details['genres']]))
        creator = clean_str(', '.join(title_details['creators'])) if 'creators' in title_details else (', '.join(title_details['directors']) if 'directors' in title_details else '')
        # language = clean_str(title_details['language'])

        cursor.execute('''
INSERT INTO title (title_name, type, release_date, category, creator) 
    VALUES (%s, %s, %s, %s, %s) RETURNING title_id
''', (title, type, titlereleased, category, creator))
        title_id = cursor.fetchone()[0]
        
        services_streaming_title = []
        streaming_opts = title_details['streamingOptions']['us'] if 'us' in title_details['streamingOptions'] else []
        if len(streaming_opts) > 1:
            options = []
            for opt in streaming_opts:
                if opt['type'] == 'subscription' or opt['type'] == 'addon':
                    options.append(opt['service']['name'])
            if len(options) > 1:
                print(f'title ({title}) can be streamed by: {options}')

        for streaming_opt in streaming_opts:
            if streaming_opt['type'] == 'subscription' or opt['type'] == 'addon':
                opt_service_name = streaming_opt['service']['name']
                opt_arrival_date = streaming_opt['availableSince']
                opt_leave_date = None
                if streaming_opt['expiresSoon'] == 'true':
                    opt_leave_date = streaming_opt['expiresOn']
                services_streaming_title.append((opt_service_name, opt_arrival_date, opt_leave_date))
        title_ids.append((title_id, services_streaming_title))
    
    # print(f'Obtained {len(title_ids)} title IDs')

    for title_id in title_ids:
        if title_id[1] != []:
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

                # print(f'Stored {svc_name} into DB ({service_id})')

                cursor.execute('''
INSERT INTO streams (service_id, title_id, arrival_date, leaving_date) 
    VALUES (%s, %s, %s, %s) ON CONFLICT (service_id, title_id) DO NOTHING
    RETURNING title_id
        ''', (service_id, title_id[0], svc[1], svc[2]))

                # print('Stored (service_id, title_id) into streams')

                store_packages(svc_name, service_id, cursor)

    conn.commit()
    cursor.close()

def store_packages(service_name, service_id, cursor):

    if service_name in all_packages and all_packages[service_name]['inserted'] == False:

        package_ids = []
        for package in all_packages[service_name]['packages']:
            cursor.execute('''
    INSERT INTO package (service_id, name, price, period, ad_supported) 
        VALUES (%s, %s, %s, %s, %s) RETURNING package_id
    ''', (service_id, package['name'], package['price'], package['period'], package['ad_supported']))
            
            package_ids.append(cursor.fetchone()[0])

        # print(f'Obtained {len(package_ids)} package IDs for {service_name}')
        all_packages[service_name]['inserted'] = True

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

        store_data_in_db(data)
    
    # manually store the large file
    with open(f'datascrapes/datanetflix.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    store_data_in_db(data)
    
    # manually store the large file
    with open(f'datascrapes/datadisney.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    store_data_in_db(data)
    
    # manually store the large file
    with open(f'datascrapes/dataparamount.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    store_data_in_db(data)
