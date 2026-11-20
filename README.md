# GS — Agente • IA de mobilidade

**Prompt Engineering & AI • FIAP • 2º Semestre 2026**

**Integrantes:** 
- Gabriel de Paula Santos (RM573195) 
- Joao Lucas Silva Lopes (RM573875)
- Enzo Ribeiro (RM569429)
  
---

imagem de comprovação do projeto rodando:

![imagem](print.png)

# Domínio

O domínio escolhido pelo grupo foi **Agente de Inteligência Artificial aplicado à assistência de escrita**.

A proposta do projeto é desenvolver um agente profissional capaz de auxiliar o usuário em diferentes etapas da produção e desenvolvimento de textos.

O agente terá consigo várias tools que permitiram se adaptar para atender da melhor forma o usuário, indo desde escrever arquivos de textos a uma busca inteligente pelas mensagens anteriores do sistema.


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

# ChatOllama

O modelo utilizado é:

```text
gemma4:cloud
```

O modelo é utilizado através do **Ollama Cloud**.

A chave de acesso é configurada através do arquivo `.env`:

```env
OLLAMA_API_KEY=<sua-chave>
```

# Interface

A interface atual do agente funciona através do gradio, criando um aplicativo web que é divido em três abas.
a primeira aba é a de chat, onde o usuário pode conversar com nosso agente fazendo perguntas ou solicitando ações
a segunda aba é o formulário, que permite o usuário editar seus dados.
e a terceira é a leitor de documentos, que permite o usuário ver os documentos técnicos.

# Principais arquivos

| Arquivo | Responsabilidade |
|----------|------------------|
| `main.py` | Inicialização do chatbot |
| `src/agent` | criação do agent do projeto |
| `src/chain.py` | pipeline da ia antiga, usado como auxiliar |
| `src/interface` | configuração da interface gradio |
| `src/rag` | configuração do rags |
| `src/tools` | configuração das tools |
| `assets/prompt/` | Prompts utilizados pelo chatbot |

# Como executar

## 1. Criar o ambiente virtual

```bash
python -m venv .venv
```

## 2. Ativar o ambiente virtual

### Windows

```bash
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

## 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

## 4. Configurar o Ollama Cloud

Crie um arquivo `.env` baseado no `.env.example`:

```env
OLLAMA_API_KEY=<sua-chave>
```

## 5. Configurar o ollama local

devido algums problemas com o ollama cloud para embeds, é preciso tanto ter ele em sua maquina quanto ter a chave do ollama cloud, siga as instruções do [site oficial](https://ollama.com/download) para abaixar o ollama 

após ter o ollama em sua maquina, inicie o servidor e rode com o modelo de embeddings, cada comando em um terminal distinto


```base
ollama serve

ollama pull nomic-embed-text
```

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

- O funcionamento depende da configuração do Ollama Cloud;
- O Rags só consegue acompanhar as modificações feitas pelo agent, quando o usuário modifica um arquivo manualmente ele fica fora do rastreio;
- o visualizar de arquivos esta limitado a arquivos já disponivel quando o projeto é executado, não conseguindo rastrear arquivos criados pelo agent, isso devido a uma limitação interna do gradio, mas ainda é possivel ver as modificações aplicadas arquivos já existentes
- o funcionamento interno do gradio pode ser defeituoso quando algum arquivo dos documentos é deletado, mesmo reininciando o projeto

# Teste e Avaliação

para testar e avaliar o agent, preparamos um arquivo separado chamado iteracoes.md, nele contém três perguntas feitas em iterações de testes, o objetivo da pergunta, e a resposta dada.

além disso, para avaliar o comportamento interno do agent, cada mensagem criada por ele, tem seus pensamentos registrados no arquivo data/logs/logs.txt, assim é possivel saber cada ferramenta usada e como o agente utilizou elas
