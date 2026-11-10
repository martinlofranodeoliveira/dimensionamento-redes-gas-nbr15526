"""Testes de integridade de empacotamento, importação e metadados."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import redes_gas_nbr15526


class TestPackaging(unittest.TestCase):
    """Validações de exportação de símbolos e versão do pacote."""

    def test_versao_pacote(self) -> None:
        self.assertEqual(redes_gas_nbr15526.__version__, "1.0.0")
        self.assertEqual(redes_gas_nbr15526.VERSAO, "1.0.0")

    def test_simbolos_exportados(self) -> None:
        exportados = redes_gas_nbr15526.__all__
        self.assertIn("dimensionar_rede_gas", exportados)
        self.assertIn("obter_gas_combustivel", exportados)
        self.assertIn("obter_tubulacao_catalogo", exportados)
        self.assertIn("calcular_perda_carga_pole", exportados)
        self.assertIn("gerar_relatorio_texto", exportados)
        self.assertIn("gerar_painel_svg", exportados)
        self.assertIn("gerar_pacote_zip_deterministico", exportados)


if __name__ == "__main__":
    unittest.main()
