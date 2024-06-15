# Ideia

MeuCPF nasce como uma api opensource simples de consultas por CPF ao site da [Fazenda.](https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp)

# Como Funciona

Usa redis como pubsub para o Crawler que funciona com Queue e Thread em python.

# Como foi construido

Usa duas partes: - Uma em python que é responsavel por responder os requests feitos no pubsub e fazer o crawling dos dados. - A outra em javascript, que é o websocket basico para se comunicar com o pubsub

# Detalhes
Ainda está em construção, e nao suporta os casos de erro do site da fazenda. Good first issue

# Doc inicial

## Como rodar

1 - Mude o nome de /api/.env.example para .env

```bash
mv ./api/.env.example ./api/.env
```

2 - Suba o container docker com o redis

```bash
docker-compose -f docker-compose.yml up -d
```

3 - Rode o Consumer
vá ate a pasta consumer e instale as dependencias e rode o codigo.

```bash
pip install -r ./consumer/requirements.txt
python3 ./consumer/app.py
```

4 - Rode o Websocket
em um terminal separado, rode o websocket. Essa parte é opicional e está sendo construida, a parte em Python é capaz de, sozinha, responder aos eventos no redis emitindo outros eventos como resposta.

```bash
cd /api
npm install
npm run start
```

## O Websocket

O servidor websocket será iniciado na porta 8080.
O servidor precisa de um header authorization para permitir sua conexão. Esse token ainda está 'hardcoded' no script, e um valor possivel é `usuario1`

Para enviar requests, voce deve enviar um payload no seguinte formato ao websocket:

```json
{
  "event": "cpf",
  "payload": {
    "cpf": "12345678912", //cpf da pessoa, sem a mascara de cpf
    "data_de_nascimento": "12121234", //data de nascimento da pessoa, sem espaços ou traços, formato DDMMYYYY
    "id": "mensagem1" //seu id pra essa requisição, sera retornado a resposta
  }
}
```

Você receberá de volta do websocket:

```json
{
  {
	"event": "processed_event",
	"id": "mensagem1", //id da requisição indormado anteriormente
	"data": {
		"No do CPF": "123.456.789-12",
		"Nome": "FULANO DE TAL",
		"Data de Nascimento": "12/12/1234",
		"Situação Cadastral": "REGULAR",
		"Data da Inscrição": "12/12/1234",
		"Digito Verificador": "00"
	}
}
}
```
