"""CLI de chat: le perguntas no terminal e mostra as respostas baseadas no PDF."""

from search import RespondedorDePerguntas, search_prompt

COMANDOS_DE_SAIDA = ("sair", "exit", "quit")


class ChatNoTerminal:
    """Cuida apenas da conversa no terminal; a busca e a resposta ficam no search."""

    def __init__(self, respondedor: RespondedorDePerguntas):
        self._respondedor = respondedor

    def iniciar(self) -> None:
        self._mostrar_boas_vindas()
        while True:
            pergunta = self._ler_pergunta()
            if pergunta is None:
                break
            if not pergunta:
                continue
            self._responder(pergunta)
        print("\nAte logo!")

    @staticmethod
    def _mostrar_boas_vindas() -> None:
        comandos = ", ".join(COMANDOS_DE_SAIDA)
        print("Chat com o conteudo do PDF.")
        print(f"Digite {comandos} ou Ctrl+D para encerrar.\n")

    @staticmethod
    def _ler_pergunta() -> str | None:
        """Devolve a pergunta digitada, ou None quando o usuario encerra o chat."""
        try:
            pergunta = input("Faça sua pergunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            return None
        return None if pergunta.lower() in COMANDOS_DE_SAIDA else pergunta

    def _responder(self, pergunta: str) -> None:
        print(f"\nPERGUNTA: {pergunta}")
        try:
            print(f"RESPOSTA: {self._respondedor.responder(pergunta)}\n")
        except Exception as erro:
            print(f"RESPOSTA: nao foi possivel responder agora ({erro})\n")


def main() -> None:
    try:
        respondedor = search_prompt()
    except Exception as erro:
        print(f"Nao foi possivel iniciar o chat: {erro}")
        print("Verifique o .env e se o banco esta no ar (docker compose up -d).")
        return

    ChatNoTerminal(respondedor).iniciar()


if __name__ == "__main__":
    main()
