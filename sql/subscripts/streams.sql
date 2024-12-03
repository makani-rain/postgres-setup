\echo -- Creating table: streams
CREATE TABLE streams (
  service_id varchar(32),
  title_id varchar(32),
  arrival_date date,
  leaving_date date,
  primary key (service_id, title_id)
);