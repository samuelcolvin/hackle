from aiohttp.web_exceptions import HTTPFound
from aiohttp_jinja2 import template
from .models import sa_user


@template('index.jinja')
async def index(request):
    return {}


async def add_user(request):
    data = await request.post()
    email = data['email']
    engine = request.app['engine']
    async with engine.acquire() as conn:
        v = await conn.execute(sa_user.insert().returning(sa_user.c.id).values({'email': email}))
        id = (await v.first()).id
        print('created user, id: {}, email: {}'.format(id, email))
    return HTTPFound('/')
