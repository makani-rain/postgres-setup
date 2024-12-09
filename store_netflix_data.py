import json
import psycopg2

# Database Configuration
DATABASE_URL = "dbname=postgres user=postgres password=admin host=localhost"
conn = psycopg2.connect(DATABASE_URL)

def clean_str(in_str) -> str:
    if in_str is None:
        return None
    return in_str.strip().replace("'", "''")

def write_data_to_file(data):
    with open('canned_netflix_titles.sql', 'w', encoding='utf-8') as file:
        file.write('\echo Populating Netflix data\n')
        file.write('INSERT INTO title (title_name, type, rating, release_date, category, creator, language)\n\tVALUES')
        for index, title_details in enumerate(data):
            title = clean_str(title_details['title'])
            type = clean_str(title_details['type'])
            rating = clean_str(title_details['rating'])
            titlereleased = clean_str(title_details['titlereleased'])
            category = clean_str(title_details['category'])
            creator = clean_str(title_details['director'])
            language = clean_str(title_details['language'])
            line = f"\t\t('{title}', '{type}', '{rating}', '{titlereleased}', '{category}', '{creator}', '{language}'){',' if index < (len(data) - 1) else ''}\n"
            file.write(line)
        if index == (len(data) - 1):
            file.write(';')

    print("Dictionary contents have been written to the file.")

def store_data_in_db(data):
    cursor = conn.cursor()
    title_ids = []
    for title_details in data:
        title = clean_str(title_details['title'])
        type = clean_str(title_details['type'])
        rating = clean_str(title_details['rating'])
        titlereleased = clean_str(title_details['titlereleased'])
        category = clean_str(title_details['category'])
        creator = clean_str(title_details['director'])
        language = clean_str(title_details['language'])

        cursor.execute('''
INSERT INTO title (title_name, type, rating, release_date, category, creator, language) 
    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING title_id
''', (title, type, rating, titlereleased, category, creator, language))
        title_ids.append(cursor.fetchone()[0])
    
    print(f'Obtained {len(title_ids)} title IDs')

    service_name = 'netflix'
    cursor.execute('''
INSERT INTO streaming_service (name) 
    VALUES (%s) RETURNING service_id
''', (service_name,))
    service_id = cursor.fetchone()[0]

    print(f'Stored {service_name} into DB ({service_id})')

    for title_id in title_ids:
        cursor.execute('''
INSERT INTO streams (service_id, title_id) 
    VALUES (%s, %s) RETURNING title_id
''', (service_id, title_id))

    print('Stored (service_id, title_id) into streams')

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
    # Open and read the JSON file
    with open('datascrapes/netflix.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # write_data_to_file(data)
    store_data_in_db(data)
    # test_db(data)
