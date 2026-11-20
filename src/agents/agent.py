import json
import os
from typing import Iterator, Literal, cast

from langchain_classic import hub

# from langchain_c.agents import AgentExecutor, create_react_agent
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_classic.prompts import PromptTemplate
from langchain_classic.schema import AgentAction
from src.agents.llm import instanciar_llm
from langchain_ollama import ChatOllama
from langsmith import Client
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents.guardrail import Input_Guardrail
from src.db import Database
from src.agents.tools import obter_caminho_documento, tools


class AgentResponse: ...


class WriteAgentResponse(AgentResponse):
    file: str

    def __init__(self, file: str):
        self.file = file


class PensamentoAgentResponse(AgentResponse):
    pensamento: str

    def __init__(self, pensamento: str):
        self.pensamento = pensamento


class FinalAgentResponse(AgentResponse):
    conteudo: str

    def __init__(self, conteudo: str):
        self.conteudo = conteudo


def criar_agent():
    # llm = ChatOllama(
    #     # model="qwen3.5:0.8b",
    #     model="gemma4:cloud",
    #     base_url="https://ollama.com",
    #     temperature=0,
    # )
    llm = instanciar_llm()

    # Prompt ReAct padrão do LangChain Hub (testado e otimizado)
    template = open("assets/prompt/agent.md", "r").read()
    prompt_react: PromptTemplate = Client().pull_prompt(
        "hwchase17/react", dangerously_pull_public_prompt=True
    )
    prompt_react.template = template + "\n" + prompt_react.template
    # Criar o agente ReAct
    agente = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt_react,
        # dangerously_pull_public_prompt=True
    )
    # AgentExecutor — roda o loop e controla o número de iterações
    executor = AgentExecutor(
        agent=agente,
        tools=tools,
        verbose=False,
        max_iterations=8,
        handle_parsing_errors=True,
    )

    return executor


agent: AgentExecutor | None = None

def criar_executor(input: str):
    global agent
    if not agent:
        agent = criar_agent()
        print("agent created")
    guardrail = Input_Guardrail(input)

    if len(guardrail.validar_input()) > 0:
        raise Exception("Pergunta rejeitada pelo sistemas")
    return agent

def gerar_resposta_agent_direta(input: str) -> str:
    try:
        agent = criar_executor(input)
        resposta = agent.invoke({ "input": input })
        # print(resposta)
        return resposta["output"] 
    except Exception as e:
        return e.__str__()
def gerar_resposta_agent(input: str) -> Iterator[AgentResponse]:
    agent = criar_executor(input)
    # resposta = executor.json
    
    caminho_logs = f"Chat_log.txt"

    with open(caminho_logs, "a", encoding="utf-8") as logs:
        logs.write(f"\n--------\nRespondendo: {input}\n")
        arquivos: list[str] = []

        def adicionar_arquivo(arquivo: str):
            if not arquivo in arquivos:
                arquivos.append(arquivo)

        for i in agent.stream({"input": input}):
            if "actions" in i:
                actions: list[AgentAction] = i["actions"]

                for action in actions:
                    if action.tool == "tool_ler":
                        tool_input = action.tool_input
                        adicionar_arquivo(cast(str, tool_input))
                    if action.tool == "tool_escrever":
                        data: dict = (
                            json.loads(action.tool_input)
                            if type(action.tool_input) == str
                            else cast(dict, action.tool_input)
                        )

                        name = obter_caminho_documento(data["nome"])

                        adicionar_arquivo(data["nome"])

                        yield WriteAgentResponse(name)

            # if "steps" in i:
            #     print(i["steps"])

            # yield PensamentoAgentResponse(i["messages"][0].content)

            for message in i["messages"]:
                logs.write("\n")
                logs.write(message.content)
            if "output" in i:
                resposta = i["output"]
                yield FinalAgentResponse(resposta)
                db = Database.get_singleton()
                db.salvar_conversa(
                    {"role": "usuario", "conteudo": input, "arquivos": arquivos}
                )

                db.salvar_conversa(
                    {"role": "chat", "conteudo": resposta, "arquivos": arquivos}
                )

                db.write()
    # return resposta.str["output"]
