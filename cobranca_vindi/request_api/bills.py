from .http import post, put, delete, get
from .parser import parsing
from cobranca_vindi.setup import config_url


URL_BILLS = config_url('bills')


def add(token, **data_add):

    """
        Função responsável em cadastrar Faturas do Cliente

        keywords arguments:
            **data_add -- deve ser passado os seguintes argumentos com sua chave e valor:
                customer_id*	integer
                    ID do cliente
                code	string
                    Código externo para referência via API
                installments	integer
                    Número de parcelas. Se não informado, o valor '1' será utilizado
                payment_method_code*	string
                    Código do método de pagamento
                billing_at	string
                    Data opcional de emissão da cobrança no formato ISO 8601. Se não informada,
                    a cobrança será imediata
                due_at	string
                    Data opcional de vencimento da cobrança no formato ISO 8601. Se não informada,
                    o vencimento padrão será utilizado

                bill_items*	[
                    Lista de itens da fatura
                        {
                            product_id	number
                                ID do produto associado ao item da fatura
                            product_code	string
                                Código do produto associado ao item da fatura
                            amount*	number
                                Valor do item da fatura
                            description	string
                                Descrição opcional do item da fatura
                            quantity	integer
                                Quantidade do item da fatura

                            pricing_schema	{
                                price*	number
                                    Preço base
                                minimum_price	number
                                    Preço mínimo
                                schema_type*	string
                                    Tipo de cálculo da precificação
                                    Enum:[ flat, per_unit, step_usage, volume_usage, tier_usage ]
                                pricing_ranges	[
                                    Lista de faixas de precificação
                                          {
                                            start_quantity*	integer
                                                Início da faixa
                                            end_quantity	integer
                                                Término da faixa. Opcional apenas para a última

                                            price*	number
                                                Preço da unidade ou da faixa, dependendo do tipo escolhido
                                            overage_price	number
                                                Preço unitário do excedente da faixa

                                          }]
                            }
                        }]

            Returns:
              retorna dados em JSON

    """
    url = URL_BILLS
    data_json = str(parsing(**data_add))
    data_json.encode('utf-8')

    return post(url, data_json, token)


def update(token, id_bills, **data_update):
    data_json = str(parsing(**data_update))
    data_json.encode('utf-8')
    url = URL_BILLS+'/'+str(id_bills)

    return put(url, data_json, token)


def remove(token, id_bills):
    url = URL_BILLS+'/'+str(id_bills)
    delete(url, token)


def list_one_or_all(token, **filters):
    url = URL_BILLS

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
