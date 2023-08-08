import asyncio
import aiohttp
from . import generate_token
import json

with open('Source/data.json', 'r') as json_file:
    data = json.load(json_file)

headers = {'X-API-KEY': f'{data["token"]}'}
categories = {'enhance': "https://techhk.aoscdn.com/api/tasks/visual/scale",
              'removeBG': "https://techhk.aoscdn.com/api/tasks/visual/segmentation"}


# token handler
async def token_handler():
    global headers, data
    email = generate_token.get_email()
    new_token = generate_token.get_access_key(email)
    data['token'] = new_token
    with open('Source/data.json', 'w', encoding='UTF8') as json_file:
        json.dump(data, json_file)
    headers = {'X-API-KEY': f'{data["token"]}'}


# starting task
async def task_start(photo, category, process_type):
    global headers
    url = categories[category]
    if category == 'removeBG':
        _data = {'sync': '0', 'image_file': open(
            rf'{photo}', 'rb'), 'format': process_type}
    else:
        _data = {'sync': '0', 'type': f'{process_type}',
                 'image_file': open(rf'{photo}', 'rb')}
    async with aiohttp.ClientSession() as session:
        response_post = await session.post(url=url, data=_data, headers=headers)
        _json = await response_post.json()
    if _json['status'] == 200:
        task_id = _json['data']['task_id']
        return task_id
    elif _json['status'] == 401:
        await token_handler()
        raise ValueError('successfully changed the token')


# task process
async def task_process(task_id, category):
    global headers
    url = categories[category] + '/' + str(task_id)
    name = None
    while_counter = 0
    session = aiohttp.ClientSession()
    while while_counter < 3:
        response = await session.get(url=url, headers=headers)
        _json = await response.json()
        if _json['status'] == 200:
            if _json['data']['progress'] == 100:
                image_url = _json['data']['image']
                image_format_index_start = image_url.index('?')
                name = './' + \
                    image_url[image_format_index_start -
                              15:image_format_index_start]
                response = await session.get(image_url)
                with open(name, 'wb') as file:
                    async for chunk in response.content.iter_chunked(10):
                        file.write(chunk)
                await session.close()
                break
            elif _json['data']['state'] == -1:
                await session.close()
                raise ValueError('failed')
            else:
                while_counter += 1
                await asyncio.sleep(5)
                continue
        else:
            await session.close()
            await token_handler()
            raise ValueError('successfully changed the token')
    await session.close()
    if name is None:
        raise RuntimeError('Tried 3 time but failed')
    return name
