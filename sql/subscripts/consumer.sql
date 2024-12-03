\echo -- Creating table: consumer
CREATE TABLE consumer (
  consumer_id varchar(32) primary key,
  name text NOT NULL,
  address text,
  budget decimal(6, 0)
);