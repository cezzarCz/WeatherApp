# Imports de bibliotecas necessárias
# Framework Flask:
from flask import Flask, render_template, request
# Flask, framework necessário para o desenvolvimento web em Python.
# render_template, função do flask que renderiza arquivos de templates HTML.
# request, um objeto do Flask que acessa dados enviados pelo cliente.

# Programação Assíncrona:
import asyncio
import aiohttp
# Asyncio, Biblioteca nativa do python que permite programação assíncrona.
# Aiohttp, Usada para chamadas de API assincronas.

# Obter informações de paises:
import pycountry
# Informações como nome, sigla e etc.

key = "9121be263d4c8c18cc880cc377af63eb"  # Key da API OpenWeather

app = Flask(__name__)  # Instância Flask


@app.route('/')  # Rota principal do app, definida por '/'
def index():  # No acesso desta rota a função index é executada
    # Render_template renderiza o arquivo HTML, retornando-o como resposta.
    return render_template('index.html')


# Rota previsão, essa rota é iniciada quando o usuário insere um valor no campo de busca  e clica no botão de pesquisa.
@app.route('/previsao', methods=['POST'])
# Função previsão, é executada quando a rota é acessada por meio do método 'POST'.
def previsao():

    # Variavel 'lugar' é utilizada para recuperar o valor inserido no local de input do HTML, local este que recebe o nome de 'lugar'.
    lugar = request.form['lugar_inserido']

    # O valor contido na variavel é capitalizado a fins de formatação, Exemplo: Usuario inseriu > "brasilia", após o capitalize fica > "Brasilia".
    lugar = lugar.capitalize()

    # Variavel 'dados' é criada, e utiliza a função asyncio para chamada da função 'buscaCidade'
    dados = asyncio.run(buscaCidade(lugar))
    # A função 'asyncio' é utilizada para garantir o gerenciamento da execução assíncrona da função 'buscaCidade',
    # esta função gerencia o contexto de execução, sincronização das tarefas, inicialização e finalização de forma segura e adequada.

    # Os dados recebidos são verificados, caso não existam dados equivalentes ao lugar inserido,
    # uma mensagem de erro é retornada.
    if dados is None:
        erro = f"Erro! O lugar: '{lugar}' não foi encontrado. Tente novamente..."

        # Retorno da mensagem de erro e a string inserida no input.
        return render_template('index.html', erro=erro, lugar=lugar)

    # Atribuições dos dados:
    # Após a resposta bem sucedida da API, os dados são atribuidos a variaveis;
    # Sigla do País
    sigla_pais = dados['sys']['country']

    # Conversão da sigla, no nome do País.
    # Exemplo, a API retorna 'BR', a função 'pycountry' recebe a sigla e retorna 'Brazil' (Sim, em inglês)
    country = pycountry.countries.get(alpha_2=sigla_pais).name

    # Temperatura arredondada.
    # Não sendo muito comum ou intuitivo ver uma temperatura como: 27.16°C, é arredondado para: 27°C.
    temp = round(dados['main']['temp'])

    # Descrição do tempo do local.
    # Exemplo: 'Algumas nuvens', 'Céu limpo', 'Chuva leve'.
    descricao = dados['weather'][0]['description']

    # Umidade do local em '%'.
    umidade = dados['main']['humidity']

    # Icone que aparece ao lado da descricão do tempo.
    # A propia API possui varios icones equivalentes a descrição
    # Exemplo, nuvens, sol, chuva, etc.
    icone1 = dados['weather'][0]['icon']

    # Retorno dos dados recebidos, são passados como "parametros" para o HTML.
    return render_template('index.html', lugar=lugar, country=country, temp=temp, descricao=descricao, umidade=umidade, icone1=icone1)


# Função assíncrona 'buscaCidade'.
# Como se trata de uma operação de entrada e saída, onde o tempo de resposta pode ser demorado (ou não)
# foi optado por uma função assíncrona, que por ser como é, permite que após a requisição feita ao servidor da API
# e durante a espera da resposta desse servidor, outros contextos possam ser executados,
# desta forma aproveitando o tempo ocioso de espera durante a resposta.
# Mesmo que neste contexto em especifico, o codigo não explore completamente este potencial assincrono, ainda
# sim a estrutura assíncrona garante mais responsividade e flexebilidade ao lidar com multi tarefas, sendo
# escalonável e permitindo "upgrades" futuros.
async def buscaCidade(lugar):
    # URL utilizada para fazer a requisição a API, passando o lugar inserido pelo usuário e a key de acesso a API.
    url = f"https://api.openweathermap.org/data/2.5/weather?q={lugar}&appid={key}&lang=pt_br&units=metric"

    # É utilizada a função 'aiohttp' para fazer uma requisição assíncrona ao servidor da API.
    # Sendo que o 'ClientSession' vai funcionar como um gerenciador do contexto assíncrono, este gerenciamento é automatico.
    async with aiohttp.ClientSession() as session:
        # É feita a solicitação get a URL da API, e esta chamada também é assíncrona,
        # o método envia a solicitação HTTP GET para a URL da API.
        async with session.get(url) as resposta:
            # Verificação do código de resposta da API.
            # 200 indica que a requisição foi bem sucedida.
            if resposta.status == 200:
                # Os dados são guardados, sendo que o método 'await' indica que o código deve esperar
                # a chegada das respostas e conversão para JSON, e assim continuar a execução do código.
                dados = await resposta.json()

                # Print no console, a fins de analise dos dados, saber como são separados e etc.
                print(f"Dados de {lugar}: {dados}")

                # Retorno dos dados
                return dados
            else:
                # Caso o código de resposta não seja 200, é mostrado qual código foi retornado.
                print("Erro na solicitação:", resposta.status)

if __name__ == '__main__':
    app.run(debug=True)
