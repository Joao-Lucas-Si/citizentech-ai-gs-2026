import os
import sys

import dotenv

dotenv.load_dotenv()

from src.agents.tools import tool_buscar, tool_calcular_tempo, tool_dados, tool_todos_transportes
from src.db import Database
from src.agents.rag import atualizar_rag, obter_db, rag_indexar
from src.interface_final import criar_gradio
from src.agents.agent import gerar_resposta_agent
# from src.evaluate import avaliar
from time import sleep
import gradio as gr
# from io import StringIO

# gr.set_static_paths(paths=["data/documents/"])
if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    Database.read()
    rag_indexar()
    # print(tool_dados("{ \"linha\": \"508L-10\", \"documento\": \"atrasos\" }"))
    # for  i in gerar_resposta_agent("quais ferramentas você tem"):
    #     print(i)
    # print(tool_calcular_tempo("908T-10"))
    # print(tool_todos_transportes())
    demo = criar_gradio()
    
    demo.launch(share=True)

# def main():
#     console = Console(theme=Theme({
#         "background_color": "#191A1B",
#         "info": "dim cyan",
#         "warning": "magenta",
#         "danger": "bold red"
# }), )
    
#     if len(sys.argv) == 2:
#         screen = sys.argv[1]
#         if screen == "-rot":
#             context_rot(console)
#         elif screen == "-ragas":
#             avaliar()
#             ...
#         elif screen == "-chunk":
#             ...
#     else:
#         HistoruScreen().draw(console)

