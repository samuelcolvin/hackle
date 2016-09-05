import asyncio
from pathlib import Path

from aiopg.sa.engine import _create_engine
from aiohttp import web
import aiohttp_jinja2
from jinja2 import FileSystemLoader, contextfunction
from sqlalchemy.engine.url import URL

from .views import index, add_user

THIS_DIR = Path(__file__).parent.resolve()


class Settings:
    PG_HOST = 'localhost'
    PG_PORT = '5432'
    PG_USER = 'postgres'
    PG_PASSWORD = ''
    PG_DATABASE = 'hackle'

    def __init__(self, **custom_settings):
        """
        :param custom_settings: Custom settings to override defaults, only attributes already defined
        can be set.
        """
        for name, value in custom_settings.items():
            if not hasattr(self, name):
                raise TypeError('{} is not a valid setting name'.format(name))
            setattr(self, name, value)

    def get_dsn(self):
        return str(URL(
            password=self.PG_PASSWORD,
            host=self.PG_HOST,
            port=self.PG_PORT,
            username=self.PG_USER,
            database=self.PG_DATABASE,
            drivername='postgres',
        ))


async def close_pg_engine(app):
    engine = app.pop('engine')
    engine.close()
    await engine.wait_closed()


@contextfunction
def reverse_url(context, name, **parts):
    app = context['app']

    named_resources = app.router.named_resources()
    kwargs = {}
    if 'query' in parts:
        kwargs['query'] = parts.pop('query')
    if parts:
        kwargs['parts'] = parts
    return named_resources[name].url(**kwargs)


def create_app(loop=None, settings: Settings=None):
    loop = loop or asyncio.get_event_loop()
    settings = settings or Settings()
    app = web.Application(loop=loop)

    aiohttp_jinja2.setup(app, loader=FileSystemLoader(str(THIS_DIR / 'templates')))
    # app[JINJA_ENV].filters['url'] = reverse_url

    app['engine'] = loop.run_until_complete(_create_engine(settings.get_dsn(), loop=loop))
    app.on_cleanup.append(close_pg_engine)

    ar = app.router.add_route
    ar('GET', '/', index, name='index')
    ar('POST', '/add-user', add_user, name='add-user')
    return app

