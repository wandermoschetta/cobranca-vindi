import os
from cobranca_vindi.request_api.parser import encode_base_64, decode_base_64


URL_ENDPOINT = "https://app.vindi.com.br/api/v1"
URL_ENDPOINT_SANDBOX = "https://sandbox-app.vindi.com.br/api/v1"

token_sandbox_servico = os.environ.get('token_sandbox_servico')
token_sandbox_ampaf =   os.environ.get('token_sandbox_ampaf')

token_sandbox_basic_auth_servico = os.environ.get('token_sandbox_basic_auth_servico')
token_sandbox_basic_auth_ampaf = os.environ.get('token_sandbox_basic_auth_ampaf')

token_prod_servico = os.environ.get('token_prod_servico')
token_prod_ampaf = os.environ.get('token_prod_ampaf')

token_prod_servico_base64 = os.environ.get('token_prod_servico_base64')
token_prod_ampaf_base64 = os.environ.get('token_prod_ampaf_base64')

db_path = os.environ.get('db_path')
db_name = os.environ.get('db_name')
db_user = os.environ.get('user_db')
db_pass = os.environ.get('pass_db')


def config_url(link):
    return URL_ENDPOINT+'/'+link  # URL_ENDPOINT_SANDBOX+'/'+link


def encode_token(token):
    return encode_base_64(token+':')


def decode_token(token_encode):
    return decode_base_64(token_encode)
