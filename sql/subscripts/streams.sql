\echo -- Creating table: streams
CREATE TABLE streams (
  service_id UUID,
  title_id UUID,
  arrival_date bigint,
  leaving_date bigint,
  primary key (service_id, title_id)
);