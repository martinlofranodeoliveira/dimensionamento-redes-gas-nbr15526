"""Testes unitários para as constantes e tabelas normativas da NBR 15526."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fractions import Fraction
from redes_gas_nbr15526.constants import (
    APARELHOS_PADRAO,
    CATALOGO_TUBULACOES,
    CONSTANTE_POLE,
    GASES_COMBUSTIVEIS,
    PERDAS_CONEXOES_COBRE,
    TUBOS_ACO_CARBONO,
    TUBOS_COBRE_CLASSE_A,
    VELOCIDADE_MAXIMA_GAS_M_S,
    VELOCIDADE_RECOMENDADA_M_S,
)


class TestConstantes(unittest.TestCase):
    """Validações das propriedades físicas e tabelas normativas."""

    def test_gases_combustiveis(self) -> None:
        self.assertIn("GN", GASES_COMBUSTIVEIS)
        self.assertIn("GLP", GASES_COMBUSTIVEIS)

        gn = GASES_COMBUSTIVEIS["GN"]
        self.assertEqual(gn["densidade_relativa_ar"], Fraction(6, 10))
        self.assertEqual(gn["pcs_kcal_m3"], 9400)
        self.assertEqual(gn["pressao_nominal_baixa_mmca"], 200)

        glp = GASES_COMBUSTIVEIS["GLP"]
        self.assertEqual(glp["densidade_relativa_ar"], Fraction(152, 100))
        self.assertEqual(glp["pcs_kcal_m3"], 24000)
        self.assertEqual(glp["pressao_nominal_baixa_mmca"], 280)

    def test_aparelhos_padrao(self) -> None:
        self.assertGreater(len(APARELHOS_PADRAO), 6)
        self.assertIn("fogao_4_bocas", APARELHOS_PADRAO)
        self.assertIn("aquecedor_passagem_20l", APARELHOS_PADRAO)
        self.assertEqual(APARELHOS_PADRAO["fogao_4_bocas"]["potencia_kw"], 7)
        self.assertEqual(APARELHOS_PADRAO["aquecedor_passagem_20l"]["potencia_kw"], 28)

    def test_tubulacoes_cobre_e_aco(self) -> None:
        self.assertIn("CU_DN15", TUBOS_COBRE_CLASSE_A)
        self.assertIn("CU_DN22", TUBOS_COBRE_CLASSE_A)
        self.assertEqual(TUBOS_COBRE_CLASSE_A["CU_DN15"]["diametro_interno_mm"], Fraction(13, 1))
        self.assertEqual(TUBOS_COBRE_CLASSE_A["CU_DN22"]["diametro_interno_mm"], Fraction(99, 5))

        self.assertIn("ACO_1/2", TUBOS_ACO_CARBONO)
        self.assertIn("ACO_3/4", TUBOS_ACO_CARBONO)
        self.assertEqual(len(CATALOGO_TUBULACOES), len(TUBOS_COBRE_CLASSE_A) + len(TUBOS_ACO_CARBONO))

    def test_conexoes_e_constante_pole(self) -> None:
        self.assertIn("CU_DN22", PERDAS_CONEXOES_COBRE)
        self.assertEqual(CONSTANTE_POLE, Fraction(22222, 1))
        self.assertEqual(VELOCIDADE_MAXIMA_GAS_M_S, Fraction(20, 1))
        self.assertEqual(VELOCIDADE_RECOMENDADA_M_S, Fraction(15, 1))


if __name__ == "__main__":
    unittest.main()
