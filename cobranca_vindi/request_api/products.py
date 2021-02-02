from .http import post, put, get
from .parser import parsing
from cobranca_vindi.setup import config_url


URL_PRODUCTS = config_url('products')


def add(token, **data_add):
    """
        Função responsável em cadastrar os produtos da venda

        keywords arguments:
            **data_add -- deve ser passado os seguintes argumentos com sua chave e valor:
                name*	string
                    Nome do produto
                code	string
                    Código externo do produto
                unit	string
                    Texto para descrever uma unidade do produto. Apenas para quantidade variável
                status*	string
                    Status do produto
                    Enum:
                        [ active, inactive, deleted ]
                description	string
                    Descrição interna do produto
                invoice	string
                    Indica se este produto será incluído na emissão de notas fiscais.
                    Se não informado, o valor always será utilizado
                    Enum:
                        [ always, never ]
                pricing_schema {
                    price*	number
                    Preço base
                    minimum_price	number
                    Preço mínimo
                    schema_type*	string
                        Tipo de cálculo da precificação
                        Enum:
                            [ flat, per_unit, step_usage, volume_usage, tier_usage ]
                    pricing_ranges	[
                        Lista de faixas de precificação
                            {
                                start_quantity*	integer($int32)
                                    Início da faixa
                                end_quantity	integer($int32)
                                    Término da faixa. Opcional apenas para a última
                                price*	number
                                    Preço da unidade ou da faixa, dependendo do tipo escolhido
                                overage_price	number
                                    Preço unitário do excedente da faixa

                            }]
                }
                metadata	hash
                    Metadados do produto

                Returns:
                    retorna dados em JSON

    """
    url = URL_PRODUCTS
    data_json = str(parsing(**data_add))
    data_json.encode('utf-8')

    return post(url, data_json, token)


def update(token, id_product, **data_update):
    data_json = str(parsing(**data_update))
    data_json.encode('utf-8')
    url = URL_PRODUCTS+'/'+str(id_product)

    return put(url, data_json, token)


def list_one_or_all(token, **filters):
    url = URL_PRODUCTS

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
