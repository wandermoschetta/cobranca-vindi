from .http import get
from cobranca_vindi.setup import config_url

url_merchants = config_url('merchants')


def list_one_or_all(token, **filters):
    url = url_merchants

    if filters.__len__() > 0:
        url = url + '?query='
        for key in filters:
            if isinstance(filters[key], str):
                if filters.__len__() > 1:
                    url = url + key + '%3D%22' + filters[key] + '%22%26'
                else:
                    url = url + key + '%3D%22' + filters[key] + '%22'
            else:
                if filters.__len__() > 1:
                    url = url + key + '%3D' + str(filters[key]) + '%26'
                else:
                    url = url + key + '%3D' + str(filters[key])

        if filters.__len__() > 1:
            url = url[:len(url) - 3]
        else:
            url = url[:len(url)]

    return get(url, token)


def list_by_id(token, id_merchant):
    url = url_merchants+'/'+str(id_merchant)

    return get(url, token)


def list_current(token):
    url = url_merchants + '/current'
    return get(url, token)
