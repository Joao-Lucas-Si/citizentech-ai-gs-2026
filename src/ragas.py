import os
from typing import cast

from datasets import Dataset
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents.tools import procurar_documento
from src.agents.agent import gerar_resposta_agent, gerar_resposta_agent_direta
from src.agents.llm import instanciar_llm, instanciar_llm_hug, instanciar_llm_open_router
from src.agents.rag import embed, rag_indexar
from ragas import RunConfig, evaluate
from ragas.dataset_schema import EvaluationResult
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import faithfulness, answer_relevancy

def avaliar():
    from dotenv import load_dotenv

    load_dotenv()
    retriever = rag_indexar()
    # Configurar o RAGAS para usar o Ollama (sem custo)
    print("avaliando")
    ragas_llm = LangchainLLMWrapper(
        instanciar_llm_hug()
    )
    ragas_embs = LangchainEmbeddingsWrapper(embed())
    faithfulness.llm = ragas_llm
    answer_relevancy.llm = ragas_llm
    answer_relevancy.embeddings = ragas_embs

    perguntas = [
        "quais são os locais que o ônibus TERM. PQ. D. PEDRO II / BUTANTÃ passa?",
        "que horarios o ônibus 508L-10 | TERM. PRINC. ISABEL / ACLIMAÇÃO passa?",
        "há algum incoveniente presente na linha TERM. PQ. D. PEDRO II / BUTANTÃ?",
        "quais os dados de IPIRANGA / LAPA?"
       
    ]
    contextos = [
        ("itinerario", "908T-10 | TERM. PQ. D. PEDRO II / BUTANTÃ"),
        ("horario", "508L-10 | TERM. PRINC. ISABEL / ACLIMAÇÃO"),
        ("atrasos", "908T-10 | TERM. PQ. D. PEDRO II / BUTANTÃ"),
        ("itinerario", "874T-10 | IPIRANGA / LAPA")
    ]
    try:


        def responder(j: str, i: int):
            print(f"executando teste - {i + 1}")
            return gerar_resposta_agent_direta(j)

        dados_avaliacao = {
            "question": [*perguntas],
            "answer": [responder(i, j) for j, i in enumerate(perguntas)],
            "contexts": [
                [d.page_content for d in procurar_documento(c[0], c[1])] for c in contextos
            ],
        }
        resultado = cast(
            EvaluationResult,
            evaluate(
                Dataset.from_dict(dados_avaliacao),
                metrics=[faithfulness, answer_relevancy],
                run_config=RunConfig(timeout=2000 * 20),
                # embeddings= ragas_embs,
                # llm=ChatGoogleGenerativeAI(
                #     model="gemini-3.1-flash-lite",
                #     api_key=os.getenv("CHAVE_GEMINI"),
                # )
                # llm=ChatOllama(
                #     model="gemma4:cloud",
                #     base_url="https://ollama.com",
                #     num_predict=250,
                #     temperature=0,
                # ),
            ),
        )
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
