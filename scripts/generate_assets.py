"""Gera o painel visual SVG e captura screenshot PNG 1440x900 via Chrome headless."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Adiciona src ao PYTHONPATH
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from redes_gas_nbr15526.calculator import dimensionar_rede_gas
from redes_gas_nbr15526.codecs import carregar_entrada_json
from redes_gas_nbr15526.svg_generator import gerar_painel_svg


def main() -> int:
    docs_dir = ROOT / "docs"
    docs_dir.mkdir(exist_ok=True)

    exemplo_json = ROOT / "examples" / "apartamento_residencial_gn.json"
    with open(exemplo_json, "rb") as f:
        dados = carregar_entrada_json(f.read())

    res = dimensionar_rede_gas(
        tipo_gas=dados["tipo_gas"],
        aparelhos_entrada=dados["aparelhos"],
        trechos_entrada=dados["trechos"],
        aplicar_fator_simultaneidade=dados["aplicar_fator_simultaneidade"],
    )

    svg_conteudo = gerar_painel_svg(res)
    svg_caminho = docs_dir / "painel_exemplo.svg"
    with open(svg_caminho, "w", encoding="utf-8") as f:
        f.write(svg_conteudo)
    print(f"SVG gerado em: {svg_caminho}")

    png_caminho = docs_dir / "exemplo.png"
    chrome_bin = None
    for cand in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]:
        if shutil.which(cand):
            chrome_bin = cand
            break

    if chrome_bin:
        cmd = [
            chrome_bin,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--window-size=1440,900",
            f"--screenshot={png_caminho}",
            str(svg_caminho),
        ]
        res_cmd = subprocess.run(cmd, capture_output=True, text=True)
        if res_cmd.returncode == 0 and png_caminho.exists():
            print(f"PNG gerado com sucesso via {chrome_bin}: {png_caminho} ({png_caminho.stat().st_size} bytes)")
        else:
            print(f"Aviso ao rodar {chrome_bin}: {res_cmd.stderr}")
    else:
        print("Aviso: Google Chrome / Chromium não encontrado para captura do PNG.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
