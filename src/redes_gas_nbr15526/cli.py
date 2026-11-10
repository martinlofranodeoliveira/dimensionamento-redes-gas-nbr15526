"""Interface de Linha de Comando (CLI) para dimensionamento de redes internas de gás.

Conforme o padrão LOFRANO TECNOLOGIA:
- 100% em português brasileiro (pt-BR)
- Comandos: calcular, catalogo, gerar-exemplo
- Suporte a saídas em texto, JSON, CSV, SVG e pacotes determinísticos ZIP
"""

import argparse
import sys
from typing import Sequence

from .calculator import dimensionar_rede_gas
from .codecs import carregar_entrada_json, exportar_resultado_json
from .constants import (
    APARELHOS_PADRAO,
    CATALOGO_TUBULACOES,
    GASES_COMBUSTIVEIS,
)
from .exporters import (
    gerar_csv_sanitizado,
    gerar_pacote_zip_deterministico,
    gerar_relatorio_texto,
)
from .svg_generator import gerar_painel_svg

VERSAO = "1.0.0"


def criar_parser() -> argparse.ArgumentParser:
    """Configura e retorna o analisador de argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        prog="redes-gas",
        description="Dimensionamento analítico de redes de distribuição interna de gases combustíveis (ABNT NBR 15526).",
        add_help=False,
    )
    parser.add_argument(
        "-h",
        "--help",
        "--ajuda",
        action="help",
        help="Exibe esta mensagem de ajuda e encerra.",
    )
    parser.add_argument(
        "-v",
        "--versao",
        "--version",
        action="version",
        version=f"%(prog)s {VERSAO}",
        help="Exibe a versão do software e encerra.",
    )

    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    # Subcomando: calcular
    parser_calc = subparsers.add_parser(
        "calcular",
        help="Calcula o dimensionamento da rede a partir de arquivo JSON canônico.",
        add_help=False,
    )
    parser_calc.add_argument(
        "-h", "--help", "--ajuda", action="help", help="Ajuda do comando calcular."
    )
    parser_calc.add_argument(
        "arquivo_entrada",
        help="Caminho do arquivo JSON canônico com dados do gás, aparelhos e trechos.",
    )
    parser_calc.add_argument(
        "-f",
        "--formato",
        choices=["texto", "json", "csv", "svg", "zip"],
        default="texto",
        help="Formato da saída gerada (padrão: texto).",
    )
    parser_calc.add_argument(
        "-o",
        "--saida",
        help="Caminho do arquivo de saída (opcional para texto/json; obrigatório para zip/svg se especificado).",
    )

    # Subcomando: catalogo
    parser_cat = subparsers.add_parser(
        "catalogo",
        help="Lista o catálogo de gases, aparelhos e tubulações da ABNT NBR 15526.",
        add_help=False,
    )
    parser_cat.add_argument(
        "-h", "--help", "--ajuda", action="help", help="Ajuda do comando catalogo."
    )
    parser_cat.add_argument(
        "--tipo",
        choices=["todos", "gases", "aparelhos", "tubulacoes"],
        default="todos",
        help="Categoria do catálogo a exibir (padrão: todos).",
    )

    # Subcomando: gerar-exemplo
    parser_ex = subparsers.add_parser(
        "gerar-exemplo",
        help="Gera arquivo JSON de exemplo pronto para cálculo.",
        add_help=False,
    )
    parser_ex.add_argument(
        "-h", "--help", "--ajuda", action="help", help="Ajuda do comando gerar-exemplo."
    )
    parser_ex.add_argument(
        "--tipo",
        choices=["gn_residencial", "glp_comercial"],
        default="gn_residencial",
        help="Tipo de instalação de exemplo (padrão: gn_residencial).",
    )
    parser_ex.add_argument(
        "-o",
        "--saida",
        help="Caminho do arquivo de saída (imprime na tela se omitido).",
    )

    return parser


def cmd_catalogo(tipo: str) -> int:
    """Exibe catálogo normativo formatado."""
    if tipo in ["todos", "gases"]:
        print("=" * 80)
        print("   GASES COMBUSTÍVEIS E PROPRIEDADES FÍSICAS (ABNT NBR 15526)")
        print("=" * 80)
        print(f"{'Sigla':<6} | {'Nome':<30} | {'Dens. Rel.':<10} | {'PCS (kcal/m³)':<14} | {'P_nom (mmca)'}")
        print("-" * 80)
        for s, g in sorted(GASES_COMBUSTIVEIS.items()):
            print(f"{s:<6} | {str(g['nome']):<30} | {str(g['densidade_relativa_ar']):<10} | {str(g['pcs_kcal_m3']):<14} | {str(g['pressao_nominal_baixa_mmca'])}")
        print()

    if tipo in ["todos", "aparelhos"]:
        print("=" * 80)
        print("   APARELHOS DE CONSUMO PADRONIZADOS E POTÊNCIAS NOMINAIS")
        print("=" * 80)
        print(f"{'Código':<26} | {'Descrição':<36} | {'Potência (kW)':<12}")
        print("-" * 80)
        for c, a in sorted(APARELHOS_PADRAO.items()):
            print(f"{c:<26} | {str(a['descricao']):<36} | {str(a['potencia_kw']):<12}")
        print()

    if tipo in ["todos", "tubulacoes"]:
        print("=" * 80)
        print("   CATÁLOGO DE TUBULAÇÕES COMERCIAIS (COBRE NBR 13206 E AÇO NBR 5580)")
        print("=" * 80)
        print(f"{'Código':<12} | {'Rótulo Comercial':<28} | {'D_ext (mm)':<10} | {'D_int (mm)':<10} | {'Material'}")
        print("-" * 80)
        for c, t in sorted(CATALOGO_TUBULACOES.items()):
            print(f"{c:<12} | {str(t['rotulo']):<28} | {str(t['diametro_externo_mm']):<10} | {str(t['diametro_interno_mm']):<10} | {str(t['tipo'])}")
        print()

    return 0


def cmd_gerar_exemplo(tipo: str, saida: str | None) -> int:
    """Gera modelo JSON canônico de exemplo."""
    if tipo == "gn_residencial":
        json_conteudo = """{
  "tipo_gas": "GN",
  "aplicar_fator_simultaneidade": true,
  "aparelhos": [
    {
      "identificador": "FOGAO_1",
      "descricao": "Fogão doméstico 4 bocas com forno",
      "quantidade": 1,
      "tipo_padrao": "fogao_4_bocas"
    },
    {
      "identificador": "AQUECEDOR_1",
      "descricao": "Aquecedor de passagem 20 L/min",
      "quantidade": 1,
      "tipo_padrao": "aquecedor_passagem_20l"
    }
  ],
  "trechos": [
    {
      "identificador": "A-B (Principal)",
      "comprimento_real_m": 8,
      "tubulacao_codigo": "CU_DN22",
      "conexoes": {
        "joelho_90": 2,
        "te_passagem_direta": 1,
        "valvula_esfera": 1
      }
    },
    {
      "identificador": "B-Aquecedor",
      "comprimento_real_m": 3,
      "tubulacao_codigo": "CU_DN22",
      "conexoes": {
        "joelho_90": 3,
        "valvula_esfera": 1
      },
      "vazao_m3_h": "2.56"
    },
    {
      "identificador": "B-Fogao",
      "comprimento_real_m": 5,
      "tubulacao_codigo": "CU_DN15",
      "conexoes": {
        "joelho_90": 2,
        "valvula_esfera": 1
      },
      "vazao_m3_h": "0.64"
    }
  ]
}
"""
    else:  # glp_comercial
        json_conteudo = """{
  "tipo_gas": "GLP",
  "aplicar_fator_simultaneidade": true,
  "aparelhos": [
    {
      "identificador": "FOGAO_IND",
      "descricao": "Fogão industrial 6 bocas",
      "quantidade": 2,
      "tipo_padrao": "fogao_6_bocas"
    },
    {
      "identificador": "FORNO_IND",
      "descricao": "Forno a gás comercial",
      "quantidade": 1,
      "potencia_kw": 8
    }
  ],
  "trechos": [
    {
      "identificador": "Central-B",
      "comprimento_real_m": 12,
      "tubulacao_codigo": "CU_DN28",
      "conexoes": {
        "joelho_90": 3,
        "te_passagem_direta": 1,
        "valvula_esfera": 2
      }
    },
    {
      "identificador": "B-Fogoes",
      "comprimento_real_m": 4,
      "tubulacao_codigo": "CU_DN22",
      "conexoes": {
        "joelho_90": 2,
        "valvula_esfera": 1
      }
    }
  ]
}
"""

    if saida:
        with open(saida, "w", encoding="utf-8") as f:
            f.write(json_conteudo)
        print(f"Exemplo JSON ({tipo}) salvo com sucesso em: {saida}")
    else:
        sys.stdout.write(json_conteudo)
    return 0


def cmd_calcular(arquivo_entrada: str, formato: str, saida: str | None) -> int:
    """Executa o cálculo e emite o resultado no formato especificado."""
    try:
        with open(arquivo_entrada, "rb") as f:
            conteudo_bytes = f.read()
        dados = carregar_entrada_json(conteudo_bytes)
    except Exception as e:
        sys.stderr.write(f"Erro ao carregar arquivo de entrada JSON: {e}\n")
        return 1

    try:
        resultado = dimensionar_rede_gas(
            tipo_gas=dados["tipo_gas"],
            aparelhos_entrada=dados["aparelhos"],
            trechos_entrada=dados["trechos"],
            aplicar_fator_simultaneidade=dados["aplicar_fator_simultaneidade"],
        )
    except Exception as e:
        sys.stderr.write(f"Erro no cálculo hidráulico: {e}\n")
        return 1

    if formato == "texto":
        rel = gerar_relatorio_texto(resultado)
        if saida:
            with open(saida, "w", encoding="utf-8") as f:
                f.write(rel)
            print(f"Relatório técnico salvo em: {saida}")
        else:
            sys.stdout.write(rel)
    elif formato == "json":
        js = exportar_resultado_json(resultado)
        if saida:
            with open(saida, "w", encoding="utf-8") as f:
                f.write(js)
            print(f"Resultado JSON salvo em: {saida}")
        else:
            sys.stdout.write(js + "\n")
    elif formato == "csv":
        csv_txt = gerar_csv_sanitizado(resultado)
        if saida:
            with open(saida, "w", encoding="utf-8") as f:
                f.write(csv_txt)
            print(f"Tabela CSV sanitizada salva em: {saida}")
        else:
            sys.stdout.write(csv_txt)
    elif formato == "svg":
        if not saida:
            sys.stderr.write("Erro: O formato SVG exige especificação do arquivo de saída (-o / --saida).\n")
            return 1
        svg_txt = gerar_painel_svg(resultado)
        with open(saida, "w", encoding="utf-8") as f:
            f.write(svg_txt)
        print(f"Painel visual SVG salvo em: {saida}")
    elif formato == "zip":
        if not saida:
            sys.stderr.write("Erro: O formato ZIP exige especificação do arquivo de saída (-o / --saida).\n")
            return 1
        svg_txt = gerar_painel_svg(resultado)
        gerar_pacote_zip_deterministico(saida, resultado, conteudo_svg=svg_txt)
        print(f"Pacote determinístico ZIP salvo em: {saida}")

    return 0 if resultado.aprovado_global else 2


def main(argv: Sequence[str] | None = None) -> int:
    """Ponto de entrada principal da CLI."""
    parser = criar_parser()
    args = parser.parse_args(argv)

    if not args.comando:
        parser.print_help()
        return 0

    if args.comando == "catalogo":
        return cmd_catalogo(args.tipo)
    if args.comando == "gerar-exemplo":
        return cmd_gerar_exemplo(args.tipo, args.saida)
    if args.comando == "calcular":
        return cmd_calcular(args.arquivo_entrada, args.formato, args.saida)

    return 0


if __name__ == "__main__":
    sys.exit(main())
