"""RentSmart - versão TERMINAL (sem janela).

    python main_terminal.py

Faz as perguntas no terminal, valida as respostas, mostra o orçamento e gera o CSV.
"""

from __future__ import annotations

from datetime import date

from imoveis import Apartamento, Casa, Estudio, Imovel
from orcamento import Cliente, Orcamento, TaxaContratual


# ---------- Perguntas com validação (modo terminal) ----------

def perguntar_opcao(pergunta: str, opcoes: list[str]) -> str:
    """Repete a pergunta até o usuário digitar uma das opções válidas."""
    while True:
        resposta = input(pergunta).strip().upper()
        if resposta in opcoes:
            return resposta
        print(f"  Opção inválida. Digite uma destas: {', '.join(opcoes)}")


def perguntar_inteiro(pergunta: str, minimo: int, maximo: int = None, invalidos=()) -> int:
    """Repete a pergunta até receber um inteiro dentro do intervalo."""
    while True:
        try:
            valor = int(input(pergunta))
        except ValueError:
            print("  Digite um número inteiro.")
            continue
        if valor < minimo or (maximo is not None and valor > maximo) or valor in invalidos:
            print("  Valor fora das opções permitidas.")
            continue
        return valor


def perguntar_cliente() -> Cliente:
    """Repete até o nome ser aceito pela própria classe Cliente."""
    while True:
        try:
            return Cliente(input("Nome do cliente: "))
        except ValueError as erro:
            print(f"  {erro}")


def perguntar_inicio() -> date:
    hoje = date.today()
    mes = perguntar_inteiro("Mês de início do contrato (1 a 12): ", 1, 12)
    ano = perguntar_inteiro(f"Ano de início ({hoje.year} a {hoje.year + 2}): ", hoje.year, hoje.year + 2)
    return date(ano, mes, 1)


def criar_imovel() -> Imovel:
    tipo = perguntar_opcao("Tipo de imóvel - [A]Apartamento, [C]Casa ou [E]Estúdio: ", ["A", "C", "E"])

    if tipo == "E":
        vagas = perguntar_inteiro("Quantas vagas de estacionamento? (0 = nenhuma, mínimo 2): ",
                                  0, invalidos=(1,))
        return Estudio(vagas)

    quartos = perguntar_inteiro("Quantos quartos? (1 ou 2): ", 1, 2)
    garagem = perguntar_opcao("Deseja vaga de garagem? (S/N): ", ["S", "N"]) == "S"

    if tipo == "A":
        criancas = perguntar_opcao("Possui crianças? (S/N): ", ["S", "N"]) == "S"
        return Apartamento(quartos, garagem, criancas)
    return Casa(quartos, garagem)


def atender_cliente() -> None:
    cliente = perguntar_cliente()
    inicio = perguntar_inicio()
    imovel = criar_imovel()
    parcelas = perguntar_inteiro("Em quantas parcelas pagar a taxa contratual de R$ 2.000,00? (1 a 5): ", 1, 5)

    orcamento = Orcamento(cliente, imovel, TaxaContratual(parcelas), inicio)
    print(orcamento.resumo())

    if perguntar_opcao("\nOs dados estão corretos? Gerar o CSV? (S/N): ", ["S", "N"]) == "N":
        print("Orçamento descartado.")
        return
    print(f"Projeção de 12 meses salva em: {orcamento.gerar_csv()}")


def modo_terminal() -> None:
    print("=== RentSmart - R.M Imóveis ===\n")
    try:
        while True:
            atender_cliente()
            if perguntar_opcao("\nFazer outro orçamento? (S/N): ", ["S", "N"]) == "N":
                break
            print()
    except (KeyboardInterrupt, EOFError):
        print("\n\nAtendimento cancelado.")
    print("Obrigado por usar o RentSmart!")


if __name__ == "__main__":
    modo_terminal()
