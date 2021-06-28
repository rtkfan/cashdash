SELECT t.guid AS txn_guid,
       t.post_date,
       t.description,
       s.account_guid AS expense_account_guid,
       a_s.account_type AS expense_type,
       s.guid AS expense_split_guid,
       a_s.name AS expense_category,
       c.guid AS contra_guid,
       a_c.account_type AS contra_account_type,
       a_c.name AS contra_account_name,
       s.value_num AS amount_cents,
       COUNT(c.guid) OVER (PARTITION BY t.guid) AS num_entries
FROM splits s
  INNER JOIN accounts a_s ON s.account_guid = a_s.guid
  INNER JOIN splits c ON s.tx_guid = c.tx_guid AND
                         s.account_guid <> c.account_guid
  INNER JOIN accounts a_c ON c.account_guid = a_c.guid
  INNER JOIN transactions t ON s.tx_guid = t.guid
WHERE a_s.account_type IN ('INCOME','EXPENSE')
  AND a_c.account_type IN ('BANK','CREDIT')
  AND a_s.name <> 'Mortgage (Temp)'
ORDER BY expense_category, enter_date, txn_guid;
