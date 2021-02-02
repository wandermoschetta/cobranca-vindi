import base64
from unicodedata import normalize
import re


def parsing(**data_field):

    """Função para converter dados para JSON
      Keyword arguments:
         **data_field -- parâmetro(s) com chave e valor ex: nome='José da Silva'
    """

    data_parsed = "{"

    for key, value in data_field.items():
        if isinstance(value, list):
            data_parsed += '"{}": ['.format(str(key))
            for key2 in value:
                data_parsed += '{'
                value2 = dict(key2)
                for key3 in value2:
                    if isinstance(value2[key3], str):
                        data_parsed += '"{}":"{}",'.format(key3, str(value2[key3]))
                    else:
                        data_parsed += '"{}":{},'.format(key3, value2[key3])
                data_parsed = data_parsed[:len(data_parsed) - 1] + '},'
            data_parsed = data_parsed[:len(data_parsed) - 1] + '],'
        elif isinstance(value, dict):
            data_parsed = data_parsed + '"{}": {}'.format(str(key), str('{'))
            for key2 in value:
                if isinstance(value[key2], str):
                    data_parsed = data_parsed + '"{}":"{}",'.format(key2, str(value[key2]))
                else:
                    data_parsed = data_parsed + '"{}":{},'.format(key2, value[key2])

            data_parsed = data_parsed[:len(data_parsed) - 1] + '},'
        else:
            if isinstance(value, str):
                data_parsed = data_parsed + '"{}":"{}",'.format(key, str(value))
            else:
                data_parsed = data_parsed + '"{}":{},'.format(key, value)

    data_parsed = data_parsed[:len(data_parsed) - 1] + "}"

    return data_parsed


def encode_base_64(data_encode) -> bytes:
    transform_b = bytes(data_encode, "utf8")
    return base64.b64encode(transform_b)


def decode_base_64(data_decode) -> str:
    decode = "".join([chr(_) for _ in data_decode])
    return decode


def remove_accentuation(words):
    """
        Remove acentos das palavras passadas no argumento[words]
    """
    normalizado = normalize('NFKD', words).encode('ASCII', 'ignore').decode('ASCII')
    word = remove_especial_words(normalizado)

    return word


def isvalid_email(email):
    is_check = re.search(r'[a-zA-Z0-9_-]+@[a-zA-Z0-9]+\.[a-zA-Z]{1,3}$', email)
    if is_check:
        return True
    else:
        return False


def remove_especial_words(words):
    new_string = words
    caracter_especial = "#$:!;"

    for x in caracter_especial:
        new_string = new_string.replace(x, '')
    new_word = new_string
    return new_word
