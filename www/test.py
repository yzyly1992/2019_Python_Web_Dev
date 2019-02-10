import orm
import asyncio
from models import User, Blog, Comment

async def test(loop):
    await orm.create_pool(loop=loop, user='root', password='Lilidai00', db='awesome')
    u = Blog(user_id='0015472266357569e74005330744ceca1d1f6fdd6b034a4000', user_name='test@qq.com', user_image='about:blank',name='Test', summary='Test', content='1234567890')
    await u.save()
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test(loop))
    loop.close()