"""Testes automáticos das regras da R.M Imóveis.  Rodar com:  python -m unittest -v"""

import csv
import os
import tempfile
import unittest
from datetime import date

from imoveis import Apartamento, Casa, Estudio, Imovel
from orcamento import Cliente, Orcamento, TaxaContratual


class TestApartamento(unittest.TestCase):
    def test_um_quarto_com_criancas_paga_so_a_base(self):
        self.assertEqual(Apartamento(1, False, True).aluguel_mensal(), 700.00)

    def test_dois_quartos_garagem_sem_criancas(self):
        # (700 + 200 + 300) = 1.200 -> 5% de desconto = 1.140
        self.assertEqual(Apartamento(2, True, False).aluguel_mensal(), 1140.00)

    def test_desconto_aplicado_depois_dos_adicionais(self):
        desconto = Apartamento(2, True, False).detalhamento()[-1]
        self.assertEqual(desconto.valor, -60.00)


class TestCasa(unittest.TestCase):
    def test_um_quarto(self):
        self.assertEqual(Casa(1, False).aluguel_mensal(), 900.00)

    def test_dois_quartos_com_garagem(self):
        self.assertEqual(Casa(2, True).aluguel_mensal(), 1450.00)  # 900 + 250 + 300


class TestEstudio(unittest.TestCase):
    def test_sem_vagas(self):
        self.assertEqual(Estudio(0).aluguel_mensal(), 1200.00)

    def test_pacote_duas_vagas(self):
        self.assertEqual(Estudio(2).aluguel_mensal(), 1450.00)

    def test_vagas_extras(self):
        self.assertEqual(Estudio(5).aluguel_mensal(), 1630.00)  # 1200 + 250 + 3 x 60

    def test_uma_vaga_e_invalida(self):
        with self.assertRaises(ValueError):
            Estudio(1)


class TestRegrasDeObjeto(unittest.TestCase):
    def test_imovel_abstrato_nao_pode_ser_criado(self):
        with self.assertRaises(TypeError):
            Imovel()

    def test_quartos_invalidos(self):
        with self.assertRaises(ValueError):
            Casa(3, False)

    def test_encapsulamento_valida_alteracao_posterior(self):
        casa = Casa(1, False)
        with self.assertRaises(ValueError):
            casa.quartos = 5

    def test_cliente_sem_nome(self):
        with self.assertRaises(ValueError):
            Cliente("   ")

    def test_nome_de_arquivo_sem_acentos(self):
        self.assertEqual(Cliente("João da Silva").nome_arquivo(), "joao_da_silva")


class TestTaxaContratual(unittest.TestCase):
    def test_parcelas_somam_dois_mil(self):
        for n in range(1, 6):
            taxa = TaxaContratual(n)
            self.assertAlmostEqual(sum(taxa.parcela_do_mes(m) for m in range(1, 13)), 2000.00)

    def test_mais_de_cinco_parcelas_e_invalido(self):
        with self.assertRaises(ValueError):
            TaxaContratual(6)


class TestOrcamento(unittest.TestCase):
    def setUp(self):
        self.orcamento = Orcamento(Cliente("Maria Teste"), Apartamento(2, True, False),
                                   TaxaContratual(4), date(2026, 11, 1))

    def test_taxa_so_nos_primeiros_meses(self):
        parcelas = [l.parcela_taxa for l in self.orcamento.projecao()]
        self.assertEqual(parcelas, [500.0] * 4 + [0.0] * 8)

    def test_total_do_ano(self):
        self.assertEqual(self.orcamento.total_previsto(), 12 * 1140 + 2000)

    def test_meses_viram_o_ano(self):
        self.assertEqual(self.orcamento.referencia_do_mes(1), "Nov/2026")
        self.assertEqual(self.orcamento.referencia_do_mes(3), "Jan/2027")

    def test_csv_tem_cabecalho_12_meses_e_total(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = self.orcamento.gerar_csv(pasta)
            self.assertTrue(os.path.basename(caminho) == "orcamento_maria_teste.csv")
            with open(caminho, encoding="utf-8-sig") as arquivo:
                linhas = list(csv.reader(arquivo, delimiter=";"))
        self.assertEqual(len(linhas), 14)
        self.assertEqual(linhas[-1][0], "TOTAL")


if __name__ == "__main__":
    unittest.main()
