import os
import time
from typing import Literal, TypedDict, Union

import gradio as gr

from src.interface.leitor_documento import leitor_documento
from src.db import Database, TipoTransporte
from src.agents.agent import (
    FinalAgentResponse,
    PensamentoAgentResponse,
    WriteAgentResponse,
    gerar_resposta_agent,
)
from src.agents.tools import obter_caminho_documento


class NavigationState(TypedDict):
    tipo: Literal["chat", "documento"]
    caminho: str | None


def criar_gradio():
    db = Database.get_singleton()

    with gr.Blocks() as demo:
        Database.read()
        initial: NavigationState = {
            "tipo": "chat",
            "caminho": "itinerario.md",
        }
        route = gr.State(initial)

        # current = gr.Column()

        def responder(pergunta: str, historico: list):
            start_time = time.time()
            segments: list[Union[str, gr.FileData, gr.Component]] = ["pensando"]
            response = gr.ChatMessage(
                content=segments,
                metadata={
                    "status": "pending",
                },
            )
            yield response
            try:
                resposta = gerar_resposta_agent(pergunta)

                for i in resposta:
                    if isinstance(i, WriteAgentResponse):
                        segments.append(gr.FileData(path=i.file))
                        # yield response
                        # docs.change(lambda : obter_docs(), outputs=[docs])
                    # elif isinstance(i, PensamentoAgentResponse):
                    #     # pensamento_conteudo.value += i.pensamento
                    #     final += i.pensamento
                    elif isinstance(i, FinalAgentResponse):
                        # pen
                        segments[0] = i.conteudo
                    yield response
                response.metadata["status"] = "done"
                yield response
            except Exception as e:
                segments[0] = str(e)
                yield response
            response.metadata["duration"] = time.time() - start_time
            yield response

        with gr.Row():
            with gr.Column(scale=1):
                with gr.Tab("chats", scale=1):
                    gr.ChatInterface(
                        fn=responder,
                        title="🤖 Agente de mobilidade pública — GS - Citizentech",
                        description="Agente com RAG. Powered by Gemini.",
                        # inputs=gr.Textbox(label="Pergunta", placeholder="Digite aqui..."),
                        # outputs=gr.Textbox(label="Resposta"),
                        # title="Assistente escrita",
                        # description="Seu agente de escrita",
                        chatbot=gr.Chatbot(
                            [
                                {
                                    "content": [
                                        m["conteudo"],
                                        *[
                                            gr.FileData(path=obter_caminho_documento(a))
                                            for a in m["arquivos"]
                                            if m["role"] == "chat"
                                        ],
                                    ],
                                    "role": (
                                        "user"
                                        if m["role"] == "usuario"
                                        else "assistant"
                                    ),
                                }
                                for m in db.mensagens
                            ]
                        ),
                        # examples=[
                        #     "Faça sua pergunta"
                        # ]
                    )
             
                with gr.Tab("perfil"):
                    usuario = Database.get_singleton().usuario

                    def salvar(nome, localizacao, preferencia):
                        usuario["nome"] = nome
                        usuario["localizacao"] = localizacao
                        usuario["preferencia_transpote"] = preferencia
                        
                        Database.get_singleton().write()

                    gr.Interface(
                        salvar,
                        [
                            gr.Textbox(usuario["nome"], label="nome"),
                            gr.Textbox(usuario["localizacao"], label="localização"),
                            gr.Radio(
                                [TipoTransporte.ONIBUS, TipoTransporte.METRO],
                                value=usuario["preferencia_transpote"],
                                label="preferencia",
                            ),
                            
                        ],
                        None,
                    )
                with gr.Tab("documentos", scale=1):
                    leitor_documento()
        return demo
