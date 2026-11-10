"""Exportadores em múltiplos formatos (Texto, CSV sanitizado e ZIP determinístico).

Conforme o padrão LOFRANO TECNOLOGIA:
- Relatório técnico tabular 100% pt-BR com formulações normativas
- Sanitização rigorosa de CSV contra injeção de fórmulas (=, +, -, @, \\t, \\r)
- Pacote determinístico ZIP com carimbo temporal fixo (2026-01-01) e proteção O_EXCL
"""

import io
import os
import zipfile
from fractions import Fraction
from typing import Final

from .codecs import exportar_resultado_json, fracao_para_str
from .models import ResultadoDimensionamentoRede

DATA_DETERMINISTICA: Final[tuple[int, int, int, int, int, int]] = (2026, 1, 1, 0, 0, 0)
GATILHOS_INJECAO_CSV: Final[tuple[str, ...]] = ("=", "+", "-", "@", "\t", "\r")


def sanitizar_campo_csv(valor: str) -> str:
    """Sanitiza strings para prevenir injeção de fórmulas em planilhas."""
    if not valor:
        return ""
    if any(valor.startswith(gatilho) for gatilho in GATILHOS_INJECAO_CSV):
        return f"'{valor}"
    texto = valor.strip()
    if any(texto.startswith(gatilho) for gatilho in GATILHOS_INJECAO_CSV):
        return f"'{texto}"
    return texto


def formatar_taxa_pct(f: Fraction) -> str:
    """Converte fração em representação percentual inteira."""
    pct = (f * 100).numerator // max(1, (f * 100).denominator)
    return f"{pct}%"


def gerar_relatorio_texto(res: ResultadoDimensionamentoRede) -> str:
    """Gera relatório técnico de dimensionamento em texto tabular formatado."""
    linhas: list[str] = [
        "=" * 82,
        "   LOFRANO TECNOLOGIA - DIMENSIONAMENTO DE REDES INTERNAS DE GÁS",
        "                NORMA TÉCNICA ABNT NBR 15526:2016",
        "=" * 82,
        "",
        "1. DADOS DO GÁS COMBUSTÍVEL E PARÂMETROS DE FORNECIMENTO",
        "-" * 82,
        f"  Gás Utilizado            : {res.gas.nome} ({res.gas.sigla})",
        f"  Densidade Relativa (Ar=1): {fracao_para_str(res.gas.densidade_relativa_ar)}",
        f"  Poder Calorífico Superior: {res.gas.pcs_kcal_m3} kcal/m³",
        f"  Pressão Nominal Fornecida: {res.gas.pressao_nominal_baixa_mmca} mmca ({res.gas.pressao_nominal_baixa_mmca / 100:.1f} kPa)",
        f"  Perda de Carga Máxima Adm: {fracao_para_str(res.gas.perda_carga_maxima_mmca)} mmca",
        "",
        "2. QUADRO DE DEMANDA E CONSUMO DOS APARELHOS",
        "-" * 82,
        f"{'Identificador':<14} | {'Descrição':<28} | {'Qtd':<4} | {'Pot (kW)':<10} | {'Vazão (m³/h)'}",
        "-" * 82,
    ]

    for ap in res.aparelhos:
        pot_str = f"{fracao_para_str(ap.potencia_total_kw)} kW"
        vaz_str = f"{fracao_para_str(ap.vazao_total_m3_h)} m³/h"
        linhas.append(
            f"{ap.identificador:<14} | {ap.descricao[:28]:<28} | {ap.quantidade:<4} | {pot_str:<10} | {vaz_str}"
        )

    linhas.extend([
        "-" * 82,
        f"  Potência Total Instalada : {fracao_para_str(res.potencia_total_instalada_kw)} kW",
        f"  Fator de Simultaneidade  : {fracao_para_str(res.fator_simultaneidade)}",
        f"  Potência Adotada (Simult): {fracao_para_str(res.potencia_simultanea_kw)} kW",
        f"  Vazão Simultânea de Pico : {fracao_para_str(res.vazao_total_simultanea_m3_h)} m³/h",
        "",
        "3. QUADRO ANALÍTICO DE DIMENSIONAMENTO DOS TRECHOS (FÓRMULA DE POLE)",
        "-" * 82,
        f"{'Trecho':<12} | {'Tubulação':<18} | {'D_int':<7} | {'L_eq':<7} | {'Q (m³/h)':<9} | {'ΔH (mmca)':<10} | {'Vel (m/s)'}",
        "-" * 82,
    ])

    for tr in res.trechos:
        d_int = f"{fracao_para_str(tr.tubulacao.diametro_interno_mm)}mm"
        l_eq = f"{fracao_para_str(tr.comprimento_total_equivalente_m)}m"
        q_str = f"{fracao_para_str(tr.vazao_m3_h)}"
        dh_str = f"{fracao_para_str(tr.perda_carga_trecho_mmca)}"
        vel_str = f"{fracao_para_str(tr.velocidade_m_s)}"
        linhas.append(
            f"{tr.identificador:<12} | {tr.tubulacao.codigo:<18} | {d_int:<7} | {l_eq:<7} | {q_str:<9} | {dh_str:<10} | {vel_str}"
        )

    linhas.extend([
        "-" * 82,
        "",
        "4. CONCLUSÃO TÉCNICA E RESULTADO GLOBAL",
        "-" * 82,
        f"  Perda de Carga Acumulada : {fracao_para_str(res.perda_carga_total_acumulada_mmca)} mmca (Limite: {fracao_para_str(res.perda_carga_admissivel_mmca)} mmca)",
        f"  Taxa de Perda de Carga   : {formatar_taxa_pct(res.taxa_perda_carga)} ({'OK' if res.aprovado_perda_carga else 'VIOLADA'})",
        f"  Velocidade Máxima do Gás : {fracao_para_str(res.velocidade_maxima_m_s)} m/s (Limite: 20 m/s - {'OK' if res.aprovado_velocidade else 'VIOLADA'})",
        f"  Status Geral da Rede     : {'APROVADO' if res.aprovado_global else 'REPROVADO'}",
        f"  Parecer Técnico          : {res.resumo_status}",
        "=" * 82,
    ])
    return "\n".join(linhas) + "\n"


def gerar_csv_sanitizado(res: ResultadoDimensionamentoRede) -> str:
    """Gera tabela CSV sanitizada contra injeção de fórmulas."""
    linhas: list[str] = [
        "Trecho,Tubulacao,Diametro_Interno_mm,Comprimento_Real_m,Comprimento_Eq_Conexoes_m,Comprimento_Total_m,Vazao_m3_h,Perda_Carga_mmca,Velocidade_m_s,Velocidade_OK"
    ]

    for tr in res.trechos:
        linhas.append(
            ",".join([
                sanitizar_campo_csv(tr.identificador),
                sanitizar_campo_csv(tr.tubulacao.codigo),
                sanitizar_campo_csv(fracao_para_str(tr.tubulacao.diametro_interno_mm)),
                sanitizar_campo_csv(fracao_para_str(tr.comprimento_real_m)),
                sanitizar_campo_csv(fracao_para_str(tr.conexoes.comprimento_equivalente_m)),
                sanitizar_campo_csv(fracao_para_str(tr.comprimento_total_equivalente_m)),
                sanitizar_campo_csv(fracao_para_str(tr.vazao_m3_h)),
                sanitizar_campo_csv(fracao_para_str(tr.perda_carga_trecho_mmca)),
                sanitizar_campo_csv(fracao_para_str(tr.velocidade_m_s)),
                sanitizar_campo_csv("SIM" if tr.velocidade_aprovada else "NAO"),
            ])
        )

    return "\n".join(linhas) + "\n"


def gerar_pacote_zip_deterministico(
    caminho_zip: str,
    res: ResultadoDimensionamentoRede,
    conteudo_svg: str | None = None,
) -> None:
    """Gera pacote ZIP determinístico com proteção O_EXCL e carimbo 2026-01-01."""
    buffer = io.BytesIO()

    conteudo_txt = gerar_relatorio_texto(res).encode("utf-8")
    conteudo_json = exportar_resultado_json(res).encode("utf-8")
    conteudo_csv = gerar_csv_sanitizado(res).encode("utf-8")

    arquivos = [
        ("relatorio.txt", conteudo_txt),
        ("resultado.json", conteudo_json),
        ("trechos.csv", conteudo_csv),
    ]

    if conteudo_svg is not None:
        arquivos.append(("painel.svg", conteudo_svg.encode("utf-8")))

    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for nome_arq, dados_bytes in arquivos:
            zinfo = zipfile.ZipInfo(nome_arq, date_time=DATA_DETERMINISTICA)
            zinfo.external_attr = 0o644 << 16
            zinfo.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(zinfo, dados_bytes)

    bytes_finais = buffer.getvalue()

    flags = os.O_CREAT | os.O_WRONLY | os.O_EXCL
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY

    fd = os.open(caminho_zip, flags, 0o644)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(bytes_finais)
    except Exception:
        raise
