-- on tenant
CREATE USER TECH_MONI PASSWORD "UltraComplexPassword2020!";             -- Technical user for Python program
ALTER USER TECH_MONI DISABLE PASSWORD LIFETIME;
GRANT MONITORING to TECH_MONI;
GRANT ABAP_READ to TECH_MONI;
-- Enable monitoring for sql request
-- Enabling  Expensive Statements trace in HANA
alter system alter configuration ('global.ini', 'system') set ('expensive_statement', 'use_in_memory_tracing') = 'false' with reconfigure;
alter system alter configuration ('global.ini', 'system') set ('expensive_statement', 'threshold_duration') = '1000000' with reconfigure;
alter system alter configuration ('global.ini', 'system') set ('expensive_statement', 'enable') = 'true' with reconfigure;
-- Limiting expensive statements
alter system alter configuration ('global.ini', 'SYSTEM') set ('resource_tracking', 'enable_tracking') = 'on' with reconfigure;
alter system alter configuration ('global.ini', 'SYSTEM') set ('resource_tracking', 'memory_tracking') = 'on' with reconfigure;
