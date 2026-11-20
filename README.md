# GS — Agente • IA de mobilidade

**Prompt Engineering & AI • FIAP • 2º Semestre 2026**

**Integrantes:** 
- Gabriel de Paula Santos (RM573195) 
- Joao Lucas Silva Lopes (RM573875)
- Enzo Ribeiro (RM569429)
---

# Domínio

O domínio escolhido pelo grupo foi **mobilidade pública**.

A proposta do projeto é desenvolver um agente auxiliar que ajudaria o usuário em relação a transporte público, a ia consegue ver todas as linhas do sistema, visualizar seus dados como itinerario, atrasos e horario, ela pode calcular o tempo de uma viagem considerando seu atraso, pode ver os dados do usuário para personalizar uma resposta e tem controle sobre sua própria mémoria.

# llm

devido a problemas com o serviço do ollama cloud, tivemos que trocar a llm do agente para gemini através de api do google e usar ollama localmente para tarefas como embeddis e para o juiz do ragas, sendo assim, é preciso ter uma chave no google ai studio e ollama instalado.

devido a esses mesmos motivos, o projeto foi desenvolvido localmente, sem colab ou jupyter notebook, siga as instruções no arquivo readme para descobrir como rodar.

## juiz

como dito assim, o juz do sistema é feito através do ollama local, explicando melhor a escolha, principalmente sobre a preferencia acima do gemini api, boa parte dos modelos hospedados pelo google não permitem multiplos candidatos de resposta, algo obrigatorio para que a bibilioteca ragas funcione, sendo assim, um modelo local foi necessário

## ferramentas/tools

### ferramenta de busca (tool_buscar)

essa tool permite o agent procurar pelos dados de uma linha a partir de um string de consulta, mas para uma melhor eficiencia, a ferramenta não faz pesquisa em documentos relatorios, e sim dentro de um documento especifico, a ia deve informar que tipo de informação ela deseja que a ferramenta irá peguar o documento apropriado.

### ferramenta de dados (tool_dados)

essa tool é uma versão alternativa a ferramenta de busca, só que invés de procurar uma linha por palavras chaves, ela recebe diretamente o nome da linha e pegua os dados correspondentes a ela, assim como a ferramenta de busca ela recebe qual documento o texto deve ser pego, mas aqui é opcional, se o documento não for informe, a ferramenta pegua todos os dados da linha, tanto itinerario, historico e atrasos

### ferramenta de tempo (tool_calcular_tempo)

essa ferramenta é a parte do sistema responsável por calcular quanto tempo uma viagem em uma certa linha demoraria, ela recebe o nome da linha a ser calculada, obtém o tempo médio de duração da viagem e soma com os atrasos e incovenientes presentes.

### ferramenta de memoria recente(tool_historico_recente)

essa ferramenta é usada quando o agente percebe uma mensagem abigua ou com contexto cortado, ela busca pelas mensagens anteriores mais recentes e retorna elas em par de (pedido do usuário, resposta do agente)

### ferramenta de listagem de linhas (tool_todos_transportes)

essa tool retorna todas as linhas dentro do sistema.

### ferramenta de dados do usuário (tool_dados_usuario)

essa tool serve para selecionar os dados do usuário atual salvas no sistema, permitindo a ia personalizar a resposta a partir das informações presentes.

# Gemini

como digo anteriormente, utilizamos o gemini devido a problemas com ollama cloud, o modelo atualmente utilizado é:

```text
gemini-3.1-flash-lite
```

O modelo é utilizado através do **Google ai studio**.

A chave de acesso é configurada através do arquivo `.env`:

```env
GEMINI=<chave>
```

# Interface

A interface atual do agente funciona através do gradio, criando um aplicativo web que é divido em três abas.
a primeira aba é a de chat, onde o usuário pode conversar com nosso agente fazendo perguntas ou solicitando ações
a segunda aba é o formulário, que permite o usuário editar seus dados.
e a terceira é a leitor de documentos, que permite o usuário ver os documentos técnicos.

# Principais arquivos

| Arquivo           | Responsabilidade                                     |
| ----------------- | ---------------------------------------------------- |
| `main.py`         | Inicialização do sistema                             |
| `src/agent`       | pasta com todos os arquivos necessários para o agent |
| `src/interface`   | configuração da interface gradio                     |
| `src/agent/rag`   | configuração do rags                                 |
| `src/agent/tools` | configuração das tools                               |
| `assets/prompt/`  | Prompts utilizados pelo chatbot                      |
| `src/db.py`       | Código para o banco de dados                         |

# Como executar

## 1. Criar o ambiente virtual

```bash
python -m venv venv
```

## 2. Ativar o ambiente virtual

### Windows

```bash
.venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

## 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

## 4. Configurar a api do gemini

Crie um arquivo `.env` baseado no `.env.example`, coloque sua chave do google ai studio e informe qual modelo local deseja usar como juiz:

```env
GEMINI=<sua-chave>
JUIZ=<modelo ollama local>
```

## 5. Configurar o ollama local

devido algums problemas com o ollama cloud para embeds, é preciso tanto ter ele em sua maquina quanto ter a chave do ollama cloud, siga as instruções do [site oficial](https://ollama.com/download) para abaixar o ollama 

após ter o ollama em sua maquina, inicie o servidor e rode com o modelo de embeddings, cada comando em um terminal distinto


```base
ollama serve

ollama pull nomic-embed-text
```

também instale o modelo de geração de texto que você escolheu como juiz

## 5. Executar

com os dois ollamas configurados, rode

```bash
python main.py
```

ou use o gradio em caso de hot reload 

```
gradio main.py
```

com o projeto rodado, abra a url que aparecerá no terminal

# Limitações atuais

- os atrasos do sistema são estaticos, não mudam com o tempo e são considerados como sempre ativos, não tendo funcionamento condicional que um sistema de verdade teria.

