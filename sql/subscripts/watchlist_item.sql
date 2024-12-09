\echo -- Creating table: watchlist_item
CREATE TABLE watchlist_item (
  watchlist_item_id UUID default gen_random_uuid() primary key,
  watchlist_id UUID references watchlist(watchlist_id) ON DELETE CASCADE,
  title_id UUID references title(title_id) ON DELETE CASCADE
);