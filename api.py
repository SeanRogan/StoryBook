import json
import requests
from flask import Flask, request

app = Flask(__name__)
'''webhook endpoint receives/up-versions midjourney images when the api is called by the storybook image generation service.'''
image_repo = {}


@app.route('/get-img', methods=['GET'])
def get_images():
    return image_repo


@app.route('/webhook', methods=['POST'])
def initial_img_webhook():
    final_img_url = ''
    token = 'Bearer 8c5990ef-78f5-44b4-aa9b-deec04dc3774'
    res = request.json
    buttons = res['buttons']
    btn_msg_id = res['buttonMessageId']
    msg_id = res['originatingMessageId']
    # url, payload and headers for post request to use upgrade button
    api_url = 'https://api.thenextleg.io/v2/button'
    payload = json.dumps({
        'buttonMessageId': btn_msg_id,
        'button': 'U1'
    })
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    # start off assuming requests are multi_img
    single_img = False
    # loop through the buttons in the response,
    for b in buttons:
        # if there is a 'web' button,
        if b == 'Web':
            # it's a single img
            single_img = True
    # if a single image
    if single_img:
        # save the img_url
        final_img_url = res['imageUrl']
        image_repo[msg_id] = final_img_url
    # if a multi img,
    else:
        # make the post request to get a single image
        requests.request('POST', api_url, headers=headers, data=payload)



    print(str(image_repo))
    return res


if __name__ == '__main__':
    app.run()
