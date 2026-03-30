## Temporary Views vs Global Temporary Views in Spark/Databricks

### Temporary Views (`CREATE OR REPLACE TEMP VIEW`)
- **Scope:** Session-scoped. Only visible to the session (notebook or job) that created it.
- **Lifetime:** Exists only for the duration of the session. Dropped automatically when the session ends.
- **Usage:** Useful for intermediate results or sharing data within a single notebook or job.
- **Syntax Example:**
  sql
  CREATE OR REPLACE TEMP VIEW my_temp_view AS
  SELECT * FROM my_table;
  

### Global Temporary Views (`CREATE OR REPLACE GLOBAL TEMP VIEW`)
- **Scope:** Global. Visible across all sessions and notebooks within the same Spark application.
- **Lifetime:** Exists until the Spark application stops.
- **Usage:** Useful for sharing data between different notebooks or jobs within the same Spark application.
- **Syntax Example:**
  sql
  CREATE OR REPLACE GLOBAL TEMP VIEW my_global_temp_view AS
  SELECT * FROM my_table;
  
- **Access:** Must be referenced with the `global_temp` database prefix:
  sql
  SELECT * FROM global_temp.my_global_temp_view;
  

### Key Differences

| Feature         | Temporary View         | Global Temporary View         |
|-----------------|-----------------------|------------------------------|
| Scope           | Session               | Application-wide             |
| Lifetime        | Session duration      | Application duration         |
| Accessibility   | Current session only  | All sessions (with prefix)   |
| Reference       | Direct name           | `global_temp.` prefix needed |