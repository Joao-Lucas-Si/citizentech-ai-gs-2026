from enum import EnumDict, EnumType
import json
import os
from typing import Literal, Self, TypedDict


class Mensagem(TypedDict):
    role: Literal["usuario", "chat"]
    conteudo: str
    arquivos: list[str]


class User(TypedDict):
    nome: str
    localizacao: str
    preferencia_transpote: str


class TipoTransporte(EnumType):
    ONIBUS = "Ônibus"
    METRO = "Metro"


class Database:
    caminho = "data/db/db.json"

    def __init__(self) -> None:
        self.mensagens: list[Mensagem] = []
        self.usuario: User = {
            "nome": "Leonardo",
            "preferencia_transpote": TipoTransporte.ONIBUS,
            "localizacao": "Avenida Paulista, São Paulo",
        }

    @staticmethod
    def read():
        if os.path.exists(Database.caminho):
            singleton = Database.get_singleton()
            salvo = json.loads(open(Database.caminho, "r", encoding="utf-8").read())
            # print(salvo)
            singleton.mensagens = salvo["mensagens"]
            singleton.usuario = salvo["usuario"]
            # print(singleton.mensagens)

    def write(self):
        if not os.path.exists("data/db"):
            os.mkdir("data/db")
        with open(Database.caminho, "w", encoding="utf-8") as file:
            file.write(
                json.dumps(
                    {
                        "mensagens": self.mensagens,
                        "usuario": self.usuario,
                    },
                    indent=4
                ),
            )

    def salvar_conversa(self, mensagem: Mensagem):
        self.mensagens.append(mensagem)

    singleton: "Database|None" = None

    @staticmethod
    def get_singleton():
        if not Database.singleton:
            Database.singleton = Database()
        return Database.singleton
