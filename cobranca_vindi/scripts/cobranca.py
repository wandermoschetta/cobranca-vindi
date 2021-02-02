from datetime import date
from cobranca_vindi.request_api.parser import isvalid_email

from cobranca_vindi.db.mssql.base import Query
from cobranca_vindi.request_api.customers import list_one_or_all as customer_list, add as customer_add, \
    remove as customer_archive, unarchive as customer_unarchive
from cobranca_vindi.request_api.payment_profiles import list_one_or_all as card_list, add as card_add, \
    remove as card_remove
from cobranca_vindi.request_api.parser import remove_accentuation
from cobranca_vindi.request_api.bills import list_one_or_all as bill_list, add as bill_add, \
    remove as bill_cancel
from cobranca_vindi.request_api.products import list_one_or_all as product_list
from cobranca_vindi.request_api.payment_methods import list_one_or_all as payment_method_list
from cobranca_vindi.request_api.charge import list_one_or_all as list_charge
from cobranca_vindi.request_api.transaction import list_one_or_all as list_trans


def add():
    print('#' * 80)
    print("CADASTRADO DE ASSOCIADOS NA VINDI")
    print('#' * 80)
    query = Query()
    sql_add = '''select top 500 a.inscricao,a.nome,a.cpf,rtrim(ltrim(a.assemail)) as email,a.cobranca,a.numerocobranca,
    a.ComplementoCob,a.bairrocob,a.cepcob,c.nome as cidade, c.uf as estado,'BR' as pais, isnull(a.telefone,''),
    isnull(a.Telefone2,''),isnull(a.Celular,''),rtrim(ltrim(a.nomeTitularCartaoCredito)),
    rtrim(ltrim(a.VencimentoCartaoCredito)),rtrim(ltrim(a.NumeroCartaoCredito)),rtrim(ltrim(a.NumeroAutCartaoCredito)),
    isnull(a.fax,''),isnull(f.token_vindi,'') as token, case a.codigobandeiracentercob when 39 then 'mastercard'
    when 42 then 'visa' when 60 then 'elo' when 40 then 'hipercard' when 41 then 'diners_club' when 62 then 'jcb' 
    when 38 then 'American Express' end as tag_cartao  
    from associados a 
    left outer join cidades c on c.Codigo = a.CidadeCob 
    inner join filiais f on f.Codigo = a.codigoEF 
    where a.status in(1,2)  
    and a.familia = 'CARTAOCR' and a.DataCanceladoRemessaCartaoCred is null and plataformacartaocredito='VINDI'
    and exists(select m.inscricao from vwparcela m where m.inscricao = a.inscricao 
    and m.vencimento >= cast( (SUBSTRING(a.mesiniciocartaocredito,7,4)+'-'+
    SUBSTRING(a.mesiniciocartaocredito,4,2)+'-'+SUBSTRING(a.mesiniciocartaocredito,1,2)+' 00:00:00') 
    as datetime) 
    and m.vencimento >= cast(  (cast(cast(getdate() as date) as varchar(11))+' 00:00:00') as datetime) 
    and m.pagamento is null and m.codigologcobranca is null and m.numboleto is null and m.MenLote is null and 
    m.tipomensalidade in(0,1) )'''

    list_associate = query.select(sql_add)
    for associate in list_associate:
        code = associate[0]
        token = associate[20]
        tag_cartao = associate[21]

        clients = customer_list(token, code=code)

        if not clients['customers'] or clients['customers'][0]['status'] == 'archived':

            if not clients['customers']:
                # add clientes / perfil de pagamento / faturas
                address = {
                    "street": remove_accentuation(associate[4]),
                    "number": associate[5],
                    "additional_details": remove_accentuation(associate[6]) if associate[6] else "",
                    "zipcode": associate[8],
                    "neighborhood": remove_accentuation(associate[7]),
                    "city": remove_accentuation(associate[9]),
                    "state": associate[10],
                    "country": associate[11]
                }

                phone = []
                if associate[12] == '' and associate[13] == '' and associate[14] == '' and associate[19] == '':
                    pass
                else:
                    if associate[12] != '' and associate[13] != '' and associate[14] != '' and associate[19] != '':
                        if associate[12] != '' and len(associate[12]) >= 10:
                            dic = {"phone_type": "landline", "number": "55" + associate[12]}
                            phone.append(dic)
                        if associate[14] != '' and len(associate[14]) >= 10:
                            dic = {"phone_type": "mobile", "number": "55" + associate[14]}
                            phone.append(dic)
                        if associate[19] != '' and len(associate[19]) >= 10:
                            dic = {"phone_type": "mobile", "number": "55" + associate[19]}
                            phone.append(dic)
                    else:
                        if associate[12] != '' and len(associate[12]) >= 10:
                            dic = {"phone_type": "landline", "number": "55"+associate[12]}
                            phone.append(dic)
                        if associate[13] != '' and len(associate[13]) >= 10:
                            dic = {"phone_type": "landline", "number": "55" + associate[13]}
                            phone.append(dic)
                        if associate[14] != '' and len(associate[14]) >= 10:
                            dic = {"phone_type": "mobile", "number": "55" + associate[14]}
                            phone.append(dic)
                        if associate[19] != '' and len(associate[19]) >= 10:
                            if int(associate[19][3:4]) == 9:
                                dic = {"phone_type": "mobile", "number": "55" + associate[19]}
                            elif int(associate[19][3:4]) < 7:
                                dic = {"phone_type": "landline", "number": "55" + associate[19]}
                            else:
                                dic = {}
                            if len(dic) != 0:
                                phone.append(dic)

                customer_id = _customer_subscribe(token, str(associate[0]), remove_accentuation(associate[1]),
                                                  associate[2], remove_accentuation(associate[3]) if associate[3] else "", address, phone)
            else:
                customer_id = _customer_unarchive(token, clients['customers'][0]['id'], clients['customers'][0]['code'],
                                                  clients['customers'][0]['name'])

            if customer_id != 0:
                _payment_profile_subscribe(token, remove_accentuation(associate[1]), str(associate[0]), customer_id,
                                           remove_accentuation(str(associate[15])), str(associate[16]),
                                           str(associate[17]), str(associate[18]), tag_cartao)

                _bill_subscribe(token, str(associate[0]), remove_accentuation(associate[1]), customer_id)

            print(' ')
            print(' ')

        else:
            print(" -> {} {}  [CLIENTE JÁ CADASTRADO]".format(str(associate[0]), remove_accentuation(associate[1])))

            _payment_profile_subscribe(token, remove_accentuation(associate[1]), str(associate[0]),
                                       clients['customers'][0]['id'], remove_accentuation(str(associate[15])),
                                       str(associate[16]), str(associate[17]), str(associate[18]), tag_cartao)

            _bill_subscribe(token, str(associate[0]), remove_accentuation(associate[1]), clients['customers'][0]['id'])
            print(' ')
            print(' ')


def _customer_subscribe(token, code, name, registry_code, email, address, phones):
    if len(phones) == 0:
        if isvalid_email(email):
            result = customer_add(token, code=code, name=name, registry_code=registry_code, email=email,
                                  address=address)
        else:
            result = customer_add(token, code=code, name=name, registry_code=registry_code, address=address)
    else:
        if isvalid_email(email):
            result = customer_add(token, code=code, name=name, registry_code=registry_code, email=email,
                                  address=address, phones=phones)
        else:
            result = customer_add(token, code=code, name=name, registry_code=registry_code, address=address,
                                  phones=phones)
    item = ""
    valor = ""
    for key, value in result.items():
        item = str(key)
        valor = value

    if item == 'errors':
        print(" -> {} {}  [FALHOU CADASTRO]".format(code, name))
        print("     -> ", item, valor)
        msg = ""
        for key in valor:
            msg += key['parameter']+' '+key['message']+', '

        msg = msg[:len(msg)-2]
        _log_cobranca("CADASTRO", msg, code, '', None, None, None, None, None, None, None)
        return 0

    print(" -> {} {}  [CADASTRO OK]".format(code, name))
    return result['customer']['id']


def _customer_unarchive(token, customer_id, code, name):
    result = customer_unarchive(customer_id, token)

    item = ""
    valor = ""
    for key, value in result.items():
        item = str(key)
        valor = value

    if item == 'errors':
        print(" -> Associado {}   ID {}       [FALHOU CADASTRO]".format(code, customer_id))
        print("     -> ", item, valor)
        msg = ""
        for key in valor:
            msg += key['parameter'] + ' ' + key['message'] + ', '

        msg = msg[:len(msg) - 2]
        _log_cobranca("RECADASTRO", msg, code, '', None, None, None, None, None, None, None)
        return 0

    print(" -> {} {}  [RECADASTRO OK]".format(code, name))

    return result['customer']['id']


def _payment_profile_subscribe(token, name, code, customer_id, holder_name, card_expiration, card_number, card_cvv,
                               payment_company_code):
    card = card_list(token, customer_id=customer_id)

    payment_method_code = 'credit_card'

    if not card['payment_profiles']:
        result = card_add(token, customer_id=customer_id, holder_name=holder_name, card_expiration=card_expiration,
                          card_number=card_number, card_cvv=card_cvv, payment_method_code=payment_method_code,
                          payment_company_code=payment_company_code)

        print('Result Card Add => ', result)

        item = ""
        valor = ""
        for key, value in result.items():
            item = str(key)
            valor = value
        if item == 'errors':
            print('ERRO ---> ', item, valor)
            
            tam = int(len(code) + len(name) + 6)
            print(' ' * tam, '[PERFIL DE PAGAMENTO FALHOU]')
            msg = ""
            for key in valor:
                msg += key['parameter'] + ' ' + key['message'] + ', '
            msg = msg[:len(msg) - 2]
            _log_cobranca("CADASTRO CARTAO", msg, code, '', None, None, None, None, None, None, None)
            return

        tam = int(len(code)+len(name)+6)
        print(' ' * tam, '[PERFIL DE PAGAMENTO CADASTRADO OK]')
    else:
        if card['payment_profiles'][0]['status'] == 'active':
            tam = int(len(code) + len(name) + 6)
            print(' ' * tam, '[PERFIL DE PAGAMENTO JA ATIVO]')
        else:
            result = card_add(token, customer_id=customer_id, holder_name=holder_name, card_expiration=card_expiration,
                              card_number=card_number, card_cvv=card_cvv)
            item = ""
            valor = ""
            for key, value in result.items():
                item = str(key)
                valor = value
            if item == 'errors':
                tam = int(len(code) + len(name) + 6)
                print(' ' * tam, '[PERFIL DE PAGAMENTO FALHOU]')
                msg = ""
                for key in valor:
                    msg += key['parameter'] + ' ' + key['message'] + ', '
                msg = msg[:len(msg) - 2]
                _log_cobranca("CADASTRO NOVO CARTAO", msg, code, '', None, None, None, None, None, None, None)
                return

            tam = int(len(code) + len(name) + 6)
            print(' ' * tam, '[PERFIL DE PAGAMENTO NOVO CADASTRADO OK]')


def _bill_subscribe(token, code, name, customer_id):
    query = Query()
    sql_parc = '''select m.inscricao, ltrim(rtrim(m.Referencia)), convert(varchar,m.Vencimento,103), 
                      (substring( CONVERT(varchar, vencimento,102),1,4)+'-'+
                      substring( CONVERT(varchar, vencimento,102),6,2)+'-'+
                      substring( CONVERT(varchar, vencimento,102),9,2)), a.mesInicioCartaoCredito
                      ,m.valor,m.tipomensalidade, 
                      rtrim(ltrim(substring( convert(varchar,a.mesInicioCartaoCredito,102),1,2)))
                    from vwParcela m inner join associados a on a.inscricao = m.inscricao
                    where m.inscricao = {} 
                       and m.vencimento >= cast((SUBSTRING(a.mesiniciocartaocredito, 7, 4) + '-' +
                          SUBSTRING(a.mesiniciocartaocredito, 4, 2) + '-' + 
                          SUBSTRING(a.mesiniciocartaocredito, 1,2) + ' 00:00:00') as datetime)
                       and m.Vencimento >= cast((cast(cast(getdate() as date) as varchar(11))+' 00:00:00') as datetime) 
                       and m.pagamento is null
                       and m.codigologcobranca is null and m.numboleto is null and m.MenLote is null 
                       and m.tipomensalidade in(0,1)'''.format(code)
    list_parc = query.select(sql_parc)
    tam = int(len(code) + len(name) + 6)

    if not list_parc:
        print(' ' * tam, '[FATURA NÃO CADASTRADA, NÃO HÁ PARCELA(S) DO ASSOCIADO]')
        return

    product_id = product_list(token, status='active')
    payment_method_code = payment_method_list(token)

    for rows in list_parc:
        is_error = False
        vencimento = str(rows[3])
        data_atual = date.today()
        dia_fatura = str(rows[7])

        if str(data_atual)[5:7] == vencimento[5:7]:
            if int(str(data_atual)[9:10]) <= int(dia_fatura):
                if int(vencimento[5:7]) == 2 and int(dia_fatura) > 28:
                    data_fatura = vencimento[:7] + '-28'
                else:
                    data_fatura = vencimento[:7]+'-'+dia_fatura
            else:
                data_fatura = str(data_atual)
        else:
            if int(vencimento[5:7]) == 2 and int(dia_fatura) > 28:
                data_fatura = vencimento[:7] + '-28'
            else:
                data_fatura = vencimento[:7]+'-'+dia_fatura

        valor_fatura = rows[5]
        desc = str('Insc. '+str(rows[0])+' Referente a '+str(rows[1]))

        bill_items = [{"product_id": product_id['products'][0]['id'], "amount": valor_fatura, "description": desc}]

        bill = bill_add(token, customer_id=customer_id,
                        payment_method_code=payment_method_code['payment_methods'][0]['code'],
                        billing_at=data_fatura, due_at=vencimento, bill_items=bill_items)

        item = ""
        valor = ""
        for key, value in bill.items():
            item = str(key)
            valor = value
        if item == 'errors':
            is_error = True
            print(' ' * tam, '[FATURA DO MÊS {} FALHOU]'.format(rows[1]))
            print(bill)
            msg = ""
            for key in valor:
                msg += key['id'] + ' ' + key['message'] + ', '
            msg = msg[:len(msg) - 2]

            # checa se já existe esse erro gravado no log pra essa referencia, se existir não grava novamente
            sql_log = '''select inscricao from logcobranca where inscricao = {} and referencia = '{}' 
                  and descricao_erro = '{}' '''.format(code, rows[1], msg)
            log_exists = query.select(sql_log)
            if not log_exists:
                _log_cobranca("FATURA NOVA", msg, code, rows[1], None, None, None, None, None, None, None)

        if is_error is False:
            # cadastra no log da cobrança os dados da fatura e o codigo do log na parcela
            print(' ' * tam, '[FATURA DA REFERÊNCIA {} CADASTRADA OK]'.format(rows[1]))

            data_emissao = bill['bill']['billing_at'][:10]+' '+bill['bill']['billing_at'][11:23]
            data_vencimento = bill['bill']['due_at'][:10]+' '+bill['bill']['due_at'][11:23]
            data_geracao = bill['bill']['created_at'][:10]+' '+bill['bill']['created_at'][11:23]

            _log_cobranca(None, None, code, rows[1], bill['bill']['id'], bill['bill']['status'],
                          data_emissao, data_vencimento, data_geracao, bill['bill']['url'], valor_fatura)

            cobranca = query.select('''select codigo from logcobranca where Inscricao = {} 
                                           and referencia = '{}' and id_fatura={}'''.format(code, str(rows[1]),
                                                                                            bill['bill']['id']))
            codigo_cobranca = 0
            for rows2 in cobranca:
                codigo_cobranca = rows2[0]

            sql_update = "update "
            if int(rows[6]) == 1:
                sql_update += " mensalidade set  codigologcobranca={} where inscricao = {} " \
                                  "and referencia = '{}' ;".format(codigo_cobranca, code, str(rows[1]))
            else:
                sql_update += " inscricao set  codigologcobranca={} where inscricao = {} " \
                                  "and parcela = {} ;".format(codigo_cobranca, code, str(rows[1]))

            updated = query.update(sql_update)
            print("     ***[Código da Cobrança Gravado na Parcela] - ", updated)

            status = bill['bill']['status']

            if status == "paid":
                pago_em = bill['bill']['updated_at'][:10] + ' ' + bill['bill']['updated_at'][11:23]

                sql_baixa = "insert into extrato(inscricao,referencia,valor,valorpago,pagamento,datahora,tipodoc," \
                            "tipomensalidade,usuario)values({},'{}',{},{},'{}',getdate(),'{}',{},'{}')".format(
                                                                                                      code,
                                                                                                      str(rows[1]),
                                                                                                      valor_fatura,
                                                                                                      valor_fatura,
                                                                                                      pago_em,
                                                                                                      'RET',
                                                                                                      int(rows[6]),
                                                                                                      'VINDI')
                query_baixa = Query()
                inserted = query_baixa.insert(sql_baixa)
                print("     ***[Cobrança Baixada no Extrato] - ", inserted)

                query_update_parcela = Query()

                sql_update = "update "
                if int(rows[6]) == 1:
                    sql_update += " mensalidade set  valorpago={},pagamento='{}' where inscricao = {} " \
                                  "and referencia = '{}'; ".format(valor_fatura, pago_em, code, str(rows[1]))
                else:
                    sql_update += " inscricao set  valorpago={}, pagamento='{}' where inscricao = {} " \
                                  "and parcela = {}; ".format(valor_fatura, pago_em, code, str(rows[1]))

                updated = query_update_parcela.update(sql_update)
                print("     ***[Cobrança Baixada na Parcela] - ", updated)

            # _log_transacao(token, bill['bill']['id'])


def _log_cobranca(error, message_error, inscricao, referencia, id_fatura, status_fatura, data_emissao_fatura,
                  data_vencimento_fatura, data_geracao_fatura, url_pagamento_fatura, valor_fatura):
    query_log_cob = Query()
    if error:
        sql_insert = "insert into logcobranca(plataforma,inscricao,referencia,data_inclusao,erro,descricao_erro)" \
                     "values('{}',{},'{}', getdate(),'{}','{}')".format('VINDI', inscricao, referencia, error,
                                                                        message_error)
        inserted = query_log_cob.insert(sql_insert)
        print("     ***[Gravado na Logcobranca] - ", inserted)
    else:
        sql_insert = "insert into logcobranca(plataforma,inscricao,referencia,data_inclusao," \
                     "id_fatura,status_fatura,data_emissao_fatura,data_vencimento_fatura,data_geracao_fatura," \
                     "url_pagamento_fatura,valor_fatura)" \
                     "values('{}',{},'{}', getdate(),'{}','{}','{}','{}','{}','{}',{})".format('VINDI', inscricao,
                                                                                               referencia, id_fatura,
                                                                                               status_fatura,
                                                                                               data_emissao_fatura,
                                                                                               data_vencimento_fatura,
                                                                                               data_geracao_fatura,
                                                                                               url_pagamento_fatura,
                                                                                               valor_fatura)
        inserted = query_log_cob.insert(sql_insert)
        print("     ***[Gravado na Logcobranca] - ", inserted)


def update_bills():
    print('#' * 80)
    print('ATUALIZANDO FATURAS NA VINDI')
    print('#' * 80)
    query = Query()

    # Atualiza Status da Fatura
    sql_faturas = '''select m.inscricao, m.Referencia,m.valor as valor_parcela, l.valor_fatura, l.id_fatura, 
                    l.status_fatura,m.tipomensalidade,
                    (substring( CONVERT(varchar, vencimento,102),1,4)+'-'+
                    substring( CONVERT(varchar, vencimento,102),6,2)+'-'+
                    substring( CONVERT(varchar, vencimento,102),9,2)) as vencimento,
                    isnull(f.token_vindi,''), m.valorpago,
                    rtrim(ltrim(substring( convert(varchar,a.mesInicioCartaoCredito,102),1,2)))
                    from vwParcela m
                    inner join associados a on a.inscricao = m.inscricao
                    inner join logcobranca l on l.codigo = m.codigologcobranca
                    inner join filiais f on f.Codigo = a.codigoEF
                    where l.erro is null 
                        and a.status in(1,2) 
                        and a.familia = 'CARTAOCR' 
                        and l.status_fatura in('review', 'pending', 'scheduled')
                        and m.codigologcobranca is not null
                        and m.vencimento between getdate()-30 and getdate()+120 
                        and m.tipomensalidade in(0,1)
                  '''

    lista_faturas = query.select(sql_faturas)
    for fatura in lista_faturas:
        id_fatura = fatura[4]
        inscricao = fatura[0]
        referencia = fatura[1]
        valor_parcela = fatura[2]
        valor_fatura = fatura[3]
        tipo_mensalidade = fatura[6]
        token = fatura[8]
        valorpago = fatura[9]
        dia_fatura = str(fatura[10])

        bills = bill_list(token, id=id_fatura)

        status = bills['bills'][0]['status']

        if status != fatura[5]:
            query_status = Query()
            sql_status = "update logcobranca set status_fatura = '{}' where id_fatura = {} and " \
                         "inscricao = {}".format(status, id_fatura, inscricao)
            updated = query_status.update(sql_status)
            print("Inscrição {} Ref. {} ID FAT. #{}   [Atualizado Status para {} ] - ".format(inscricao,
                                                                                              referencia,
                                                                                              str(id_fatura), status),
                  updated)

            if status == 'canceled':
                sql_update = "update "
                if int(tipo_mensalidade) == 1:
                    sql_update += " mensalidade set  codigologcobranca=null where inscricao = {} " \
                                  "and referencia = '{}'; ".format(inscricao, str(referencia))
                else:
                    sql_update += " inscricao set  codigologcobranca=null where inscricao = {} " \
                                  "and parcela = {}; ".format(inscricao, str(referencia))

                query_update = Query()
                updated_parc = query_update.update(sql_update)

                print("Inscrição {} Ref. {} ID FAT. #{}   [PARCELA CANCELADA] - ".format(inscricao,
                                                                                         referencia, str(id_fatura)),
                      updated_parc)

            if status == "paid":
                pago_em = bills['bills'][0]['updated_at'][:10] + ' ' + bills['bills'][0]['updated_at'][11:23]

                sql_baixa = "insert into extrato(inscricao,referencia,valor,valorpago,pagamento,datahora,tipodoc," \
                            "tipomensalidade,usuario)values({},'{}',{},{},'{}',getdate(),'{}',{},'{}')".format(
                                                                                                      inscricao,
                                                                                                      referencia,
                                                                                                      valor_parcela,
                                                                                                      valor_fatura,
                                                                                                      pago_em,
                                                                                                      'RET',
                                                                                                      tipo_mensalidade,
                                                                                                      'VINDI')
                query_baixa = Query()
                inserted = query_baixa.insert(sql_baixa)
                print("     ***[Cobrança Baixada no Extrato] - ", inserted)

                query_update_parcela = Query()
                sql_update = "update "
                if int(tipo_mensalidade) == 1:
                    sql_update += " mensalidade set  valorpago={},pagamento='{}' where inscricao = {} " \
                                  "and referencia = '{}'; ".format(valor_fatura, pago_em, inscricao, str(referencia))
                else:
                    sql_update += " inscricao set  valorpago={}, pagamento='{}' where inscricao = {} " \
                                  "and parcela = {}; ".format(valor_fatura, pago_em, inscricao, str(referencia))

                updated = query_update_parcela.update(sql_update)
                print("     ***[Cobrança Baixada na Parcela] - ", updated)

        else:
            if status == 'scheduled':
                if valor_parcela != valor_fatura:
                    bill_canceled = bill_cancel(token, id_fatura)

                    print('bill_canceled - > ', bill_canceled)

                    item = ""
                    valor = ""

                    if bill_canceled:
                        for key, value in bill_canceled.items():
                            item = str(key)
                            valor = value
                        if item == 'errors':
                            print('   ', '[CANCELAMENTO DA FATURA DO MÊS {} FALHOU]'.format(referencia))
                            msg = ""
                            for key in valor:
                                msg += key['id'] + ' ' + key['message'] + ', '
                            msg = msg[:len(msg) - 2]

                            # checa se já existe esse erro gravado no log pra essa referencia,
                            # se existir não grava novamente
                            sql_log = '''select inscricao from logcobranca where inscricao = {} and referencia = '{}' 
                                          and descricao_erro = '{}' '''.format(inscricao, referencia, msg)
                            log_exists = query.select(sql_log)
                            if not log_exists:
                                _log_cobranca("CANCELAMENTO FATURA", msg, inscricao, referencia, None, None, None, None,
                                              None, None, None)
                    else:
                        query_status = Query()
                        sql_status = "update logcobranca set status_fatura = '{}' where id_fatura = {} and " \
                                     "inscricao = {}".format('canceled', id_fatura, inscricao)
                        updated = query_status.update(sql_status)
                        print("Inscrição {} Ref. {} ID FAT. #{}   [Atualizado Status para {} ] - ".format(inscricao,
                                                                                                          referencia,
                                                                                                          str(
                                                                                                           id_fatura),
                                                                                                          'canceled'),
                              updated)

                        # insere uma nova fatura
                        product_id = product_list(token)
                        payment_method_code = payment_method_list(token)
                        customer_id = customer_list(token, code=inscricao)
                        valor_fatura = valor_parcela
                        vencimento = str(fatura[7])

                        data_atual = date.today()

                        if str(data_atual)[5:7] == vencimento[5:7]:
                            if int(str(data_atual)[9:10]) <= int(dia_fatura):
                                if int(vencimento[5:7]) == 2 and int(dia_fatura) > 28:
                                    data_fatura = vencimento[:7] + '-28'
                                else:
                                    data_fatura = vencimento[:7] + '-' + dia_fatura
                            else:
                                data_fatura = str(data_atual)
                        else:
                            if int(vencimento[5:7]) == 2 and int(dia_fatura) > 28:
                                data_fatura = vencimento[:7] + '-28'
                            else:
                                data_fatura = vencimento[:7] + '-' + dia_fatura

                        desc = str('Insc. ' + str(inscricao) + ' Referente a ' + str(referencia))

                        bill_items = [{"product_id": product_id['products'][0]['id'], "amount": valor_fatura,
                                       "description": desc}]

                        bill = bill_add(token, customer_id=customer_id['customers'][0]['id'],
                                        payment_method_code=payment_method_code['payment_methods'][0]['code'],
                                        billing_at=data_fatura, due_at=vencimento, bill_items=bill_items)

                        # verifica se fatura cadastrou senão gera logcobrança de erro
                        item = ""
                        valor = ""
                        for key, value in bill.items():
                            item = str(key)
                            valor = value
                        if item == 'errors':
                            print('   ', '[NOVA FATURA DO MÊS {} FALHOU]'.format(referencia))
                            msg = ""
                            for key in valor:
                                msg += key['id'] + ' ' + key['message'] + ', '
                            msg = msg[:len(msg) - 2]

                            # checa se já existe esse erro gravado no log pra essa referencia,
                            # se existir não grava novamente
                            query_log_fatura = Query()
                            sql_log = '''select inscricao from logcobranca where inscricao = {} and referencia = '{}' 
                                                              and descricao_erro = '{}' '''.format(inscricao,
                                                                                                   referencia, msg)
                            log_exists = query_log_fatura.select(sql_log)
                            if not log_exists:
                                _log_cobranca("NOVA FATURA", msg, inscricao, referencia, None, None, None, None,
                                              None, None, None)
                        else:
                            id_fatura_nova = bill['bill']['id']
                            data_emissao = bill['bill']['billing_at'][:10] + ' ' + bill['bill']['billing_at'][11:23]
                            data_vencimento = bill['bill']['due_at'][:10] + ' ' + bill['bill']['due_at'][11:23]
                            data_geracao = bill['bill']['created_at'][:10] + ' ' + bill['bill']['created_at'][11:23]

                            _log_cobranca(None, None, inscricao, referencia, id_fatura_nova, bill['bill']['status'],
                                          data_emissao, data_vencimento, data_geracao, bill['bill']['url'],
                                          valor_fatura)

                            query_select_cod = Query()

                            sql_cod = "select codigo from logcobranca where inscricao = {} and referencia = '{}' " \
                                " and id_fatura = {}".format(inscricao, str(referencia), id_fatura_nova)

                            codigo_cobranca = query_select_cod.select(sql_cod)

                            sql_update = "update "
                            if int(tipo_mensalidade) == 1:
                                sql_update += " mensalidade set  codigologcobranca={} where inscricao = {} " \
                                              "and referencia = '{}'; ".format(str(codigo_cobranca[0][0]), inscricao,
                                                                               str(referencia))
                            else:
                                sql_update += " inscricao set  codigologcobranca={} where inscricao = {} " \
                                              "and parcela = {}; ".format(str(codigo_cobranca[0][0]), inscricao,
                                                                          str(referencia))
                            query_update_cod = Query()
                            updated = query_update_cod.update(sql_update)
                            print("     ***[Atualizado código da cobrança na Parcela] - ", updated)

                            print('Inscrição {} Ref. {} ID FAT. #{} [NOVA FATURA CADASTRADA]'.format(inscricao,
                                                                                                     referencia,
                                                                                                     str(id_fatura_nova
                                                                                                         )))

                else:
                    if valorpago == 0:
                        bill_canceled = bill_cancel(token, id_fatura)
                        print('BILL CANCELED => ', bill_canceled)

                        item = ""
                        valor = ""

                        if bill_canceled:
                            for key, value in bill_canceled.items():
                                item = str(key)
                                valor = value
                            if item == 'errors':
                                print('   ', '[CANCELAMENTO DA FATURA DO MÊS {} FALHOU]'.format(referencia))
                                msg = ""
                                for key in valor:
                                    msg += key['id'] + ' ' + key['message'] + ', '
                                msg = msg[:len(msg) - 2]

                                # checa se já existe esse erro gravado no log pra essa referencia,
                                # se existir não grava novamente
                                sql_log = '''select inscricao from logcobranca where inscricao = {} and 
                                referencia = '{}' and descricao_erro = '{}' '''.format(inscricao, referencia, msg)
                                log_exists = query.select(sql_log)
                                if not log_exists:
                                    _log_cobranca("CANCELAMENTO FATURA", msg, inscricao, referencia, None, None, None,
                                                  None,
                                                  None, None, None)
                        else:
                            query_status = Query()
                            sql_status = "update logcobranca set status_fatura = '{}' where id_fatura = {} and " \
                                         "inscricao = {}".format('canceled', id_fatura, inscricao)
                            updated = query_status.update(sql_status)

                            print("Inscrição {} Ref. {} ID FAT. #{}   [Atualizado Status para {} ] - ".format(
                                inscricao, referencia, str(id_fatura), 'CANCELED'), updated)

                            sql_update = "update "
                            if int(tipo_mensalidade) == 1:
                                sql_update += " mensalidade set  codigologcobranca=null where inscricao = {} " \
                                              "and referencia = '{}'; ".format(inscricao, str(referencia))
                            else:
                                sql_update += " inscricao set  codigologcobranca=null where inscricao = {} " \
                                              "and parcela = {}; ".format(inscricao, str(referencia))

                            query_update = Query()
                            updated_parc = query_update.update(sql_update)

                            print("Inscrição {} Ref. {} ID FAT. #{}   [PARCELA CANCELADA] - ".format(inscricao,
                                                                                                     referencia,
                                                                                                     str(id_fatura)),
                                  updated_parc)
                    else:
                        print('Inscrição {} Ref. {} ID FAT. #{} [NO STATUS UPDATED]'.format(inscricao, referencia,
                                                                                            str(id_fatura)))
            else:
                print('Inscrição {} Ref. {} ID FAT. #{} [NO STATUS UPDATED]'.format(inscricao, referencia,
                                                                                    str(id_fatura)))
        # _log_transacao(token, id_fatura)


def remove_bills():
    print('#' * 80)
    print('CANCELANDO FATURAS NA VINDI')
    print('#' * 80)
    query = Query()

    # Remove Faturas para contratos com familia diferente de cartão de crédito mas que tenha faturas lançadas
    sql_faturas = '''select m.inscricao, m.Referencia,m.valor as valor_parcela, l.valor_fatura, l.id_fatura, 
                        l.status_fatura,m.tipomensalidade,
                        (substring( CONVERT(varchar, vencimento,102),1,4)+'-'+
                        substring( CONVERT(varchar, vencimento,102),6,2)+'-'+
                        substring( CONVERT(varchar, vencimento,102),9,2)) as vencimento,
                        isnull(f.token_vindi,'')
                        from vwParcela m
                        inner join associados a on a.inscricao = m.inscricao
                        inner join logcobranca l on l.codigo = m.codigologcobranca
                        inner join filiais f on f.Codigo = a.codigoEF
                        where l.erro is null 
                            and a.status in(1,2) 
                            and a.familia <> 'CARTAOCR' 
                            and l.status_fatura in('review', 'pending', 'scheduled')
                            and m.codigologcobranca is not null
                            and m.vencimento > getdate()-30 
                            and m.tipomensalidade in(0,1)
                        order by m.inscricao     
                      '''
    lista_faturas = query.select(sql_faturas)

    inscricao_anterior = 0
    quantidade_cancelado = 0
    token_prior = None

    for fatura in lista_faturas:
        id_fatura = fatura[4]
        inscricao = fatura[0]
        referencia = fatura[1]
        tipo_mensalidade = fatura[6]
        token = fatura[8]

        bill_canceled = bill_cancel(token, id_fatura)

        print("bill canceled -> ", bill_canceled)

        if bill_canceled:
            item = ""
            valor = ""
            for key, value in bill_canceled.items():
                item = str(key)
                valor = value
            if item == 'errors':
                print('   ', '[FATURA CANCELADA DO MÊS {} FALHOU]'.format(referencia))
                msg = ""
                for key in valor:
                    msg += key['id'] + ' ' + key['message'] + ', '
                msg = msg[:len(msg) - 2]

                # checa se já existe esse erro gravado no log pra essa referencia,
                # se existir não grava novamente
                query_log_fatura = Query()
                sql_log = '''select inscricao from logcobranca where inscricao = {} and referencia = '{}' 
                                                                          and descricao_erro = '{}' '''.format(
                                                                                                        inscricao,
                                                                                                        referencia,
                                                                                                        msg)
                log_exists = query_log_fatura.select(sql_log)
                if not log_exists:
                    _log_cobranca("FATURA CANCELADA", msg, inscricao, referencia, None, None, None, None,
                                  None, None, None)
        else:
            status = 'canceled'
            query_status = Query()
            sql_status = "update logcobranca set status_fatura = '{}' where id_fatura = {} and " \
                         "inscricao = {}".format(status, id_fatura, inscricao)
            updated = query_status.update(sql_status)

            sql_update = "update "
            if int(tipo_mensalidade) == 1:
                sql_update += " mensalidade set  codigologcobranca=null where inscricao = {} " \
                              "and referencia = '{}'; ".format(inscricao, str(referencia))
            else:
                sql_update += " inscricao set  codigologcobranca=null where inscricao = {} " \
                              "and parcela = {}; ".format(inscricao, str(referencia))

            query_update = Query()
            updated_parc = query_update.update(sql_update)

            print("Inscrição {} Ref. {} ID FAT. #{}   [FATURA CANCELADA] - ".format(inscricao,
                                                                                    referencia, str(id_fatura)),
                  updated, updated_parc)

            customer = customer_list(token, code=inscricao)
            id_payment_profile = list_payment_profile_active(token, customer['customers'][0]['id'])
            removed_payment_profile = card_remove(token, id_payment_profile)
            print("Inscrição {}                       [PERFIL DE PAGAMENTO CANCELADO] - ".format(inscricao),
                  removed_payment_profile)
            quantidade_cancelado += 1

            if inscricao_anterior != inscricao and inscricao_anterior > 0:
                # arquiva o cliente anterior
                customer_prior = customer_list(token_prior, code=inscricao_anterior)

                customer_archived = customer_archive(token_prior, customer_prior['customers'][0]['id'])
                print("Inscrição {}                       [CLIENTE ARQUIVADO] - ".format(inscricao_anterior),
                      customer_archived)
                inscricao_anterior = inscricao
                token_prior = token
            else:
                inscricao_anterior = inscricao
                token_prior = token

    if quantidade_cancelado > 0:
        # arquivo o cliente do ultimo registro da query ou com só um registro
        customer_prior = customer_list(token_prior, code=inscricao_anterior)

        customer_archived = customer_archive(token_prior, customer_prior['customers'][0]['id'])
        print("Inscrição {}                       [CLIENTE ARQUIVADO] - ".format(inscricao_anterior),
              customer_archived)

    # Remove Faturas para contratos que estão na familia Cartão de Crédito e cancelado
    sql_faturas = '''select m.inscricao, m.Referencia,m.valor as valor_parcela, l.valor_fatura, l.id_fatura, 
                               l.status_fatura,m.tipomensalidade,
                               (substring( CONVERT(varchar, vencimento,102),1,4)+'-'+
                               substring( CONVERT(varchar, vencimento,102),6,2)+'-'+
                               substring( CONVERT(varchar, vencimento,102),9,2)) as vencimento,
                               isnull(f.token_vindi,'')
                               from vwParcela m
                               inner join associados a on a.inscricao = m.inscricao
                               inner join logcobranca l on l.codigo = m.codigologcobranca
                               inner join filiais f on f.Codigo = a.codigoEF
                               where l.erro is null 
                                   and a.status in(3) 
                                   and a.familia = 'CARTAOCR' 
                                   and l.status_fatura in('review', 'pending', 'scheduled')
                                   and m.codigologcobranca is not null
                                   and m.vencimento > getdate()-30
                                   and m.tipomensalidade in(0,1)
                               order by m.inscricao     
                             '''
    lista_faturas2 = query.select(sql_faturas)

    inscricao_anterior = 0
    quantidade_cancelado = 0
    token_prior = None

    for fatura2 in lista_faturas2:
        id_fatura = fatura2[4]
        inscricao = fatura2[0]
        referencia = fatura2[1]
        tipo_mensalidade = fatura2[6]
        token = fatura2[8]

        bill_canceled2 = bill_cancel(token, id_fatura)

        if bill_canceled2:
            for key, value in bill_canceled2.items():
                item = str(key)
                valor = value
                if item == 'errors':
                    print('   ', '[FATURA CANCELADA DO MÊS {} FALHOU]'.format(referencia))
                    msg = ""
                    for key2 in valor:
                        msg += key2['id'] + ' ' + key2['message'] + ', '
                    msg = msg[:len(msg) - 2]

                    # checa se já existe esse erro gravado no log pra essa referencia,
                    # se existir não grava novamente
                    query_log_fatura = Query()
                    sql_log = '''select inscricao from logcobranca where inscricao = {} and referencia = '{}' 
                                                                                     and descricao_erro = '{}' '''.\
                        format(inscricao, referencia, msg)
                    log_exists = query_log_fatura.select(sql_log)
                    if not log_exists:
                        _log_cobranca("FATURA CANCELADA", msg, inscricao, referencia, None, None, None, None,
                                      None, None, None)
        else:
            status = 'canceled'
            query_status = Query()
            sql_status = "update logcobranca set status_fatura = '{}' where id_fatura = {} and " \
                         "inscricao = {}".format(status, id_fatura, inscricao)
            updated = query_status.update(sql_status)

            sql_update = "update "
            if int(tipo_mensalidade) == 1:
                sql_update += " mensalidade set  codigologcobranca=null where inscricao = {} " \
                              "and referencia = '{}'; ".format(inscricao, str(referencia))
            else:
                sql_update += " inscricao set  codigologcobranca=null where inscricao = {} " \
                              "and parcela = {}; ".format(inscricao, str(referencia))

            query_update = Query()
            updated_parc = query_update.update(sql_update)

            print("Inscrição {} Ref. {} ID FAT. #{}   [FATURA CANCELADA] - ".format(inscricao,
                                                                                    referencia, str(id_fatura)),
                  updated_parc, updated)

            customer = customer_list(token, code=inscricao)
            id_payment_profile = list_payment_profile_active(token, customer['customers'][0]['id'])
            removed_payment_profile = card_remove(token, id_payment_profile)
            print("Inscrição {}                       [PERFIL DE PAGAMENTO CANCELADO] - ".format(inscricao),
                  removed_payment_profile)

            quantidade_cancelado += 1

            if inscricao_anterior != inscricao and inscricao_anterior > 0:
                # arquiva o cliente anterior
                customer_prior = customer_list(token_prior, code=inscricao_anterior)

                customer_archived = customer_archive(token_prior, customer_prior['customers'][0]['id'])
                print("Inscrição {}                       [CLIENTE ARQUIVADO] - ".format(inscricao_anterior),
                      customer_archived)
                inscricao_anterior = inscricao
                token_prior = token
            else:
                inscricao_anterior = inscricao
                token_prior = token

    if quantidade_cancelado > 0:
        # arquivo o cliente do ultimo registro da query ou com só um registro
        customer_prior = customer_list(token_prior, code=inscricao_anterior)

        customer_archived = customer_archive(token_prior, customer_prior['customers'][0]['id'])
        print("Inscrição {}                       [CLIENTE ARQUIVADO] - ".format(inscricao_anterior),
              customer_archived)

    # Cancela faturas que estão na familia Cartão com status ativo e suspenso
    # mas trocou de plataforma para CENTERCOB
    sql_faturas = '''select m.inscricao, m.Referencia,m.valor as valor_parcela, l.valor_fatura, l.id_fatura, 
                                   l.status_fatura,m.tipomensalidade,
                                   (substring( CONVERT(varchar, vencimento,102),1,4)+'-'+
                                   substring( CONVERT(varchar, vencimento,102),6,2)+'-'+
                                   substring( CONVERT(varchar, vencimento,102),9,2)) as vencimento,
                                   isnull(f.token_vindi,'')
                                   from vwParcela m
                                   inner join associados a on a.inscricao = m.inscricao
                                   inner join logcobranca l on l.codigo = m.codigologcobranca
                                   inner join filiais f on f.Codigo = a.codigoEF
                                   where l.erro is null 
                                       and a.status in(1,2) 
                                       and a.familia = 'CARTAOCR'
                                       and a.plataformacartaocredito = 'CENTERCOB' 
                                       and l.status_fatura in('review', 'pending', 'scheduled')
                                       and m.codigologcobranca is not null
                                       and m.vencimento > getdate()-30 
                                       and m.tipomensalidade in(0,1) 
                                   order by m.inscricao    
                                 '''
    lista_faturas2 = query.select(sql_faturas)

    inscricao_anterior = 0
    quantidade_cancelado = 0
    token_prior = None

    for fatura2 in lista_faturas2:
        id_fatura = fatura2[4]
        inscricao = fatura2[0]
        referencia = fatura2[1]
        tipo_mensalidade = fatura2[6]
        token = fatura2[8]

        bill_canceled2 = bill_cancel(token, id_fatura)

        if bill_canceled2:
            for key, value in bill_canceled2.items():
                item = str(key)
                valor = value
                if item == 'errors':
                    print('   ', '[FATURA CANCELADA DO MÊS {} FALHOU]'.format(referencia))
                    msg = ""
                    for key2 in valor:
                        msg += key2['id'] + ' ' + key2['message'] + ', '
                    msg = msg[:len(msg) - 2]

                    # checa se já existe esse erro gravado no log pra essa referencia,
                    # se existir não grava novamente
                    query_log_fatura = Query()
                    sql_log = '''select inscricao from logcobranca where inscricao = {} and referencia = '{}' 
                                                                                 and descricao_erro = '{}' '''.format(
                        inscricao,
                        referencia,
                        msg)
                    log_exists = query_log_fatura.select(sql_log)
                    if not log_exists:
                        _log_cobranca("FATURA CANCELADA", msg, inscricao, referencia, None, None, None, None,
                                      None, None, None)
        else:
            status = 'canceled'
            query_status = Query()
            sql_status = "update logcobranca set status_fatura = '{}' where id_fatura = {} and " \
                "inscricao = {}".format(status, id_fatura, inscricao)
            updated = query_status.update(sql_status)

            sql_update = "update "
            if int(tipo_mensalidade) == 1:
                sql_update += " mensalidade set  codigologcobranca=null where inscricao = {} " \
                              "and referencia = '{}'; ".format(inscricao, str(referencia))
            else:
                sql_update += " inscricao set  codigologcobranca=null where inscricao = {} " \
                              "and parcela = {}; ".format(inscricao, str(referencia))

            query_update = Query()
            updated_parc = query_update.update(sql_update)

            print("Inscrição {} Ref. {} ID FAT. #{}   [FATURA CANCELADA] - ".format(inscricao,
                                                                                    referencia, str(id_fatura)),
                  updated_parc, updated)

            customer = customer_list(token, code=inscricao)
            id_payment_profile = list_payment_profile_active(token, customer['customers'][0]['id'])
            removed_payment_profile = card_remove(token, id_payment_profile)
            print("Inscrição {}                       [PERFIL DE PAGAMENTO CANCELADO] - ".format(inscricao),
                  removed_payment_profile)

            quantidade_cancelado += 1

            if inscricao_anterior != inscricao and inscricao_anterior > 0:
                # arquiva o cliente anterior
                customer_prior = customer_list(token_prior, code=inscricao_anterior)

                customer_archived = customer_archive(token_prior, customer_prior['customers'][0]['id'])
                print("Inscrição {}                       [CLIENTE ARQUIVADO] - ".format(inscricao_anterior),
                      customer_archived)
                inscricao_anterior = inscricao
                token_prior = token
            else:
                inscricao_anterior = inscricao
                token_prior = token

    if quantidade_cancelado > 0:
        # arquivo o cliente do ultimo registro da query ou com só um registro
        customer_prior = customer_list(token_prior, code=inscricao_anterior)

        customer_archived = customer_archive(token_prior, customer_prior['customers'][0]['id'])
        print("Inscrição {}                       [CLIENTE ARQUIVADO] - ".format(inscricao_anterior),
              customer_archived)


def _log_transacao(token, id_fatura):
    charge = list_charge(token, bill_id=id_fatura)

    if charge['charges']:
        trans = list_trans(token, charge_id=charge['charges'][0]['id'])
        id_charge = charge['charges'][0]['id']
        tentativas = charge['charges'][0]['attempt_count']

        items_trans = trans['transactions']
        for key in items_trans:
            trans_id = key['id']
            status = key['status']
            msg_gateway = key['gateway_message']
            cod_gateway = key['gateway_response_code']
            msg_brand = key['gateway_response_fields']['brand_return_message']
            cod_brand = key['gateway_response_fields']['brand_return_code']
            data_trans = key['created_at'][:10]+' '+key['created_at'][11:23]

            if cod_gateway is None:
                cod_gateway = 0

            query_trans = Query()
            sql_trans = '''select isnull(id_transacao,0) from logtransacaocobranca where id_fatura = {} and 
                id_transacao = {}'''.format(id_fatura, trans_id)
            lista_trans = query_trans.select(sql_trans)

            if lista_trans.__len__() == 0:
                query_log_trans = Query()
                sql_insert_trans = "insert into LogTransacaoCobranca(id_fatura, id_transacao, id_cobranca, " \
                                   "status_transacao, mensagem_gateway, codigo_gateway, codigo_brand, mensagem_brand," \
                                   " data_criacao_transacao)values({},{},{},'{}','{}','{}','{}','{}','{}')".\
                    format(id_fatura, trans_id, id_charge, status, msg_gateway, cod_gateway, cod_brand, msg_brand,
                           data_trans)

                inserted_trans = query_log_trans.insert(sql_insert_trans)
                print("     ***[Gravado na LogTransacaoCobranca] - ", inserted_trans)
            else:
                if int(tentativas) == 5:
                    query_status = Query()
                    sql_status = '''select isnull(id_fatura,0) from logcobranca where id_fatura = {} and 
                                    status_fatura = '{}' '''.format(id_fatura, 'Vencido')
                    lista_status = query_status.select(sql_status)

                    if lista_status.__len__() == 0:
                        query_update_status = Query()
                        sql_update_status = '''update logcobranca set status_fatura = '{}' where id_fatura = {} and 
                                status_fatura <> '{}' '''.format('Vencido', id_fatura, 'Vencido')
                        lista_update_status = query_update_status.update(sql_update_status)
                        print("     ***[Atualizado Status para Vencido na LogCobranca] - ", lista_update_status)


def list_payment_profile_active(token, customer_id):
    profile = card_list(token, customer_id=customer_id)
    id_profile = 0

    profile_item = profile['payment_profiles']
    for key in profile_item:
        if key['status'] == 'active':
            id_profile = key['id']

    return id_profile
