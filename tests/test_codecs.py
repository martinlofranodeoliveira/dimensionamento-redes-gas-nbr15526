"""Testes unitários dos codecs canônicos JSON e proteções RFC 8259."""

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fractions import Fraction
from redes_gas_nbr15526.codecs import (
    carregar_entrada_json,
    exportar_resultado_json,
    fracao_para_str,
    parsear_fracao_segura,
    parsear_json_seguro,
    verificar_profundidade,
)
from redes_gas_nbr15526.calculator import dimensionar_rede_gas


class TestCodecs(unittest.TestCase):
    """Validações de rejeição estrita de BOM, floats, chaves duplicadas e profundidade."""

    def test_rejeicao_bom_bytes_e_str(self) -> None:
        conteudo_bytes = b"\xef\xbb\xbf{\"tipo_gas\": \"GN\"}"
        with self.assertRaises(ValueError):
            parsear_json_seguro(conteudo_bytes)

        conteudo_str = "\ufeff{\"tipo_gas\": \"GN\"}"
        with self.assertRaises(ValueError):
            parsear_json_seguro(conteudo_str)

    def test_rejeicao_chaves_duplicadas(self) -> None:
        json_dup = '{"tipo_gas": "GN", "tipo_gas": "GLP"}'
        with self.assertRaises(ValueError):
            parsear_json_seguro(json_dup)

    def test_rejeicao_ponto_flutuante(self) -> None:
        json_float = '{"vazao": 2.5}'
        with self.assertRaises(ValueError):
            parsear_json_seguro(json_float)

    def test_rejeicao_profundidade_excessiva(self) -> None:
        obj: dict = {}
        curr = obj
        for _ in range(35):
            curr["nested"] = {}
            curr = curr["nested"]
        with self.assertRaises(ValueError):
            verificar_profundidade(obj)

    def test_parsear_fracao_segura(self) -> None:
        self.assertEqual(parsear_fracao_segura(10), Fraction(10, 1))
        self.assertEqual(parsear_fracao_segura("10"), Fraction(10, 1))
        self.assertEqual(parsear_fracao_segura("3/4"), Fraction(3, 4))
        self.assertEqual(parsear_fracao_segura("2.5"), Fraction(25, 10))
        self.assertEqual(parsear_fracao_segura("2,5"), Fraction(25, 10))
        self.assertEqual(parsear_fracao_segura((5, 2)), Fraction(5, 2))
        self.assertEqual(parsear_fracao_segura(Fraction(7, 3)), Fraction(7, 3))

        with self.assertRaises(ValueError):
            parsear_fracao_segura(2.5)
        with self.assertRaises(TypeError):
            parsear_fracao_segura(False)
        with self.assertRaises(ValueError):
            parsear_fracao_segura("")

    def test_fracao_para_str(self) -> None:
        self.assertEqual(fracao_para_str(Fraction(4, 1)), "4")
        self.assertEqual(fracao_para_str(Fraction(1, 2)), "0.5")
        self.assertEqual(fracao_para_str(Fraction(1, 4)), "0.25")
        self.assertEqual(fracao_para_str(Fraction(1, 3)), "1/3")

    def test_carregar_entrada_json_valida(self) -> None:
        conteudo = """{
            "tipo_gas": "GN",
            "aparelhos": [
                {"identificador": "FOGAO", "tipo_padrao": "fogao_4_bocas", "quantidade": 1}
            ],
            "trechos": [
                {"identificador": "A-B", "comprimento_real_m": 10, "tubulacao_codigo": "CU_DN22"}
            ]
        }"""
        dados = carregar_entrada_json(conteudo)
        self.assertEqual(dados["tipo_gas"], "GN")
        self.assertEqual(len(dados["aparelhos"]), 1)
        self.assertEqual(len(dados["trechos"]), 1)

    def test_exportar_resultado_json(self) -> None:
        res = dimensionar_rede_gas(
            tipo_gas="GN",
            aparelhos_entrada=[{"identificador": "FOGAO", "tipo_padrao": "fogao_4_bocas", "quantidade": 1}],
            trechos_entrada=[{"identificador": "A-B", "comprimento_real_m": 5, "tubulacao_codigo": "CU_DN22"}],
        )
        js = exportar_resultado_json(res)
        self.assertIn("ABNT NBR 15526:2016", js)
        self.assertIn("APROVADO", js)
        parsed = json.loads(js)
        self.assertEqual(parsed["status_global"], "APROVADO")


    def test_parsear_fracao_segura_tupla_invalida(self) -> None:
        with self.assertRaises(TypeError):
            parsear_fracao_segura((1, 2, 3))

    def test_carregar_entrada_json_sem_tipo_gas(self) -> None:
        with self.assertRaises(ValueError):
            carregar_entrada_json('{"aparelhos": [], "trechos": []}')

    def test_carregar_entrada_json_sem_aparelhos(self) -> None:
        with self.assertRaises(ValueError):
            carregar_entrada_json('{"tipo_gas": "GN", "trechos": []}')


if __name__ == "__main__":
    unittest.main()
