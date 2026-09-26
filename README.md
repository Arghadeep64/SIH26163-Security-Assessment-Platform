# SIH26163: Security Assessment of the World Monitor Application

## Project Details
- **Project ID:** SIH26163
- **Title:** Security Assessment of the World Monitor Application
- **Organization:** National Technical Research Organisation (NTRO)
- **Category:** Software
- **Theme:** Smart Automation
- **Target Application:** World Monitor (https://www.worldmonitor.app)
- **Source Repository:** https://github.com/koala73/worldmonitor

## Purpose
Authorized/local security assessment platform for World Monitor.

## Technology Stack

- **Frontend:** React + Vite + TypeScript
- **Backend:** FastAPI + Python 3.12+
- **Database:** MySQL (Local Development) / TiDB (Production & Cloud Hosting)
- **ORM:** SQLAlchemy
- **Database Driver:** PyMySQL
- **Database Management:** MySQL Workbench-compatible SQL scripts are maintained under `database/mysql/` and `database/tidb/`.

## Local MySQL Setup

To set up the local MySQL database using MySQL Workbench:

1. **Install MySQL 8+**: Ensure MySQL Server 8+ is installed and running locally.
2. **Open MySQL Workbench**: Connect to your local MySQL instance.
3. **Open Schema Script**: Open `database/mysql/sih26163_schema.sql` in MySQL Workbench.
4. **Execute the Script**: Run the SQL script to create the `sih26163_db` database and its corresponding tables (`assessments`, `security_checks`, `findings`, `evidence`, `reports`).
5. **Create Local `.env` File**: Copy `.env.example` to `.env` in the project root:
   ```bash
   cp .env.example .env
   ```
6. **Configure Database Credentials**: Update `.env` with your local MySQL credentials:
   ```env
   APP_ENV=development
   BACKEND_HOST=127.0.0.1
   BACKEND_PORT=8000
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_NAME=sih26163_db
   DB_USER=root
   DB_PASSWORD=YOUR_LOCAL_MYSQL_PASSWORD
   DEFAULT_TARGET=http://localhost:3000
   ```
7. **Start Backend Service**:
   ```bash
   uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
   ```
8. **Verify Database Health**: Send a GET request to verify connectivity:
   ```http
   GET http://127.0.0.1:8000/health/database
   ```
   Expected response when connected:
   ```json
   {
       "status": "healthy",
       "database": "connected"
   }
   ```

## TiDB Deployment

TiDB Cloud is the production and cloud database platform for SIH26163.
- TiDB provides MySQL 8 wire protocol compatibility and supports horizontal scalability and distributed transactions.
- The same database schema (`database/tidb/sih26163_schema.sql`) applies directly to TiDB Cloud clusters.
- To connect the backend to TiDB Cloud, simply update the `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` environment variables in your deployment environment.

## Security Note
This project is intended only for authorized security testing and controlled/local environments. Sensitive credentials, tokens, and arbitrary secrets are strictly excluded from persistent storage and logging.
