\echo -- Creating table: package
CREATE TABLE package (
  package_id varchar(32) primary key,
  service_id varchar(32) references streaming_service(service_id),
  price decimal(6, 2),
  period text,
  ad_supported boolean,
  deprecated boolean
);