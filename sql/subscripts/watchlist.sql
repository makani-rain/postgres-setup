\echo -- Creating table: watchlist
CREATE TABLE watchlist (
  watchlist_id UUID default gen_random_uuid() primary key,
  consumer_id UUID references consumer(consumer_id) ON DELETE CASCADE
);