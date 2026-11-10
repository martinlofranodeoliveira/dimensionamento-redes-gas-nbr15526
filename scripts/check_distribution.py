"""Valida o conteúdo das distribuições construídas (wheel e sdist)."""

import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"


def main() -> int:
    if not DIST.exists():
        print("Erro: Diretório dist/ não encontrado.")
        return 1

    wheels = list(DIST.glob("*.whl"))
    sdists = list(DIST.glob("*.tar.gz"))

    if not wheels:
        print("Erro: Nenhum pacote .whl encontrado em dist/.")
        return 1
    if not sdists:
        print("Erro: Nenhum pacote .tar.gz encontrado em dist/.")
        return 1

    wheel_path = wheels[0]
    sdist_path = sdists[0]

    print(f"Inspecionando wheel: {wheel_path.name}")
    with zipfile.ZipFile(wheel_path) as zf:
        nomes = zf.namelist()
        for nome in nomes:
            if nome.endswith(".pyc") or "__pycache__" in nome:
                print(f"Erro: Arquivo compilado indesejado no wheel: {nome}")
                return 1
        tem_py_typed = any("py.typed" in n for n in nomes)
        if not tem_py_typed:
            print("Erro: Arquivo py.typed ausente no wheel.")
            return 1
        print(f"✓ Wheel válido ({len(nomes)} arquivos, py.typed presente).")

    print(f"Inspecionando sdist: {sdist_path.name}")
    with tarfile.open(sdist_path, "r:gz") as tf:
        nomes_sdist = tf.getnames()
        tem_pyproject = any("pyproject.toml" in n for n in nomes_sdist)
        tem_licenca = any("LICENSE" in n for n in nomes_sdist)
        if not (tem_pyproject and tem_licenca):
            print("Erro: pyproject.toml ou LICENSE ausente no sdist.")
            return 1
        print(f"✓ sdist válido ({len(nomes_sdist)} arquivos, metadados presentes).")

    print("Distribuições inspecionadas e validadas com sucesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
