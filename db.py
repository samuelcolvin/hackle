import sys

import psycopg2
from sqlalchemy import create_engine

from hackle.main import Settings
from hackle.models import Base


def prepare_database(reset: bool=False):
    settings = Settings()
    conn = psycopg2.connect(
        password=settings.PG_PASSWORD,
        host=settings.PG_HOST,
        port=settings.PG_PORT,
        user=settings.PG_USER,
    )
    conn.autocommit = True
    cur = conn.cursor()
    if not reset:
        args = settings.PG_DATABASE,
        cur.execute('SELECT EXISTS (SELECT datname FROM pg_catalog.pg_database WHERE datname=%s)', args)
        if cur.fetchone()[0]:
            print('database already exists, not creating')
            return
    cur.execute('DROP DATABASE IF EXISTS {}'.format(settings.PG_DATABASE))
    cur.execute('CREATE DATABASE {}'.format(settings.PG_DATABASE))
    cur.close()
    conn.close()

    engine = create_engine(settings.get_dsn())
    Base.metadata.create_all(engine)
    engine.dispose()
    print('database and tables created')

if __name__ == '__main__':
    prepare_database('--reset' in sys.argv)
