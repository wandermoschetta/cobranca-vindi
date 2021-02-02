from .http import get
from cobranca_vindi.setup import config_url

url_payment = config_url('payment_methods')


def list_one_or_all(token, **filters):
    """
        Métodos de pagamento representam as opções de pagamento disponíveis para nossos clientes
        keyword arguments:
            **filters:
                id: int
                código identificador do nosso cliente na VINDI
                name: string
                    nome do tipo de pagamento ex.: cartão de crédito, débito conta,etc.
                code: string
                    código responsável pela identificação do código do cliente do nosso sistema
                    na VINDI(código do nosso cliente. campo inscrição)
    """

    url = url_payment
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


def list_by_id(token, id_payment):
    url = url_payment + '/' + str(id_payment)
    return get(url, token)
