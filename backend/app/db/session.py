import os

from sqlalchemy import URL, create_engine


def database_url() -> URL:
    return URL.create(
        "mysql+pymysql",
        username=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
        port=int(os.environ.get("MYSQL_PORT", "3307")),
        database=os.environ["MYSQL_DATABASE"],
        query={"charset": "utf8mb4"},
    )


def make_engine():
    return create_engine(database_url(), pool_pre_ping=True)
