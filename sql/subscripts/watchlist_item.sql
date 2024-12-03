\echo -- Creating table: watchlist_item
CREATE TABLE watchlist_item (
  watchlist_item_id varchar(32) primary key,
  watchlist_id varchar(32) references watchlist(watchlist_id),
  title_id varchar(32) references title(title_id),
  priority int
);