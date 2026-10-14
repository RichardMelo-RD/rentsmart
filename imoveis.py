"""Tipos de imóvel da R.M Imóveis.

Hierarquia de classes:

    Imovel (abstrata)           -> molde geral: aluguel-base e soma dos itens
    ├── ImovelResidencial       -> regra comum de quartos e garagem
    │   ├── Apartamento         -> + desconto de 5% para quem não tem crianças
    │   └── Casa
    └── Estudio                 -> regra própria de vagas de estacionamento

Cada imóvel sabe calcular o próprio aluguel e listar os itens que o compõem.
A classe base concentra o que é comum; as subclasses só implementam suas regras.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import NamedTuple, Optional


class Item(NamedTuple):
    """Uma linha do orçamento: descrição e valor (valor negativo = desconto)."""

    descricao: str
    valor: float


class Imovel(ABC):
    """Classe abstrata: não existe "imóvel genérico", só os tipos concretos."""

    tipo = "Imóvel"
    aluguel_base = 0.0

    @abstractmethod
    def itens_adicionais(self) -> list[Item]:
        """Adicionais cobrados por mês. Cada subclasse define os seus."""

    @abstractmethod
    def caracteristicas(self) -> list[str]:
        """Descrição curta das escolhas do cliente (usada no __str__)."""

    def desconto(self, subtotal: float) -> Optional[Item]:
        """Desconto sobre o subtotal. Padrão: nenhum."""
        return None

    def detalhamento(self) -> list[Item]:
        """Lista completa: aluguel-base, adicionais e desconto, nessa ordem."""
        itens = [Item(f"Aluguel-base ({self.tipo})", self.aluguel_base)]
        itens += self.itens_adicionais()
        desconto = self.desconto(sum(item.valor for item in itens))
        if desconto:
            itens.append(desconto)
        return itens

    def aluguel_mensal(self) -> float:
        return round(sum(item.valor for item in self.detalhamento()), 2)

    def __str__(self) -> str:
        return " · ".join([self.tipo] + self.caracteristicas())


class ImovelResidencial(Imovel):
    """Casa e apartamento compartilham a regra de quartos e de garagem."""

    ADICIONAL_GARAGEM = 300.0
    adicional_dois_quartos = 0.0

    def __init__(self, quartos: int, garagem: bool):
        self.quartos = quartos  # passa pela validação do setter abaixo
        self.garagem = garagem

    @property
    def quartos(self) -> int:
        return self._quartos

    @quartos.setter
    def quartos(self, valor: int) -> None:
        if valor not in (1, 2):
            raise ValueError("O número de quartos deve ser 1 ou 2.")
        self._quartos = valor

    def itens_adicionais(self) -> list[Item]:
        itens = []
        if self.quartos == 2:
            itens.append(Item("Adicional 2 quartos", self.adicional_dois_quartos))
        if self.garagem:
            itens.append(Item("Vaga de garagem", self.ADICIONAL_GARAGEM))
        return itens

    def caracteristicas(self) -> list[str]:
        return [f"{self.quartos} quarto(s)", "com garagem" if self.garagem else "sem garagem"]


class Apartamento(ImovelResidencial):
    tipo = "Apartamento"
    aluguel_base = 700.0
    adicional_dois_quartos = 200.0
    PERCENTUAL_DESCONTO = 0.05

    def __init__(self, quartos: int, garagem: bool, tem_criancas: bool):
        super().__init__(quartos, garagem)
        self.tem_criancas = tem_criancas

    def desconto(self, subtotal: float) -> Optional[Item]:
        # Desconto de 5% aplicado depois dos adicionais, só para quem não tem crianças.
        if self.tem_criancas:
            return None
        return Item("Desconto 5% (sem crianças)", -round(subtotal * self.PERCENTUAL_DESCONTO, 2))

    def caracteristicas(self) -> list[str]:
        return super().caracteristicas() + ["com crianças" if self.tem_criancas else "sem crianças"]


class Casa(ImovelResidencial):
    tipo = "Casa"
    aluguel_base = 900.0
    adicional_dois_quartos = 250.0


class Estudio(Imovel):
    tipo = "Estúdio"
    aluguel_base = 1200.0
    PACOTE_DUAS_VAGAS = 250.0
    VAGA_EXTRA = 60.0

    def __init__(self, vagas: int):
        self.vagas = vagas  # passa pela validação do setter abaixo

    @property
    def vagas(self) -> int:
        return self._vagas

    @vagas.setter
    def vagas(self, valor: int) -> None:
        if valor < 0:
            raise ValueError("O número de vagas não pode ser negativo.")
        if valor == 1:
            raise ValueError("Estúdios têm pacote mínimo de 2 vagas (ou nenhuma).")
        self._vagas = valor

    def itens_adicionais(self) -> list[Item]:
        if self.vagas == 0:
            return []
        itens = [Item("Pacote 2 vagas de estacionamento", self.PACOTE_DUAS_VAGAS)]
        extras = self.vagas - 2
        if extras > 0:
            itens.append(Item(f"{extras} vaga(s) extra(s) x R$ 60,00", extras * self.VAGA_EXTRA))
        return itens

    def caracteristicas(self) -> list[str]:
        return ["sem estacionamento" if self.vagas == 0 else f"{self.vagas} vagas"]
