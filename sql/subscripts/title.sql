\echo -- Creating table: title
CREATE TABLE title (
  title_id UUID default gen_random_uuid() primary key,
  name varchar(64) NOT NULL,
  type varchar(32),
  rating varchar(32),
  release_date varchar(32),
  genre varchar(32),
  category varchar(32),
  director varchar(32)
);