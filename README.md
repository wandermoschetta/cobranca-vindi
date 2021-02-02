# Integração com API de Cobrança de Cartão de Crédito Recorrente e Avulsa

### Integração de cobrança avulsa de Cartão de Crédito com a empresa [Vindi](https://vindi.com.br/)

O objetivo desse projeto é enviar cobranças de cartão de crédito de forma automática,
conforme regras estabelecidas pela [empresa](http://familiaprever.com.br).

O Processo está rodando desde(01/11/2020) gerando quase 2000 cobranças mensais de alguns clientes da empresa. 
  
### As seguintes regras foram estabelecidas para processo de cobrança na plataforma:

  * **Cadastrar clientes**, assim como dados de telefone, cartão de crédito, validando os dados antes da finalização do cadastro.
  
  * **Gerar faturas** de cartão de crédito para cada cliente, em cima de regras de negócio já   estabelecidas.
  * **Gerenciar os pagamentos** dessas faturas, assim como agendamento, cancelamento e alteração de  valores das cobranças entre nosso ERP e a plataforma Vindi.
  * **Gerenciar o cancelamento** dos clientes.

