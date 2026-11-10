"""Testes unitários dos exportadores (relatório texto, CSV sanitizado e pacote determinístico ZIP)."""

import os
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fractions import Fraction
from redes_gas_nbr15526.calculator import dimensionar_rede_gas
from redes_gas_nbr15526.exporters import (
    DATA_DETERMINISTICA,
    gerar_csv_sanitizado,
    gerar_pacote_zip_deterministico,
    gerar_relatorio_texto,
    sanitizar_campo_csv,
)


class TestExporters(unittest.TestCase):
    """Validações de formatação tabular, sanitização de CSV e ZIP determinístico."""

    def setUp(self) -> None:
        self.resultado = dimensionar_rede_gas(
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

    def test_relatorio_texto(self) -> None:
        rel = gerar_relatorio_texto(self.resultado)
        self.assertIn("LOFRANO TECNOLOGIA", rel)
        self.assertIn("ABNT NBR 15526:2016", rel)
        self.assertIn("Gás Natural", rel)
        self.assertIn("APROVADO", rel)

    def test_sanitizacao_csv(self) -> None:
        self.assertEqual(sanitizar_campo_csv("=1+1"), "'=1+1")
        self.assertEqual(sanitizar_campo_csv("+123"), "'+123")
        self.assertEqual(sanitizar_campo_csv("-123"), "'-123")
        self.assertEqual(sanitizar_campo_csv("@CMD"), "'@CMD")
        self.assertEqual(sanitizar_campo_csv("\tTESTE"), "'\tTESTE")
        self.assertEqual(sanitizar_campo_csv("Normal"), "Normal")

    def test_gerar_csv_sanitizado(self) -> None:
        csv_txt = gerar_csv_sanitizado(self.resultado)
        self.assertIn("Trecho,Tubulacao,Diametro_Interno_mm", csv_txt)
        self.assertIn("A-B", csv_txt)
        self.assertIn("CU_DN22", csv_txt)

    def test_gerar_pacote_zip_deterministico(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_caminho = os.path.join(tmpdir, "pacote.zip")
            gerar_pacote_zip_deterministico(zip_caminho, self.resultado, conteudo_svg="<svg></svg>")

            self.assertTrue(os.path.exists(zip_caminho))

            with zipfile.ZipFile(zip_caminho, "r") as zf:
                nomes = zf.namelist()
                self.assertIn("relatorio.txt", nomes)
                self.assertIn("resultado.json", nomes)
                self.assertIn("trechos.csv", nomes)
                self.assertIn("painel.svg", nomes)

                for info in zf.infolist():
                    self.assertEqual(info.date_time, DATA_DETERMINISTICA)

            # Testar proteção O_EXCL
            with self.assertRaises(FileExistsError):
                gerar_pacote_zip_deterministico(zip_caminho, self.resultado)


if __name__ == "__main__":
    unittest.main()
