\echo -- Creating table: watchlist
CREATE TABLE watchlist (
  watchlist_id varchar(32) primary key,
  consumer_id varchar(32) references consumer(consumer_id)
);