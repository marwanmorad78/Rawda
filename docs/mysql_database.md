# Switching the project to MySQL

The project can run on MySQL or MariaDB by changing environment variables.

## 1. Create the database

Create a MySQL database using `utf8mb4`:

```sql
CREATE DATABASE al_rawda_center CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Create or choose a MySQL user that can access it.

## 2. Configure `.env`

Use:

```env
DATABASE_ENGINE=mysql
DATABASE_NAME=al_rawda_center
DATABASE_USER=root
DATABASE_PASSWORD=your_mysql_password
DATABASE_HOST=127.0.0.1
DATABASE_PORT=3306
DATABASE_CHARSET=utf8mb4
```

You can also use a URL:

```env
DATABASE_URL=mysql://root:your_mysql_password@127.0.0.1:3306/al_rawda_center
```

When `DATABASE_URL` is set, it takes priority over the separate `DATABASE_*` values.

## 3. Install dependencies

After pulling these changes, run:

```powershell
uv sync
```

## 4. Apply migrations

For a fresh MySQL database:

```powershell
uv run python src\manage.py migrate
```

## Existing data

Changing the database engine does not automatically copy existing PostgreSQL or SQLite data into MySQL. For data migration, export from the old database and import into MySQL, then run `migrate` and verify orders, products, users, and settings.
