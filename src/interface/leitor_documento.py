import os

import gradio as gr

def leitor_documento():
    #  documentos.select()
    with gr.Row():
        docs = [i for i in os.listdir("base_documental")]
        route = gr.State("itinerario.md")
        
    
        with gr.Column(scale=1):
            for file in docs:
                gr.Button(file).click(
                    lambda x, y=file: y,
                    route,
                    route,
                )

        @gr.render(route)
        def current(current: str):
            if current != "":
                gr.Markdown(
                    open(
                        f"base_documental/{current}"
                    ).read(),
                    scale=9,
                )