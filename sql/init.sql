\echo === Creating tables ===
\i /docker-entrypoint-initdb.d/subscripts/consumer.sql;
\i /docker-entrypoint-initdb.d/subscripts/watchlist.sql;
\i /docker-entrypoint-initdb.d/subscripts/title.sql;
\i /docker-entrypoint-initdb.d/subscripts/watchlist_item.sql;
\i /docker-entrypoint-initdb.d/subscripts/streaming_service.sql;
\i /docker-entrypoint-initdb.d/subscripts/streams.sql;
\i /docker-entrypoint-initdb.d/subscripts/package.sql;
\i /docker-entrypoint-initdb.d/subscripts/subscribes.sql;
\echo === Populating tables ===
\i /docker-entrypoint-initdb.d/subscripts/canned/consumer_canned.sql;