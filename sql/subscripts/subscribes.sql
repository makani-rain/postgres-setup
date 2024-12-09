\echo -- Creating table: subscribes
CREATE TABLE subscribes (
  consumer_id UUID references consumer(consumer_id) ON DELETE CASCADE,
  package_id UUID references package(package_id) ON DELETE CASCADE,
  renewal_date date,
  primary key (consumer_id, package_id)
);