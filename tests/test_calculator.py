"""Testes unitários do motor analítico de dimensionamento de gás (NBR 15526)."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fractions import Fraction
from redes_gas_nbr15526.calculator import (
    calcular_comprimento_equivalente_conexoes,
    calcular_fator_simultaneidade,
    calcular_perda_carga_pole,
    calcular_vazao_aparelho,
    calcular_velocidade_gas,
    dimensionar_rede_gas,
    obter_gas_combustivel,
    obter_tubulacao_catalogo,
)
from redes_gas_nbr15526.models import ConexoesTrecho


class TestCalculadora(unittest.TestCase):
    """Testes de todas as rotinas analíticas sem uso de floats."""

    def test_obter_gas_combustivel(self) -> None:
        gn = obter_gas_combustivel("gn")
        self.assertEqual(gn.sigla, "GN")
        self.assertEqual(gn.densidade_relativa_ar, Fraction(6, 10))

        glp = obter_gas_combustivel("GLP")
        self.assertEqual(glp.sigla, "GLP")
        self.assertEqual(glp.densidade_relativa_ar, Fraction(152, 100))

        with self.assertRaises(ValueError):
            obter_gas_combustivel("GAS_INEXISTENTE")

    def test_obter_tubulacao_catalogo(self) -> None:
        tubo = obter_tubulacao_catalogo("cu_dn22")
        self.assertEqual(tubo.codigo, "CU_DN22")
        self.assertEqual(tubo.diametro_interno_mm, Fraction(99, 5))

        with self.assertRaises(ValueError):
            obter_tubulacao_catalogo("TUBO_INEXISTENTE")

    def test_calcular_vazao_aparelho(self) -> None:
        gn = obter_gas_combustivel("GN")
        # Fogao 7 kW -> 7 * 860 = 6020 kcal/h -> 6020 / 9400 = 602 / 940 m³/h
        vazao_gn = calcular_vazao_aparelho(Fraction(7, 1), gn)
        self.assertEqual(vazao_gn, Fraction(6020, 9400))

        glp = obter_gas_combustivel("GLP")
        # Fogao 7 kW -> 6020 / 24000 = 602 / 2400 m³/h
        vazao_glp = calcular_vazao_aparelho(Fraction(7, 1), glp)
        self.assertEqual(vazao_glp, Fraction(6020, 24000))

        with self.assertRaises(ValueError):
            calcular_vazao_aparelho(Fraction(-5, 1), gn)

    def test_calcular_fator_simultaneidade(self) -> None:
        self.assertEqual(calcular_fator_simultaneidade(0), Fraction(0, 1))
        self.assertEqual(calcular_fator_simultaneidade(1), Fraction(1, 1))
        self.assertEqual(calcular_fator_simultaneidade(2), Fraction(1, 1))
        self.assertEqual(calcular_fator_simultaneidade(3), Fraction(85, 100))
        self.assertEqual(calcular_fator_simultaneidade(4), Fraction(75, 100))
        self.assertEqual(calcular_fator_simultaneidade(5), Fraction(65, 100))
        self.assertEqual(calcular_fator_simultaneidade(10), Fraction(55, 100))
        self.assertEqual(calcular_fator_simultaneidade(20), Fraction(45, 100))
        self.assertEqual(calcular_fator_simultaneidade(30), Fraction(35, 100))

    def test_calcular_comprimento_equivalente_conexoes(self) -> None:
        con = ConexoesTrecho(joelho_90=2, te_passagem_direta=1, valvula_esfera=1)
        # Para CU_DN22: joelho_90=0.7, te_dir=0.3, valvula=0.2
        # Leq = 2*0.7 + 1*0.3 + 1*0.2 = 1.4 + 0.3 + 0.2 = 1.9 m
        comp = calcular_comprimento_equivalente_conexoes("CU_DN22", con)
        self.assertEqual(comp, Fraction(19, 10))

    def test_calcular_perda_carga_pole(self) -> None:
        # Vazão 0 -> perda 0
        self.assertEqual(
            calcular_perda_carga_pole(Fraction(0), Fraction(20), Fraction(10), Fraction(6, 10)),
            Fraction(0, 1),
        )

        # Delta_H = (22222 * dr * L * Q^2) / D^5
        dh = calcular_perda_carga_pole(
            vazao_m3_h=Fraction(2, 1),
            diametro_interno_mm=Fraction(20, 1),
            comprimento_total_m=Fraction(10, 1),
            densidade_relativa=Fraction(6, 10),
        )
        self.assertGreater(dh, 0)
        # Esperado: (22222 * 0.6 * 10 * 4) / 3200000 = 533328 / 3200000 = 0.166665 mmca
        self.assertEqual(dh, Fraction(22222 * 6 * 10 * 4, 10 * 3200000))

        with self.assertRaises(ValueError):
            calcular_perda_carga_pole(Fraction(1), Fraction(0), Fraction(10), Fraction(6, 10))

    def test_calcular_velocidade_gas(self) -> None:
        self.assertEqual(calcular_velocidade_gas(Fraction(0), Fraction(20)), Fraction(0, 1))

        vel = calcular_velocidade_gas(Fraction(2, 1), Fraction(20, 1))
        self.assertGreater(vel, 0)
        # Em m/s: (2 * 10000) / (9 * (355/113) * 400) = 20000 / (3600 * 355/113) ~ 1.76 m/s
        self.assertLess(vel, 20)

        with self.assertRaises(ValueError):
            calcular_velocidade_gas(Fraction(1), Fraction(0))

    def test_dimensionamento_completo_aprovado(self) -> None:
        aparelhos = [
            {"identificador": "FOGAO", "tipo_padrao": "fogao_4_bocas", "quantidade": 1},
            {"identificador": "AQUECEDOR", "tipo_padrao": "aquecedor_passagem_20l", "quantidade": 1},
        ]
        trechos = [
            {
                "identificador": "A-B",
                "comprimento_real_m": 8,
                "tubulacao_codigo": "CU_DN22",
                "conexoes": {"joelho_90": 2, "te_passagem_direta": 1},
            },
            {
                "identificador": "B-Aquecedor",
                "comprimento_real_m": 3,
                "tubulacao_codigo": "CU_DN22",
                "conexoes": {"joelho_90": 3},
                "vazao_m3_h": "2.56",
            },
            {
                "identificador": "B-Fogao",
                "comprimento_real_m": 5,
                "tubulacao_codigo": "CU_DN15",
                "conexoes": {"joelho_90": 2},
                "vazao_m3_h": "0.64",
            },
        ]

        res = dimensionar_rede_gas(
            tipo_gas="GN",
            aparelhos_entrada=aparelhos,
            trechos_entrada=trechos,
            aplicar_fator_simultaneidade=True,
        )

        self.assertTrue(res.aprovado_global)
        self.assertTrue(res.aprovado_perda_carga)
        self.assertTrue(res.aprovado_velocidade)
        self.assertIn("APROVADO", res.resumo_status)

    def test_dimensionamento_reprovado_perda_carga(self) -> None:
        # Trecho extremamente longo e tubo fino gerando perda superior a 25 mmca
        aparelhos = [{"identificador": "AQUECEDOR", "potencia_kw": 40, "quantidade": 1}]
        trechos = [
            {
                "identificador": "Trecho_Extremo",
                "comprimento_real_m": 120,
                "tubulacao_codigo": "CU_DN15",
            }
        ]
        res = dimensionar_rede_gas(
            tipo_gas="GN",
            aparelhos_entrada=aparelhos,
            trechos_entrada=trechos,
        )
        self.assertFalse(res.aprovado_global)
        self.assertFalse(res.aprovado_perda_carga)
        self.assertIn("REPROVADO: Perda de carga", res.resumo_status)


    def test_calcular_vazao_aparelho_zero(self) -> None:
        gn = obter_gas_combustivel("GN")
        self.assertEqual(calcular_vazao_aparelho(Fraction(0), gn), Fraction(0, 1))

    def test_calcular_perda_carga_comprimento_zero(self) -> None:
        dh = calcular_perda_carga_pole(Fraction(1), Fraction(20), Fraction(0), Fraction(6, 10))
        self.assertEqual(dh, Fraction(0, 1))

    def test_calcular_velocidade_vazao_zero(self) -> None:
        v = calcular_velocidade_gas(Fraction(0), Fraction(20))
        self.assertEqual(v, Fraction(0, 1))

    def test_dimensionamento_rede_glp(self) -> None:
        aparelhos = [
            {"identificador": "FOGAO_GLP", "tipo_padrao": "fogao_6_bocas", "quantidade": 1}
        ]
        trechos = [
            {
                "identificador": "Central-Ponto",
                "comprimento_real_m": 6,
                "tubulacao_codigo": "CU_DN22",
                "conexoes": {"joelho_90": 2, "valvula_esfera": 1},
            }
        ]
        res = dimensionar_rede_gas(
            tipo_gas="GLP",
            aparelhos_entrada=aparelhos,
            trechos_entrada=trechos,
        )
        self.assertTrue(res.aprovado_global)
        self.assertEqual(res.gas.sigla, "GLP")

    def test_dimensionamento_sem_simultaneidade(self) -> None:
        aparelhos = [
            {"identificador": "F1", "tipo_padrao": "fogao_4_bocas", "quantidade": 4}
        ]
        trechos = [
            {
                "identificador": "Ramal",
                "comprimento_real_m": 4,
                "tubulacao_codigo": "CU_DN22",
            }
        ]
        res = dimensionar_rede_gas(
            tipo_gas="GN",
            aparelhos_entrada=aparelhos,
            trechos_entrada=trechos,
            aplicar_fator_simultaneidade=False,
        )
        self.assertEqual(res.fator_simultaneidade, Fraction(1, 1))

    def test_dimensionamento_reprovado_velocidade(self) -> None:
        # Tubo extremamente estreito com vazão alta forçando velocidade > 20 m/s
        aparelhos = [{"identificador": "FORNO_POTENTE", "potencia_kw": 200, "quantidade": 1}]
        trechos = [
            {
                "identificador": "Tubo_Fino",
                "comprimento_real_m": 1,
                "tubulacao_codigo": "CU_DN15",
            }
        ]
        res = dimensionar_rede_gas(
            tipo_gas="GN",
            aparelhos_entrada=aparelhos,
            trechos_entrada=trechos,
        )
        self.assertFalse(res.aprovado_velocidade)
        self.assertFalse(res.aprovado_global)


if __name__ == "__main__":
    unittest.main()
