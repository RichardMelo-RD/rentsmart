# RentSmart — Orçamento de Locação (R.M Imóveis)

Aplicação em Python, orientada a objetos, que calcula o aluguel mensal de casas, apartamentos e estúdios, mostra a taxa contratual **separada** do aluguel e gera a projeção dos 12 primeiros meses em CSV.

O sistema tem **interface gráfica** (janela com botões, orçamento atualizado em tempo real) e também um **modo terminal**.

## Requisitos
- Python 3.8 ou superior
- Nenhuma biblioteca externa (a interface usa `tkinter`, que já vem com o Python)

## Como executar
```bash
git clone https://github.com/RichardMelo-RD/rentsmart.git
cd rentsmart
python main.py
```

| Comando | O que faz |
|---|---|
| `python main.py` | Abre a janela do RentSmart |
| `python main_terminal.py` | Versão sem janela: atendimento por perguntas no terminal |
| `python -m unittest -v` | Roda os 20 testes automáticos das regras |

Na janela: preencha o cliente, o mês de início, o tipo de imóvel e as opções. O orçamento e a projeção aparecem na hora. Clique em **Gerar CSV** para confirmar e salvar o arquivo `orcamento_<nome_do_cliente>.csv`.

## Estrutura
| Arquivo | Conteúdo |
|---|---|
| `main.py` | Versão com janela: abre a interface gráfica |
| `main_terminal.py` | Versão sem janela: perguntas no terminal com validação das entradas |
| `interface.py` | Interface gráfica (`AppRentSmart`) — só coleta dados e exibe resultados |
| `imoveis.py` | `Imovel` (abstrata), `ImovelResidencial`, `Apartamento`, `Casa`, `Estudio` |
| `orcamento.py` | `Cliente`, `TaxaContratual`, `LinhaProjecao` e `Orcamento` (resumo e CSV) |
| `test_rentsmart.py` | Testes automáticos de todas as regras de negócio |
| `orcamento_cliente_exemplo.csv` | Exemplo de arquivo gerado |

```
Imovel (abstrata)
├── ImovelResidencial      quartos + garagem (R$ 300)
│   ├── Apartamento        base R$ 700, 2 quartos +R$ 200, -5% sem crianças
│   └── Casa               base R$ 900, 2 quartos +R$ 250
└── Estudio                base R$ 1.200, 2 vagas R$ 250 + R$ 60 por extra
```

## Conceitos de POO aplicados
- **Abstração:** `Imovel` é abstrata (`ABC`) — não dá para criar um "imóvel genérico".
- **Herança:** a regra da garagem está escrita uma vez só, em `ImovelResidencial`.
- **Polimorfismo:** `Orcamento` chama `imovel.aluguel_mensal()` sem saber qual é o tipo.
- **Encapsulamento:** `quartos`, `vagas` e `nome` são validados por `@property`; o objeto nunca fica inválido.

## Regras implementadas
- Aluguel-base: apartamento R$ 700, casa R$ 900, estúdio R$ 1.200
- 2 quartos: +R$ 200 (apartamento) / +R$ 250 (casa)
- Garagem (casa/apartamento): +R$ 300
- Estúdio: pacote de 2 vagas R$ 250 + R$ 60 por vaga adicional (não existe 1 vaga)
- Apartamento sem crianças: 5% de desconto **após** os adicionais
- Taxa contratual R$ 2.000 em 1 a 5 parcelas, exibida separada do aluguel (centavos ajustados na última parcela)

## Exemplo
Apartamento, 2 quartos, garagem, sem crianças, taxa em 4x, início Nov/2026:
aluguel de **R$ 1.140,00** (700 + 200 + 300 − 5%) + 4 parcelas de R$ 500,00 → **R$ 15.680,00** no primeiro ano.
