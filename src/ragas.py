import os
from typing import cast

from datasets import Dataset
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI
import pandas
from ragas import metrics
from src.agents.tools import procurar_documento
from src.agents.agent import gerar_resposta_agent, gerar_resposta_agent_direta
from src.agents.llm import instanciar_llm
from src.agents.rag import embed, rag_indexar
from ragas import RunConfig, evaluate
from ragas.dataset_schema import EvaluationResult
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper, llm_factory
from ragas.metrics import faithfulness, answer_relevancy

# from ragas.metrics import Faithfulness, AnswerRelevancy


def avaliar():
    from dotenv import load_dotenv

    load_dotenv()
    retriever = rag_indexar()
    # Configurar o RAGAS para usar o Ollama (sem custo)
    print("avaliando")
    ragas_embs = LangchainEmbeddingsWrapper(embed())

    perguntas = [
        "quais são os locais que o ônibus AV. IPIRANGA  / BUTANTÃ passa?",
        "que horarios o ônibus AV. PAULISTA / ACLIMAÇÃO passa?",
        "há algum incoveniente presente na linha AV. IPIRANGA  / BUTANTÃ?",
        "quais os dados de Vila Mariana / LAPA?"
    ]
    contextos = [
        ("itinerario", "9089-10 | AV. IPIRANGA  / BUTANTÃ"),
        ("horario", "5084-10 | AV. PAULISTA / ACLIMAÇÃO"),
        ("atrasos", "9089-10 | AV. IPIRANGA  / BUTANTÃ"),
        ("itinerario", "8742-10 | Vila Mariana / LAPA")
    ]
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI"))
        print(client)
        # llm = llm_factory("gemini-3.1-flash-lite", client=client)
        llm = instanciar_llm()
        faithfulness.llm = llm
        answer_relevancy.llm = llm
        answer_relevancy.embeddings = ragas_embs

        def responder(j: str, i: int):
            print(f"executando teste - {i + 1}")
            resposta = gerar_resposta_agent_direta(j)
            print(resposta)
            return resposta

        respostas = [responder(i, j) for j, i in enumerate(perguntas)]
        dados_avaliacao = {
            "question": [*perguntas],
            "answer": respostas,
            # "response": respostas,
            "contexts": [
                [d.page_content for d in procurar_documento(c[0], c[1])]
                for c in contextos
            ],
        }
        resultado = evaluate(
            Dataset.from_dict(dados_avaliacao),
            llm=llm,
            embeddings=embed(),
            metrics=[faithfulness, answer_relevancy],
        )
        # resultado = cast(
        #     EvaluationResult,
        #     evaluate(
        #         Dataset.from_dict(dados_avaliacao),
        #         metrics=[faithfulness, answer_relevancy],
        #         run_config=RunConfig(timeout=2000 * 20),
        #         # embeddings= ragas_embs,
        #         # llm=ChatGoogleGenerativeAI(
        #         #     model="gemini-3.1-flash-lite",
        #         #     api_key=os.getenv("CHAVE_GEMINI"),
        #         # )
        #         # llm=ChatOllama(
        #         #     model="gemma4:cloud",
        #         #     base_url="https://ollama.com",
        #         #     num_predict=250,
        #         #     temperature=0,
        #         # ),
        #     ),
        # )
        frame: pandas.DataFrame = resultado.to_pandas()
        frame.to_json("avaliacao_ragas.json", indent=4)
        print(resultado.to_pandas())
        # selecionados = resultado.to_pandas()[
        #     ["user_input", "answer_relevancy", "faithfulness"]
        # ]
        # selecionados.rename(
        #     mapper={
        #         "user_input": "pergunta",
        #         "answer_relevancy": "relevancia",
        #         "faithfulness": "fidelidade",
        #     }
        # )
        # print(selecionados)
    except Exception as e:
        print(e)


# def avaliar_rag(pergunta: str, contexto: str):
#     retriever = rag_indexar()
#     # Configurar o RAGAS para usar o Ollama (sem custo)

#     ragas_llm = LangchainLLMWrapper(
#         instanciar_llm()
#     )
#     ragas_embs = LangchainEmbeddingsWrapper(embed())
#     faithfulness.llm = ragas_llm
#     answer_relevancy.llm = ragas_llm
#     answer_relevancy.embeddings = ragas_embs

#     perguntas = [pergunta]
#     contextos = [contexto]
#     try:
#         # engine = AiEngine(model)

#         def responder(j, i):
#             return gerar_resposta_agent(j)

#         dados_avaliacao = {
#             "question": [*perguntas],
#             "answer": [responder(i, j) for j, i in enumerate(perguntas)],
#             "contexts": [
#                 [d.page_content for d in retriever.invoke(c)] for c in contextos
#             ],
#         }
#         print("respondidos")
#         resultado = cast(
#             EvaluationResult,
#             evaluate(
#                 Dataset.from_dict(dados_avaliacao),
#                 metrics=[faithfulness, answer_relevancy],
#                 run_config=RunConfig(timeout=2000 * 20),

#             ),
#         )
#         selecionados = resultado.to_pandas()
#         renomeados = selecionados.rename(
#             columns={
#                 "user_input": "pergunta",
#                 "answer_relevancy": "relevancia",
#                 "faithfulness": "fidelidade",
#                 "retrieved_contexts": "contexto",
#                 "response": "resposta"
#             },

#         )
#         # print(selecionados.to_dict("records"))
#         return renomeados.to_dict("records")
#     except Exception as e:
#         return []
