from .http import post, delete, get
from .parser import parsing
from cobranca_vindi.setup import config_url


URL_PAYMENT_PROFILES = config_url('payment_profiles')


def add(token, **data_add):

    """
        Função responsável em cadastrar perfis de pagamentos

        keywords arguments:
            **data_add -- deve ser passado os seguintes argumentos com sua chave e valor:
               holder_name: string
               card_expiration: string
               card_number: string
               card_cvv: string
               payment_method_code: string
               payment_company_code: string
               customer_id: int
            Returns:
              retorna dados em JSON

    """
    url = URL_PAYMENT_PROFILES
    data_json = str(parsing(**data_add))
    data_json.encode('utf-8')

    return post(url, data_json, token)


def remove(token, id_payment_profiles):
    url = URL_PAYMENT_PROFILES+'/'+str(id_payment_profiles)
    return delete(url, token)


def list_one_or_all(token, **filters):
    url = URL_PAYMENT_PROFILES

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


def validate_verify(token, id_payment_profiles):
    """
        Este método permite verificar se um perfil de pagamento existente é válido na
        entidade emissora.
        Apenas o método de pagamento cartão de crédito suporta esta operação.
        Utilize esta função para validar um perfil de pagamento antes da criação de uma assinatura
        que não possua cobrança imediata. Este método é desnecessário para assinaturas com cobrança imediata.

        Funcionamento
            Preferencialmente a plataforma Vindi irá executar o método de validação fornecido nativamente pelas
            adquirentes.Caso este método não esteja disponível, a plataforma poderá realizar uma autorização seguida
            de um cancelamento.

        Resultado
            Para verificar o resultado da validação, verifique no retorno se status=success.

        Disponibilidade
            Esta funcionalidade estará disponível para testes enquanto sua conta Vindi estiver no modo trial.
            Para habilitar no modo produção, instale a extensão "Transação de verificação"
            acessando Configurações > Extensões & Integrações no painel de administração da plataforma.
            Taxas adicionais por verificação poderão ser cobradas.
    """
    url = URL_PAYMENT_PROFILES + '/' + str(id_payment_profiles) + '/verify'
    return post(url, None, token)
