"""Testes unitários para o gerador de painel técnico visual em SVG."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from redes_gas_nbr15526.calculator import dimensionar_rede_gas
from redes_gas_nbr15526.svg_generator import gerar_painel_svg


class TestSvgGenerator(unittest.TestCase):
    """Validações de estrutura e elementos gráficos do painel SVG."""

    def test_gerar_painel_svg(self) -> None:
        res = dimensionar_rede_gas(
            tipo_gas="GN",
            aparelhos_entrada=[
                {"identificador": "FOGAO", "tipo_padrao": "fogao_4_bocas", "quantidade": 1},
                {"identificador": "AQUECEDOR", "tipo_padrao": "aquecedor_passagem_20l", "quantidade": 1},
            ],
            trechos_entrada=[
                {
                    "identificador": "A-B",
                    "comprimento_real_m": 8,
                    "tubulacao_codigo": "CU_DN22",
                    "conexoes": {"joelho_90": 2},
                }
            ],
        )

        svg = gerar_painel_svg(res)
        self.assertIn('<svg xmlns="http://www.w3.org/2000/svg"', svg)
        self.assertIn('viewBox="0 0 1440 900"', svg)
        self.assertIn('width="1440"', svg)
        self.assertIn('height="900"', svg)
        self.assertIn("LOFRANO TECNOLOGIA", svg)
        self.assertIn("ABNT NBR 15526", svg)
        self.assertIn("APROVADO", svg)
        self.assertIn("Gás Natural", svg)
        self.assertIn("MEDIDOR", svg)
        self.assertIn("AQUECEDOR", svg)
        self.assertIn("FOGÃO/FORNO", svg)
        self.assertIn("</svg>", svg)


if __name__ == "__main__":
    unittest.main()
