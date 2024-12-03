\echo -- Creating table: subscribes
CREATE TABLE subscribes (
  consumer_id varchar(32),
  package_id varchar(32),
  renewal_date date,
  primary key (consumer_id, package_id)
);