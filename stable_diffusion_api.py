import base64
import json
import os

from PIL import Image
from io import BytesIO

import requests
# todo implement async img request. need to make the request then go into a getStatus loop until status is complete/an img file is returned, then save the img to the directory


def call_txt2img(prompt):
    # todo build out the api to take arguments to customize the api calls more easily
    negs = ' (nsfw), (nudity:1.2), (poorly drawn), (weird hands:1.1), (deformed hands:1.1), (scary), (mutilated), (lowres), (deformed), (dark), (lowpoly), (CG), (3d), (blurry), (duplicate), (watermark), (label), (signature), (frames), grain, ugly, bad eyes, bad hands, warped, mutilated, duplicate, blurry, plastic'
    scale = 7
    steps = 20
    serverless_api_id = 'sgs8772fiifzn'
    api_key = ''
    # todo all info above ^^ should be in config file or env vars of some sort
    auth = f'Bearer {api_key}'
    url = f'https://api.runpod.ai/v2/{serverless_api_id}/runsync'
    headers = {
        'Authorization': auth,
        'Content-Type': 'application/json'
    }
    payload = {'input': {
        'api_name': 'txt2img',
        'prompt': prompt,
        'negative_prompt': negs,
        'cfg_scale': scale,
        'num_inference_steps': steps
    }}
    res = requests.post(
        url=url,
        headers=headers,
        json=payload,
    )
    response = res.json()
    save_img(response['id'], response['output']['images'][0])
    return response['id']


def save_img(img_id, img):
    # decode base64 string to byte string
    img_bytes = base64.b64decode(img)
    # declare the storage directory
    image_dir = os.curdir + '/images/'
    # send the byte string to BytesIO to convert to an img
    image_file_object = Image.open(BytesIO(img_bytes))
    image_file_object.save(image_dir + f'{img_id}.png', 'PNG')


if __name__ == '__main__':
    call_txt2img('a cat sitting on a rock by the river')
