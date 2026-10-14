"""Classes do contrato: cliente, taxa contratual e orçamento (resumo + CSV)."""

from __future__ import annotations

import csv
import os
import re
import unicodedata
from dataclasses import dataclass
from datetime import date

from imoveis import Imovel

MESES_ABREV = ("Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
               "Jul", "Ago", "Set", "Out", "Nov", "Dez")


def moeda(valor: float) -> str:
    """Formata número no padrão brasileiro: R$ 1.234,56."""
    texto = f"{abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"- R$ {texto}" if valor < 0 else f"R$ {texto}"


class Cliente:
    """Quem está pedindo o orçamento."""

    def __init__(self, nome: str):
        self.nome = nome  # passa pela validação do setter abaixo

    @property
    def nome(self) -> str:
        return self._nome

    @nome.setter
    def nome(self, valor: str) -> None:
        valor = " ".join(valor.split())
        if len(valor) < 2:
            raise ValueError("Informe o nome do cliente (mínimo 2 letras).")
        self._nome = valor

    def nome_arquivo(self) -> str:
        """Nome sem acentos nem espaços, para usar no arquivo: 'João Silva' -> 'joao_silva'."""
        sem_acento = unicodedata.normalize("NFKD", self.nome).encode("ascii", "ignore").decode()
        return re.sub(r"[^a-z0-9]+", "_", sem_acento.lower()).strip("_") or "cliente"


class TaxaContratual:
    """Taxa de contrato de R$ 2.000,00, parcelável em 1 a 5 vezes."""

    VALOR = 2000.0
    MAX_PARCELAS = 5

    def __init__(self, parcelas: int):
        if not 1 <= parcelas <= self.MAX_PARCELAS:
            raise ValueError(f"A taxa pode ser parcelada de 1 a {self.MAX_PARCELAS} vezes.")
        self.parcelas = parcelas

    def valor_parcela(self) -> float:
        return round(self.VALOR / self.parcelas, 2)

    def parcela_do_mes(self, mes: int) -> float:
        """Valor da taxa cobrado no mês informado (0 depois da última parcela)."""
        if mes > self.parcelas:
            return 0.0
        # Ajuste de centavos na última parcela para fechar exatamente R$ 2.000,00
        if mes == self.parcelas:
            return round(self.VALOR - self.valor_parcela() * (self.parcelas - 1), 2)
        return self.valor_parcela()

    def descricao(self) -> str:
        if self.parcelas == 1:
            return f"À vista: 1x de {moeda(self.VALOR)}"
        texto = f"{self.parcelas}x de {moeda(self.valor_parcela())}"
        ultima = self.parcela_do_mes(self.parcelas)
        if ultima != self.valor_parcela():
            texto += f" (última de {moeda(ultima)})"
        return texto


@dataclass
class LinhaProjecao:
    """Um mês da projeção anual."""

    mes: int
    referencia: str
    aluguel: float
    parcela_taxa: float
    total_mes: float
    acumulado: float


class Orcamento:
    """Reúne cliente, imóvel e taxa; mostra o resumo e gera a projeção de 12 meses."""

    MESES = 12

    def __init__(self, cliente: Cliente, imovel: Imovel, taxa: TaxaContratual, inicio: date):
        self.cliente = cliente
        self.imovel = imovel  # qualquer subclasse de Imovel serve (polimorfismo)
        self.taxa = taxa
        self.inicio = inicio

    def referencia_do_mes(self, mes: int) -> str:
        """Mês 1 = mês de início do contrato. Ex.: início Nov/2026 -> mês 3 = Jan/2027."""
        indice = self.inicio.month - 1 + (mes - 1)
        return f"{MESES_ABREV[indice % 12]}/{self.inicio.year + indice // 12}"

    def projecao(self) -> list[LinhaProjecao]:
        aluguel = self.imovel.aluguel_mensal()
        linhas, acumulado = [], 0.0
        for mes in range(1, self.MESES + 1):
            parcela = self.taxa.parcela_do_mes(mes)
            total = round(aluguel + parcela, 2)
            acumulado = round(acumulado + total, 2)
            linhas.append(LinhaProjecao(mes, self.referencia_do_mes(mes), aluguel,
                                        parcela, total, acumulado))
        return linhas

    def total_previsto(self) -> float:
        return self.projecao()[-1].acumulado

    def resumo(self) -> str:
        largura = 54
        linhas = ["", "=" * largura, "RENTSMART - ORÇAMENTO DE LOCAÇÃO".center(largura), "=" * largura,
                  f"Cliente: {self.cliente.nome}",
                  f"Imóvel:  {self.imovel}",
                  f"Início:  {self.referencia_do_mes(1)}",
                  "", "ALUGUEL MENSAL"]
        for item in self.imovel.detalhamento():
            linhas.append(f"  {item.descricao:<37}{moeda(item.valor):>15}")
        linhas.append("  " + "-" * (largura - 2))
        linhas.append(f"  {'Aluguel mensal':<37}{moeda(self.imovel.aluguel_mensal()):>15}")
        linhas += ["", "TAXA CONTRATUAL (cobrada à parte)",
                   f"  {'Valor total':<37}{moeda(TaxaContratual.VALOR):>15}",
                   f"  Parcelamento: {self.taxa.descricao()}",
                   "", f"  {'Total previsto em 12 meses':<37}{moeda(self.total_previsto()):>15}",
                   "=" * largura]
        return "\n".join(linhas)

    def gerar_csv(self, pasta: str = ".") -> str:
        """Salva a projeção em 'orcamento_<cliente>.csv' (abre direto no Excel)."""
        caminho = os.path.join(pasta, f"orcamento_{self.cliente.nome_arquivo()}.csv")

        def numero(valor: float) -> str:
            return f"{valor:.2f}".replace(".", ",")

        with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(["Mes", "Referencia", "Aluguel", "Parcela taxa contratual",
                               "Total do mes", "Total acumulado"])
            for l in self.projecao():
                escritor.writerow([l.mes, l.referencia, numero(l.aluguel), numero(l.parcela_taxa),
                                   numero(l.total_mes), numero(l.acumulado)])
            projecao = self.projecao()
            escritor.writerow(["TOTAL", "", numero(sum(l.aluguel for l in projecao)),
                               numero(TaxaContratual.VALOR), numero(self.total_previsto()), ""])
        return caminho
