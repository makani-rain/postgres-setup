-- create a table
CREATE TABLE consumer(
  consumer_id VARCHAR(32) PRIMARY KEY,
  name TEXT NOT NULL,
  address TEXT,
  budget DECIMAL(6, 0)
);

-- add test data
INSERT INTO consumer (consumer_id, name, address, budget)
  VALUES
    ('deadbeef', 'Alice', '123 Main St.', '100'),
    ('cafebabe', 'Bob', '124 Main St.', '150')
;