# DropMuse

## Install / Setup
1. Clone repo:

    ```
    git clone https://github.com/DropMuse/DropMuse
    cd DropMuse
    ```

2. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

3. Copy `.env` template:

    ```
    cp .env.template .env
    ```

4. Add your local DB credentials to your `.env`.
5. Create the SQL tables from `tables.sql` in your database.

### Production setup

Set the following environment variables accordingly:
* `DB_USER`
* `DB_PASS`
* `DB_HOST`
* `DB_PORT`
* `DB_DBNAME`
* `DB_PREFIX`

Alternatively, you can set `DATABASE_URL` to specify the full URL. (Used for Heroku)

## Run the app

```
python run.py
```
