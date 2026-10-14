"""Interface gráfica do RentSmart, feita com tkinter (já vem com o Python).

A janela só coleta as escolhas e mostra os resultados. Todas as contas
continuam nas classes de imoveis.py e orcamento.py.
"""

from __future__ import annotations

import os
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from imoveis import Apartamento, Casa, Estudio, Imovel
from orcamento import MESES_ABREV, Cliente, Orcamento, TaxaContratual, moeda

PASTA_SAIDA = os.path.dirname(os.path.abspath(__file__))
FONTE = "Segoe UI"
VAGAS_MAX = 10

COR = {
    "fundo": "#F4F1EA",
    "cartao": "#FFFFFF",
    "borda": "#E2DCCF",
    "tinta": "#1F2A2E",
    "suave": "#6B7570",
    "primaria": "#14453D",
    "primaria_clara": "#E3EEEA",
    "destaque": "#E9A23B",
    "destaque_claro": "#FDF3E1",
    "erro": "#B23A3A",
}

# código -> (nome, ícone, classe)
TIPOS = {
    "A": ("Apartamento", "▦", Apartamento),
    "C": ("Casa", "⌂", Casa),
    "E": ("Estúdio", "◩", Estudio),
}
CAMPOS_POR_TIPO = {"A": ("quartos", "garagem", "criancas"), "C": ("quartos", "garagem"), "E": ("vagas",)}


class AppRentSmart(tk.Tk):
    """Janela principal: formulário à esquerda, orçamento ao vivo à direita."""

    def __init__(self):
        super().__init__()
        self.title("RentSmart — R.M Imóveis")
        self.minsize(1000, 640)
        try:
            self.state("zoomed")  # abre maximizada no Windows
        except tk.TclError:
            self.geometry("1200x780")
        self.configure(bg=COR["fundo"])

        hoje = date.today()
        self.tipo = tk.StringVar(value="A")
        self.nome = tk.StringVar()
        self.quartos = tk.IntVar(value=1)
        self.garagem = tk.BooleanVar(value=False)
        self.criancas = tk.BooleanVar(value=True)
        self.vagas = tk.IntVar(value=0)
        self.parcelas = tk.IntVar(value=1)
        self.mes_inicio = tk.StringVar(value=MESES_ABREV[hoje.month % 12])  # próximo mês
        self.ano_inicio = tk.StringVar(value=str(hoje.year + (hoje.month == 12)))

        self._estilos()
        self._cabecalho()
        corpo = tk.Frame(self, bg=COR["fundo"])
        corpo.pack(fill="both", expand=True, padx=28, pady=(18, 24))
        corpo.columnconfigure(0, weight=5, uniform="coluna")
        corpo.columnconfigure(1, weight=6, uniform="coluna")
        corpo.rowconfigure(0, weight=1)
        self._painel_formulario(corpo).grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._painel_resultado(corpo).grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        # Qualquer mudança no formulário recalcula o orçamento na hora.
        for var in (self.tipo, self.nome, self.quartos, self.garagem, self.criancas,
                    self.vagas, self.parcelas, self.mes_inicio, self.ano_inicio):
            var.trace_add("write", lambda *_: self._atualizar())
        self._atualizar()
        self.entrada_nome.focus_set()

    # ---------------- Aparência ----------------

    def _estilos(self) -> None:
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("Treeview", font=(FONTE, 10), rowheight=25, background=COR["cartao"],
                         fieldbackground=COR["cartao"], foreground=COR["tinta"], borderwidth=0)
        estilo.configure("Treeview.Heading", font=(FONTE, 9, "bold"), background=COR["primaria"],
                         foreground="white", relief="flat", padding=6)
        estilo.map("Treeview.Heading", background=[("active", COR["primaria"])])
        estilo.map("Treeview", background=[("selected", COR["primaria_clara"])],
                   foreground=[("selected", COR["tinta"])])
        estilo.configure("TCombobox", padding=5, arrowsize=14)

    def _cabecalho(self) -> None:
        barra = tk.Frame(self, bg=COR["primaria"])
        barra.pack(fill="x")
        tk.Frame(barra, bg=COR["destaque"], height=4).pack(side="bottom", fill="x")
        tk.Label(barra, text="RentSmart", font=(FONTE, 22, "bold"), fg="white",
                 bg=COR["primaria"]).pack(side="left", padx=(28, 12), pady=14)
        tk.Label(barra, text="Orçamento de locação  ·  R.M Imóveis", font=(FONTE, 11),
                 fg=COR["destaque"], bg=COR["primaria"]).pack(side="left", pady=(10, 0))
        tk.Label(barra, text=date.today().strftime("%d/%m/%Y"), font=(FONTE, 10),
                 fg="white", bg=COR["primaria"]).pack(side="right", padx=28)

    def _cartao(self, pai: tk.Widget, titulo: str) -> tk.Frame:
        cartao = tk.Frame(pai, bg=COR["cartao"], highlightbackground=COR["borda"], highlightthickness=1)
        tk.Label(cartao, text=titulo.upper(), font=(FONTE, 9, "bold"), fg=COR["suave"],
                 bg=COR["cartao"]).pack(anchor="w", padx=20, pady=(14, 2))
        return cartao

    def _linha(self, pai: tk.Widget, rotulo: str, dica: str = "") -> tuple[tk.Frame, tk.Label]:
        """Bloco com rótulo + dica; o controle é colocado logo abaixo."""
        linha = tk.Frame(pai, bg=COR["cartao"])
        topo = tk.Frame(linha, bg=COR["cartao"])
        topo.pack(fill="x")
        tk.Label(topo, text=rotulo, font=(FONTE, 10, "bold"), fg=COR["tinta"],
                 bg=COR["cartao"]).pack(side="left")
        lbl_dica = tk.Label(topo, text=dica, font=(FONTE, 9), fg=COR["suave"], bg=COR["cartao"])
        lbl_dica.pack(side="left", padx=8)
        return linha, lbl_dica

    def _segmentado(self, pai: tk.Widget, var: tk.Variable, opcoes: list) -> tk.Frame:
        """Grupo de botões em que só um fica marcado (ex.: 1 ou 2 quartos)."""
        grupo = tk.Frame(pai, bg=COR["cartao"])
        botoes = []
        for valor, texto in opcoes:
            botao = tk.Label(grupo, text=texto, font=(FONTE, 10, "bold"), padx=16, pady=6,
                             cursor="hand2", highlightthickness=1)
            botao.bind("<Button-1>", lambda _e, v=valor: var.set(v))
            botao.pack(side="left", padx=(0, 6))
            botoes.append((valor, botao))

        def pintar(*_):
            for valor, botao in botoes:
                ativo = var.get() == valor
                botao.configure(bg=COR["primaria"] if ativo else COR["primaria_clara"],
                                fg="white" if ativo else COR["primaria"],
                                highlightbackground=COR["primaria"] if ativo else COR["borda"])

        var.trace_add("write", pintar)
        pintar()
        return grupo

    def _botao(self, pai: tk.Widget, texto: str, comando, principal: bool = True) -> tk.Label:
        fundo = COR["destaque"] if principal else COR["cartao"]
        botao = tk.Label(pai, text=texto, font=(FONTE, 11, "bold"), bg=fundo, fg=COR["tinta"],
                         padx=22, pady=10, cursor="hand2", highlightthickness=1,
                         highlightbackground=COR["destaque"] if principal else COR["borda"])
        botao.bind("<Button-1>", lambda _e: comando())
        return botao

    # ---------------- Formulário (esquerda) ----------------

    def _painel_formulario(self, pai: tk.Widget) -> tk.Frame:
        cartao = self._cartao(pai, "Dados da locação")
        pad = {"fill": "x", "padx": 20, "pady": (10, 0)}

        linha, _ = self._linha(cartao, "Cliente")
        self.entrada_nome = tk.Entry(linha, textvariable=self.nome, font=(FONTE, 11), relief="flat",
                                     bg=COR["fundo"], fg=COR["tinta"], insertbackground=COR["tinta"],
                                     highlightthickness=1, highlightbackground=COR["borda"],
                                     highlightcolor=COR["primaria"])
        self.entrada_nome.pack(fill="x", pady=(4, 0), ipady=6)
        linha.pack(**pad)

        linha, _ = self._linha(cartao, "Início do contrato")
        datas = tk.Frame(linha, bg=COR["cartao"])
        datas.pack(anchor="w", pady=(4, 0))
        ano = date.today().year
        ttk.Combobox(datas, textvariable=self.mes_inicio, values=MESES_ABREV, width=6,
                     state="readonly", font=(FONTE, 10)).pack(side="left")
        ttk.Combobox(datas, textvariable=self.ano_inicio, values=[str(a) for a in range(ano, ano + 3)],
                     width=7, state="readonly", font=(FONTE, 10)).pack(side="left", padx=8)
        linha.pack(**pad)

        linha, _ = self._linha(cartao, "Tipo de imóvel")
        self._cartoes_tipo(linha).pack(fill="x", pady=(6, 0))
        linha.pack(**pad)

        # Campos que mudam conforme o tipo escolhido
        area = tk.Frame(cartao, bg=COR["cartao"])
        area.pack(fill="x")
        self.campos: dict[str, tk.Frame] = {}

        self.campos["quartos"], self.dica_quartos = self._linha(area, "Quartos")
        self._segmentado(self.campos["quartos"], self.quartos,
                         [(1, "1 quarto"), (2, "2 quartos")]).pack(anchor="w", pady=(4, 0))

        self.campos["garagem"], _ = self._linha(area, "Vaga de garagem", "+ R$ 300,00 por mês")
        self._segmentado(self.campos["garagem"], self.garagem,
                         [(False, "Não"), (True, "Sim")]).pack(anchor="w", pady=(4, 0))

        self.campos["criancas"], _ = self._linha(area, "Possui crianças?", "sem crianças = 5% de desconto")
        self._segmentado(self.campos["criancas"], self.criancas,
                         [(True, "Sim"), (False, "Não")]).pack(anchor="w", pady=(4, 0))

        self.campos["vagas"], _ = self._linha(area, "Estacionamento",
                                              "pacote 2 vagas R$ 250,00 + R$ 60,00 por extra")
        self._seletor_vagas(self.campos["vagas"]).pack(anchor="w", pady=(4, 0))

        linha, _ = self._linha(cartao, "Taxa contratual", "R$ 2.000,00 — parcelas")
        self._segmentado(linha, self.parcelas,
                         [(n, f"{n}x") for n in range(1, TaxaContratual.MAX_PARCELAS + 1)]
                         ).pack(anchor="w", pady=(4, 0))
        linha.pack(**pad)

        self.lbl_erro = tk.Label(cartao, text="", font=(FONTE, 10, "bold"), fg=COR["erro"],
                                 bg=COR["cartao"], anchor="w")
        self.lbl_erro.pack(fill="x", padx=20, pady=(10, 14))
        return cartao

    def _cartoes_tipo(self, pai: tk.Widget) -> tk.Frame:
        """Três cartões clicáveis: Apartamento, Casa e Estúdio."""
        grupo = tk.Frame(pai, bg=COR["cartao"])
        cartoes = {}
        for coluna, (codigo, (nome, icone, classe)) in enumerate(TIPOS.items()):
            grupo.columnconfigure(coluna, weight=1, uniform="tipo")
            cartao = tk.Frame(grupo, highlightthickness=2, cursor="hand2")
            cartao.grid(row=0, column=coluna, sticky="nsew", padx=(0 if coluna == 0 else 8, 0))
            rotulos = [
                tk.Label(cartao, text=icone, font=(FONTE, 20)),
                tk.Label(cartao, text=nome, font=(FONTE, 11, "bold")),
                tk.Label(cartao, text=f"base {moeda(classe.aluguel_base)}", font=(FONTE, 9)),
            ]
            for rotulo, espaco in zip(rotulos, [(8, 0), 0, (0, 10)]):
                rotulo.pack(pady=espaco)
            for widget in [cartao] + rotulos:
                widget.bind("<Button-1>", lambda _e, k=codigo: self.tipo.set(k))
            cartoes[codigo] = (cartao, rotulos)

        def pintar(*_):
            for codigo, (cartao, rotulos) in cartoes.items():
                ativo = self.tipo.get() == codigo
                fundo = COR["primaria_clara"] if ativo else COR["cartao"]
                cartao.configure(bg=fundo, highlightbackground=COR["primaria"] if ativo else COR["borda"])
                for rotulo in rotulos:
                    rotulo.configure(bg=fundo, fg=COR["primaria"] if ativo else COR["tinta"])

        self.tipo.trace_add("write", pintar)
        pintar()
        return grupo

    def _seletor_vagas(self, pai: tk.Widget) -> tk.Frame:
        """Botões − e + que pulam de 0 direto para 2 (não existe 1 vaga)."""
        grupo = tk.Frame(pai, bg=COR["cartao"])

        def menos():
            v = self.vagas.get()
            self.vagas.set(0 if v <= 2 else v - 1)

        def mais():
            v = self.vagas.get()
            self.vagas.set(2 if v == 0 else min(v + 1, VAGAS_MAX))

        for texto, acao, lado in (("−", menos, "left"), ("+", mais, "right")):
            botao = tk.Label(grupo, text=texto, font=(FONTE, 13, "bold"), width=3, cursor="hand2",
                             bg=COR["primaria"], fg="white")
            botao.bind("<Button-1>", lambda _e, a=acao: a())
            botao.pack(side=lado)
        valor = tk.Label(grupo, font=(FONTE, 11, "bold"), width=18, bg=COR["primaria_clara"],
                         fg=COR["primaria"], pady=4)
        valor.pack(side="left")

        def mostrar(*_):
            v = self.vagas.get()
            valor.configure(text="Sem estacionamento" if v == 0 else f"{v} vagas")

        self.vagas.trace_add("write", mostrar)
        mostrar()
        return grupo

    # ---------------- Resultado (direita) ----------------

    def _painel_resultado(self, pai: tk.Widget) -> tk.Frame:
        coluna = tk.Frame(pai, bg=COR["fundo"])

        recibo = self._cartao(coluna, "Resumo do orçamento")
        recibo.pack(fill="x")
        self.lbl_descricao = tk.Label(recibo, font=(FONTE, 10), fg=COR["suave"], bg=COR["cartao"],
                                      anchor="w", justify="left")
        self.lbl_descricao.pack(fill="x", padx=20)
        self.area_itens = tk.Frame(recibo, bg=COR["cartao"])
        self.area_itens.pack(fill="x", padx=20, pady=(8, 0))
        tk.Frame(recibo, bg=COR["borda"], height=1).pack(fill="x", padx=20, pady=8)

        total = tk.Frame(recibo, bg=COR["cartao"])
        total.pack(fill="x", padx=20)
        tk.Label(total, text="Aluguel mensal", font=(FONTE, 12, "bold"), fg=COR["tinta"],
                 bg=COR["cartao"]).pack(side="left")
        self.lbl_aluguel = tk.Label(total, font=(FONTE, 24, "bold"), fg=COR["primaria"], bg=COR["cartao"])
        self.lbl_aluguel.pack(side="right")

        taxa = tk.Frame(recibo, bg=COR["destaque_claro"])
        taxa.pack(fill="x", padx=20, pady=(8, 16))
        tk.Label(taxa, text="TAXA CONTRATUAL · cobrada à parte do aluguel", font=(FONTE, 8, "bold"),
                 fg=COR["suave"], bg=COR["destaque_claro"]).pack(anchor="w", padx=12, pady=(8, 0))
        self.lbl_taxa = tk.Label(taxa, font=(FONTE, 11, "bold"), fg=COR["tinta"], bg=COR["destaque_claro"])
        self.lbl_taxa.pack(anchor="w", padx=12, pady=(0, 8))

        tabela = self._cartao(coluna, "Projeção dos 12 meses")
        tabela.pack(fill="both", expand=True, pady=(16, 0))
        colunas = ("referencia", "aluguel", "taxa", "total", "acumulado")
        self.tabela = ttk.Treeview(tabela, columns=colunas, show="headings", height=8, selectmode="none")
        for chave, titulo in zip(colunas, ("Mês", "Aluguel", "Taxa", "Total do mês", "Acumulado")):
            self.tabela.heading(chave, text=titulo)
            self.tabela.column(chave, anchor="center" if chave == "referencia" else "e", width=100)
        self.tabela.tag_configure("com_taxa", background=COR["destaque_claro"])
        # O rodapé é fixado embaixo primeiro, para nunca ser empurrado para fora da tela.
        rodape = tk.Frame(tabela, bg=COR["cartao"])
        rodape.pack(side="bottom", fill="x", padx=20, pady=12)
        self.tabela.pack(fill="both", expand=True, padx=20, pady=(6, 0))
        self.lbl_total_ano = tk.Label(rodape, font=(FONTE, 11, "bold"), fg=COR["tinta"], bg=COR["cartao"])
        self.lbl_total_ano.pack(side="left")
        self._botao(rodape, "Gerar CSV", self._gerar_csv).pack(side="right")
        self._botao(rodape, "Novo orçamento", self._novo, principal=False).pack(side="right", padx=8)
        return coluna

    # ---------------- Lógica da tela ----------------

    def _criar_imovel(self) -> Imovel:
        """Cria o objeto certo; daqui em diante o resto do código não precisa saber qual é."""
        tipo = self.tipo.get()
        if tipo == "E":
            return Estudio(self.vagas.get())
        if tipo == "A":
            return Apartamento(self.quartos.get(), self.garagem.get(), self.criancas.get())
        return Casa(self.quartos.get(), self.garagem.get())

    def _montar_orcamento(self, nome: str) -> Orcamento:
        inicio = date(int(self.ano_inicio.get()), MESES_ABREV.index(self.mes_inicio.get()) + 1, 1)
        return Orcamento(Cliente(nome), self._criar_imovel(), TaxaContratual(self.parcelas.get()), inicio)

    def _mostrar_campos(self) -> None:
        tipo = self.tipo.get()
        for campo in self.campos.values():
            campo.pack_forget()
        for nome in CAMPOS_POR_TIPO[tipo]:
            self.campos[nome].pack(fill="x", padx=20, pady=(10, 0))
        if tipo != "E":
            adicional = TIPOS[tipo][2].adicional_dois_quartos
            self.dica_quartos.configure(text=f"2 quartos: + {moeda(adicional)} por mês")

    def _atualizar(self) -> None:
        self._mostrar_campos()
        try:
            orcamento = self._montar_orcamento(self.nome.get().strip() or "Cliente")
        except ValueError as erro:
            self.lbl_erro.configure(text=f"⚠ {erro}")
            return
        self.lbl_erro.configure(text="")
        self._exibir(orcamento)

    def _exibir(self, orcamento: Orcamento) -> None:
        nome = self.nome.get().strip() or "Cliente não informado"
        self.lbl_descricao.configure(text=f"{nome}  ·  início {orcamento.referencia_do_mes(1)}\n"
                                          f"{orcamento.imovel}")

        for filho in self.area_itens.winfo_children():
            filho.destroy()
        for item in orcamento.imovel.detalhamento():
            linha = tk.Frame(self.area_itens, bg=COR["cartao"])
            linha.pack(fill="x", pady=1)
            cor = COR["primaria"] if item.valor < 0 else COR["tinta"]
            tk.Label(linha, text=item.descricao, font=(FONTE, 10), fg=cor, bg=COR["cartao"]).pack(side="left")
            tk.Label(linha, text=moeda(item.valor), font=(FONTE, 10), fg=cor, bg=COR["cartao"]).pack(side="right")

        self.lbl_aluguel.configure(text=moeda(orcamento.imovel.aluguel_mensal()))
        self.lbl_taxa.configure(text=f"{moeda(TaxaContratual.VALOR)}  →  {orcamento.taxa.descricao()}")

        self.tabela.delete(*self.tabela.get_children())
        for l in orcamento.projecao():
            self.tabela.insert("", "end", tags=("com_taxa",) if l.parcela_taxa else (), values=(
                l.referencia, moeda(l.aluguel), moeda(l.parcela_taxa) if l.parcela_taxa else "—",
                moeda(l.total_mes), moeda(l.acumulado)))
        self.lbl_total_ano.configure(text=f"Total no 1º ano: {moeda(orcamento.total_previsto())}")

    def _gerar_csv(self) -> None:
        try:
            orcamento = self._montar_orcamento(self.nome.get())
        except ValueError as erro:
            messagebox.showwarning("Dados incompletos", str(erro))
            self.entrada_nome.focus_set()
            return

        confirmacao = (f"Cliente: {orcamento.cliente.nome}\n"
                       f"Imóvel: {orcamento.imovel}\n"
                       f"Início: {orcamento.referencia_do_mes(1)}\n\n"
                       f"Aluguel mensal: {moeda(orcamento.imovel.aluguel_mensal())}\n"
                       f"Taxa contratual: {orcamento.taxa.descricao()}\n"
                       f"Total no 1º ano: {moeda(orcamento.total_previsto())}\n\n"
                       "Os dados estão corretos? Gerar o arquivo CSV?")
        if not messagebox.askyesno("Confirmar orçamento", confirmacao):
            return

        caminho = orcamento.gerar_csv(PASTA_SAIDA)
        if messagebox.askyesno("CSV gerado", f"Arquivo salvo em:\n{caminho}\n\nDeseja abrir agora?") \
                and hasattr(os, "startfile"):
            os.startfile(caminho)

    def _novo(self) -> None:
        self.nome.set("")
        self.tipo.set("A")
        self.quartos.set(1)
        self.garagem.set(False)
        self.criancas.set(True)
        self.vagas.set(0)
        self.parcelas.set(1)
        self.entrada_nome.focus_set()
