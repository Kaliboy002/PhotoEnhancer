import requests


# get new fake mail
def get_email():
    email_address = requests.get(
        "https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1", timeout=6).json()[0]
    return email_address


# get token
def get_access_key(email):
    url = 'https://gw.aoscdn.com/base/passport/v2/register'
    json = {"password": "Aa123456", "email": f"{email}",
            "product_id": "482", "language": "en"}
    response = requests.post(url=url, json=json)
    json = response.json()
    if json['status'] == 200 and json['message'] == 'success':
        api_token = json['data']['api_token']
        url = 'https://gw.aoscdn.com/app/picwish/organization/tokens?product_id=482&language=en'
        headers = {"Authorization": f"Bearer {api_token}", 'Content-Type': "application/json",
                   "Origin": "https://picwish.com", "Referer": "https://picwish.com/"}
        response = requests.post(url=url, data={
                                 "origin": "picwish", "language": "en", "app_type": ""}, headers=headers)
        json = response.json()
        if json['status'] == 200 and json['message'] == 'success':
            access_key = json['data']['access_key']
            return access_key
