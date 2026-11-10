"""Testes unitários para os modelos de dados e propriedades geométricas da tubulação."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fractions import Fraction
from redes_gas_nbr15526.models import (
    AparelhoConsumo,
    ConexoesTrecho,
    GasCombustivel,
    TrechoRede,
    TubulacaoItem,
)


class TestModelos(unittest.TestCase):
    """Testes de integridade e imutabilidade dos modelos de dados."""

    def test_tubulacao_item_area_interna(self) -> None:
        tubo = TubulacaoItem(
            codigo="CU_DN22",
            tipo="cobre",
            rotulo="Cobre DN 22",
            diametro_externo_mm=Fraction(22, 1),
            espessura_mm=Fraction(11, 10),
            diametro_interno_mm=Fraction(99, 5),  # 19.8 mm
        )
        self.assertEqual(tubo.codigo, "CU_DN22")
        self.assertGreater(tubo.area_interna_mm2, 0)
        # pi * D^2 / 4 = (355/113) * 19.8^2 / 4 ~ 307.9 mm²
        area_aprox = float(tubo.area_interna_mm2)
        self.assertAlmostEqual(area_aprox, 307.9, delta=1.0)

    def test_conexoes_trecho_padrao(self) -> None:
        con = ConexoesTrecho()
        self.assertEqual(con.joelho_90, 0)
        self.assertEqual(con.joelho_45, 0)
        self.assertEqual(con.comprimento_equivalente_m, Fraction(0, 1))

    def test_aparelho_consumo(self) -> None:
        ap = AparelhoConsumo(
            identificador="FOGAO_1",
            descricao="Fogão 4 bocas",
            quantidade=2,
            potencia_unitaria_kw=Fraction(7, 1),
            potencia_total_kw=Fraction(14, 1),
            vazao_unitaria_m3_h=Fraction(602, 940),
            vazao_total_m3_h=Fraction(1204, 940),
        )
        self.assertEqual(ap.quantidade, 2)
        self.assertEqual(ap.potencia_total_kw, Fraction(14, 1))


if __name__ == "__main__":
    unittest.main()
