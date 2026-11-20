import json
import os
from pydoc import doc
from re import Pattern
import re
import time
from typing import TypedDict
from langchain_core.tools import tool

# from langchain_cores.tools import tool
from pydantic import BaseModel, Field

from src.db import Database
from src.agents.rag import atualizar_rag, obter_db, rag_indexar


def obter_caminho_documento(nome: str):
    return f"data/documents/{nome}.md"


def validar_arquivo(nome: str):
    if nome.endswith(".md"):
        return "nome invalido com acordo com as regras de nomenclatura, extensão de arquivo não é permitida"

    if "/" in nome or "\\" in nome:
        return "nome invalido com acordo com as regras de nomenclatura, barras (/) não podem ser incluidas"

    return None


class EscritaParam(BaseModel):
    nome: str = Field(description="o nome do documento")
    conteudo: str = Field(description="o conteúdo do documento")

def procurar_documento(documento: str, query: str):
    retriever = rag_indexar()

    return retriever.invoke(query, filter={"document": documento + ".md"})

@tool
def tool_buscar(param):
    """\
    Use esta tool quando o usuário perguntar
    sobre qualquer informação que pode certas nos documentos técnicos, 
    deve ser informado qual o documento que deseja consultar e a consulta feita.
    assim, ele vai retornar varios trechos do documento requerido.
    leve em consideração as que mais parecem condizer com o que o usuário disse.
    em tarefas voltados a achar algum seção ou trecho dos documentos. é obrigatorio a menção do documento(use o nome do arquivo), da seção e da subsção(se houver) onde o trecho foi encontrado.
    os documentos disponiveis são:
    itinerario: mostra os onibus disponiveis, seus dados e os locais passados pelo trajeto.
    horario: mostra toda a tabela de horario de um ônibus
    atrasos: informa imprevistos que aconteceram em algum trajeto, a duração do imprevistos e quanto tempo ele ira afetar. cada incoveniente tem seu tipo, podendo ele ser transito, ausência ou evento, evento é usado para se referir de forma generalista a organizações públicas que tomam uma parte da rua temporariamente, causando uma mudança de trajeto, já ausência se refere a falta de algum componente para que o veiculo comece a rota, pode ser falta de ônibus no terminal ou de motoristas, por exemplo.
    o documento de horario deve ser usados com auxilio dos outros dois documentos, 
    ele tem pouca informação sobre locais, então é preciso que o usuário informe diretamente o nome do ônibus ou a linha,
    caso não seja fornecido busque previamente no itinerario para achar a linha buscada, e depois procure sobre o horario.
    nunca envie a pergunta do usuário de forma integral, foque em palavras chaves relacionadas a locais, então se a pergunta for "ônibus que passam em X", mande "X" ou "ônibus em X"
    Args:
        documento: o nome do documento a ser lido, nunca use barras (/ e \\), ou extensões de arquivos (.md), apenas siga os três nomes de documento especificados acima 
        query: consulta a ser feita no documento
    os parametros devem seguir formato json
    """
    dados = json.loads(param)

    documento = dados["documento"]
    query = dados["query"]

    return procurar_documento(documento, query)

@tool
def tool_historico_recente():
    """
    Use essa ferramenta para obter o historico recente de mensagens com o usuário.
    ela deve ser usada com prioridade em relação as outras ferramentas de histórico em contextos de historico mais vagas, quando o usuário não especifica qual contexto você deve seguir.
    em mensagens que sejam pedidos para refazer algo, sempre use esse tool.
    em pedidos diretos, que sejam apenas informados uma tarefa simples a ser feita com todo o contexto disponivel, não chame essa ferramenta e nenhuma outra de historico.
    """
    quantidade: int = 3
    # é possivel informar a quantidade de itens passados que devem ser buscados, mas é opcional, o número de itens do historico a ser informado como quantidade se referem sempre a duplas de mensagens, conténdo o pedido do usuário e a resposta do chatbot, ou seja, 3 itens sempre é equivalente a 6 mensagens.

    return Database.get_singleton().mensagens[-(quantidade * 2) :]


@tool
def tool_dados_usuario():
    """
    Use essa ferramenta para obter os dados do usuário que foram cadastrados no sistema.
    como nome, localização atual e preferência de transporte.
    """

    return Database.get_singleton().usuario


@tool
def tool_dados(param):
    """
    use essa tool para obter os dados de um transporte a partir do nome da sua linha
    só deve ser usado quando o usuário especifica a linha, caso não seja fornecido, use tool_buscar, que retornará os mesmos dados.
    essa ferramenta retorna os mesmos documentos que tool_buscar, como atrasos, itinerario e horario, mas deve ser usado quando o assunto é precisão
    para evitar erros na ferramenta de busca.
    Args:
        documento?: o nome do documento a ser lido, nunca use barras (/ e \\), ou extensões de arquivos (.md), apenas siga os três nomes de documento especificados em tool_buscar, pode ser opcional caso queira consultar todos os três documentos simultaneamente
        linha: a linha a ser consultada, o nome de uma linha é obrigátoriamente númerico, sem letras ou caracteres especiais, com exceção do caractere "-", em qualquer caso em que uma linha não siga esse formato XXXX-XX, onde X é um número, informe que não será possivel consultar
    os parametros devem seguir formato json
    caso seja requerido todos os dados de uma linha, mas seu nome não tem sido especificado, use tool_buscar em itinerario, obtenha o nome da linha, e depois use essa para obter os outros dois documentos
    """

    dados: dict
    try:

        dados = json.loads(param)
    except:
        return "os dados devem seguir formato json"

    documento = dados.get("documento")
    linha = dados["linha"]
    if documento and not documento in ["atrasos", "horario", "itinerario"]:
        return f"o documento deve ser um desses três: atrasos, horario, itinerario, {documento} é invalido"

    if not linha:
        return "linha não especificada"
    db = obter_db()
    return db._collection.get(
        where=(
            {"$and": [{"linha": linha}, {"document": documento + ".md"}]}
            if documento
            else {"linha": linha}
        )
    )["documents"]


@tool
def tool_calcular_tempo(linha: str):
    """
    Essa tool serve para obter o tempo de duração de um trajeto considerando seu tempo médio mais imprevistos encontrados.
    use ela sempre que requerido saber o tempo do trajeto, nunca faça o calculo por si mesmo,
    para que ela funcione, a linha deve ser informada, então,
    caso o usuário não informe a linha, apenas dê algumas informações de locais,
    use tool_buscar no documento itinerario e obtenha o nome da linha.
    em perguntas sobre atrasos, é recomendado usar essa ferramenta para obter o impacto total do atraso deve para o trajeto.
    essa tool obrigatóriamente retornará o tempo média da viagem e o tempo atual com atrasos previstos.
    diferente das outras ferramentas, esta recebe apenas uma string simples com o nome da linha, sem formato json
    """
    print(linha)
    db = obter_db()
    itinerario = db._collection.get(
        where=({"$and": [{"linha": linha}, {"document": "itinerario.md"}]})
    )["documents"]
    atrasos = db._collection.get(
        where=({"$and": [{"linha": linha}, {"document": "atrasos.md"}]})
    )["documents"]
    if not itinerario or not atrasos:
        return f"linha {linha} não existe"
    regexp = re.compile(r"\|\s+duração média\s+\|\s+(\S+)\s+\|", flags=re.M)
    
    find = regexp.findall(itinerario[0])
    
    def segmentosParaDuracao(segmentos: list[str]):
        duration = 0

        for seg in segmentos:
            if seg.endswith("h"):
                duration += int(seg[:-1]) * 60
            else:
                duration += int(seg[:-1])
        return duration

    def dividirSegmentos(find: list[str]):
        segments = [i for raw in find for i in raw.strip().split(",")]

        return segments

    duracaoBase = segmentosParaDuracao(dividirSegmentos(find))
    segmentosAtrasos = []
    regexAtraso = re.compile(
        r"\|.+\|.+\|\s+(\d+(?:m|h))\s+\|\s+(\d+(?:m|h))\s+\|.+\|", flags=re.M
    )
    for doc in atrasos:
        finds = regexAtraso.findall(doc)
        tempos = [i[1] for i in finds]

        # print(doc)
        segmentosAtrasos.extend(dividirSegmentos(tempos))
    atrasos = segmentosParaDuracao(segmentosAtrasos)
    duracao = duracaoBase + atrasos
    
    return {"media": duracaoBase, "duracao": duracao}
    # print(itinerario)

@tool
def tool_todos_transportes():
    """
    use essa ferramenta para obter uma listagem de todos os transportes(ônibus, metros trens) disponivêis
    """
    db = obter_db()
    metadatas = db._collection.get(
        where={"document": "itinerario.md"}
    )["metadatas"]
    if not metadatas:
        return "algo deu errado"
    
    linhas = [m.get("seção") for m in metadatas]
    return linhas
    # return 
tools = [
    tool_buscar,
    tool_historico_recente,
    tool_dados_usuario,
    tool_dados,
    tool_calcular_tempo,
    tool_todos_transportes
]
