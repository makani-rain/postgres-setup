\echo -- Creating table: title
CREATE TABLE title (
  title_id UUID default gen_random_uuid() primary key,
  title_name varchar(128) NOT NULL,
  type varchar(32),
  rating varchar(32),
  release_date varchar(32),
  category varchar(128),
  director varchar(128),
  language varchar(64),
  CONSTRAINT unique_title_release UNIQUE(title_name, type, rating, director, release_date, language)
);