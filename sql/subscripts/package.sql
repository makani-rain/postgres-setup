\echo -- Creating table: package
CREATE TABLE package (
  package_id UUID default gen_random_uuid() primary key,
  service_id UUID references streaming_service(service_id) ON DELETE CASCADE,
  name text,
  price decimal(6, 2),
  period int default 1,
  ad_supported boolean default false,
  deprecated boolean default false
);