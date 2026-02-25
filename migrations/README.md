# Migrations

Run initial schema with:

```bash
psql $DATABASE_URL -f migrations/001_initial.sql
```

Or use `async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)` for dev.
