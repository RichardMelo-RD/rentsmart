"""RentSmart - versão com JANELA (interface gráfica).

    python main.py            -> abre a janela
    python main_terminal.py   -> versão sem janela, só no terminal
"""


def main() -> None:
    try:
        from interface import AppRentSmart
        app = AppRentSmart()
    except Exception as erro:  # computador sem tkinter ou sem tela disponível
        print(f"Interface gráfica indisponível ({erro}). Usando o terminal.")
        from main_terminal import modo_terminal
        modo_terminal()
        return
    app.mainloop()


if __name__ == "__main__":
    main()
