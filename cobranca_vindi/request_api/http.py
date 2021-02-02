import requests


def post(url_endpoint, body, token):
    url = url_endpoint
    print('ENDPOINT: {} - [POST]'.format(url))

    header = {
        "Authorization": "Basic {}".format(token),
        "content-type": "application/json",
        "charset": "UTF-8"
    }

    if body is not None:
        # print("BODY: {}".format(body))
        r = requests.post(url, data=body, headers=header)
    else:
        r = requests.post(url, headers=header)

    return r.json()


def get(url_endpoint, token):
    print('ENDPOINT: {} - [GET]'.format(url_endpoint))

    header = {
        "Authorization": "Basic {}".format(token),
        "content-type": "application/json",
        "charset": "UTF-8"
    }

    r = requests.get(url_endpoint, headers=header)
    return r.json()


def put(url_endpoint, body, token):
    print('ENDPOINT: {} - [PUT]'.format(url_endpoint))

    header = {
        "Authorization": "Basic {}".format(token),
        "content-type": "application/json",
        "charset": "UTF-8"
    }

    r = requests.put(url_endpoint, data=body, headers=header)
    return r.json()


def delete(url_endpoint, token):
    print('ENDPOINT: {} - [DELETE]'.format(url_endpoint))

    header = {
        "Authorization": "Basic {}".format(token),
        "content-type": "application/json",
        "charset": "UTF-8"
    }

    r = requests.delete(url_endpoint, headers=header)
    return r.json()
