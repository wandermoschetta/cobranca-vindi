from .http import post, put, delete, get
from .parser import parsing
from cobranca_vindi.setup import config_url


URL_CUSTOMERS = config_url('customers')


def add(token, **data_add):

    """
        Função responsável em cadastrar cliente

        keywords arguments:
            **data_add -- deve ser passado os seguintes argumentos com sua chave e valor:
                name: string
                    Nome do cliente
                email: string
                    E-mail do cliente
                registry_code: string
                    CPF ou CNPJ do cliente
                code: string
                    Código opcional para referência via API
                notes: string
                    Observações adicionais internas sobre o cliente
                metadata: hash
                    Metadados do cliente
                Address:
                    street string
                        Endereço
                    number string
                        Número do endereço
                    additional_details	string
                        Complemento
                    zipcode	string
                        Código postal
                    neighborhood string
                        Bairro
                    city string
                        Cidade
                    state string
                        Código do estado no formato ISO 3166-2. Exemplo: SP
                    country	string
                        Código do país no formato ISO 3166-1 alpha-2. Exemplo: BR
                    phones:
                        phone_type* string
                            Tipo Enum: [ mobile, landline ]
                        number*	string
                            Número de telefone no formato E.164 incluindo código do país e código de área.
                            Exemplo: 5511975416666
                        extension string
                            Ramal com até 6 dígitos

            Returns:
              retorna dados em JSON

    """
    url = URL_CUSTOMERS
    data_json = str(parsing(**data_add))
    data_json.encode('utf-8')

    return post(url, data_json, token)


def update(token, id_customer, **data_update):
    data_json = str(parsing(**data_update))
    data_json.encode('utf-8')
    url = URL_CUSTOMERS+'/'+str(id_customer)

    return put(url, data_json, token)


def remove(token, id_customer):
    url = URL_CUSTOMERS+'/'+str(id_customer)
    delete(url, token)


def unarchive(id_customer, token):
    url = URL_CUSTOMERS + '/' + str(id_customer) + '/unarchive'
    return post(url, None, token)


def list_one_or_all(token, **filters):
    url = URL_CUSTOMERS

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
