"""Testes unitários para a interface de linha de comando (CLI)."""

import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from redes_gas_nbr15526.cli import main


class TestCli(unittest.TestCase):
    """Testes dos comandos e opções da CLI."""

    def test_cli_ajuda(self) -> None:
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            with self.assertRaises(SystemExit) as cm:
                main(["--ajuda"])
            self.assertEqual(cm.exception.code, 0)
            self.assertIn("15526", fake_out.getvalue())

    def test_cli_versao(self) -> None:
        with self.assertRaises(SystemExit):
            main(["--versao"])

    def test_cli_sem_comando(self) -> None:
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            code = main([])
            self.assertEqual(code, 0)
            self.assertIn("usage:", fake_out.getvalue())

    def test_cli_catalogo_todos(self) -> None:
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            code = main(["catalogo", "--tipo", "todos"])
            self.assertEqual(code, 0)
            self.assertIn("GASES COMBUSTÍVEIS", fake_out.getvalue())
            self.assertIn("APARELHOS DE CONSUMO", fake_out.getvalue())
            self.assertIn("CATÁLOGO DE TUBULAÇÕES", fake_out.getvalue())

    def test_cli_gerar_exemplo(self) -> None:
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            code = main(["gerar-exemplo", "--tipo", "gn_residencial"])
            self.assertEqual(code, 0)
            self.assertIn("tipo_gas", fake_out.getvalue())
            self.assertIn("GN", fake_out.getvalue())

    def test_cli_calcular_texto(self) -> None:
        exemplo = "examples/apartamento_residencial_gn.json"
        if os.path.exists(exemplo):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                code = main(["calcular", exemplo, "-f", "texto"])
                self.assertEqual(code, 0)
                self.assertIn("LOFRANO TECNOLOGIA", fake_out.getvalue())
                self.assertIn("APROVADO", fake_out.getvalue())

    def test_cli_calcular_json(self) -> None:
        exemplo = "examples/apartamento_residencial_gn.json"
        if os.path.exists(exemplo):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                code = main(["calcular", exemplo, "-f", "json"])
                self.assertEqual(code, 0)
                self.assertIn('"status_global": "APROVADO"', fake_out.getvalue())

    def test_cli_calcular_csv(self) -> None:
        exemplo = "examples/apartamento_residencial_gn.json"
        if os.path.exists(exemplo):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                code = main(["calcular", exemplo, "-f", "csv"])
                self.assertEqual(code, 0)
                self.assertIn("Trecho,Tubulacao", fake_out.getvalue())

    def test_cli_calcular_svg_e_zip(self) -> None:
        exemplo = "examples/apartamento_residencial_gn.json"
        if os.path.exists(exemplo):
            with tempfile.TemporaryDirectory() as tmpdir:
                svg_saida = os.path.join(tmpdir, "rede.svg")
                zip_saida = os.path.join(tmpdir, "rede.zip")

                code_svg = main(["calcular", exemplo, "-f", "svg", "-o", svg_saida])
                self.assertEqual(code_svg, 0)
                self.assertTrue(os.path.exists(svg_saida))

                code_zip = main(["calcular", exemplo, "-f", "zip", "-o", zip_saida])
                self.assertEqual(code_zip, 0)
                self.assertTrue(os.path.exists(zip_saida))

    def test_cli_erro_arquivo_inexistente(self) -> None:
        code = main(["calcular", "arquivo_inexistente_99.json"])
        self.assertEqual(code, 1)


    def test_cli_catalogo_gases(self) -> None:
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            code = main(["catalogo", "--tipo", "gases"])
            self.assertEqual(code, 0)
            self.assertIn("GASES COMBUSTÍVEIS", fake_out.getvalue())

    def test_cli_catalogo_tubulacoes(self) -> None:
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            code = main(["catalogo", "--tipo", "tubulacoes"])
            self.assertEqual(code, 0)
            self.assertIn("CATÁLOGO DE TUBULAÇÕES", fake_out.getvalue())

    def test_cli_gerar_exemplo_glp(self) -> None:
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            code = main(["gerar-exemplo", "--tipo", "glp_comercial"])
            self.assertEqual(code, 0)
            self.assertIn("GLP", fake_out.getvalue())


if __name__ == "__main__":
    unittest.main()
