\echo -- Creating table: package
CREATE TABLE package (
  package_id UUID default gen_random_uuid() primary key,
  service_id UUID references streaming_service(service_id),
  price decimal(6, 2),
  period text,
  ad_supported boolean,
  deprecated boolean
);