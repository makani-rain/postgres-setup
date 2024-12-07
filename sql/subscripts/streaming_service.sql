\echo -- Creating table: streaming_service
CREATE TABLE streaming_service (
  service_id UUID default gen_random_uuid() primary key,
  name text UNIQUE NOT NULL
);