\echo -- Creating table: consumer
CREATE TABLE consumer (
  consumer_id UUID default gen_random_uuid() primary key,
  name text NOT NULL,
  address text,
  budget decimal(6, 0)
);