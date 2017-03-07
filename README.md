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

### Production setup

Set the following environment variables accordingly:
* `MYSQL_USER`
* `MYSQL_PASS`
* `MYSQL_HOST`
* `MYSQL_PORT`

## Run the app

```
python run.py
```