-- recurses nested account relationship to get a colon-delimited account
-- 'location' for each account.

WITH RECURSIVE acc_tree(acc_guid, full_tree, reverse_tree) AS (
SELECT guid AS acc_guid,
       name AS full_tree,
     name AS reverse_tree
FROM accounts
WHERE parent_guid = '1d97d1b7e3714be094ee63c6797fb445' -- root account guid

UNION
SELECT accounts.guid AS acc_guid,
       acc_tree.full_tree||':'||accounts.name AS full_tree,
     accounts.name||':'||acc_tree.reverse_tree AS reverse_tree
FROM accounts
  INNER JOIN acc_tree ON accounts.parent_guid = acc_tree.acc_guid
)
SELECT a.guid,
       a.name,
     a.account_type,
     a.placeholder,
     p.name AS parent_name,
       acc_tree.full_tree,
     acc_tree.reverse_tree,
     LENGTH(full_tree)-LENGTH(REPLACE(full_tree,':','')) AS account_depth
FROM accounts a
  INNER JOIN acc_tree ON a.guid = acc_tree.acc_guid
  LEFT JOIN accounts p ON a.parent_guid = p.guid;
