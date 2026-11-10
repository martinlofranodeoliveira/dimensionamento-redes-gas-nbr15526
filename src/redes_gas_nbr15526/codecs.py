"""Codecs canônicos e determinísticos JSON para redes internas de gás.

Conforme o padrão LOFRANO TECNOLOGIA:
- Conformidade estrita à RFC 8259
- Rejeição de Byte Order Mark (BOM: \\xef\\xbb\\xbf ou \\ufeff)
- Rejeição de chaves duplicadas
- Rejeição estrita de números de ponto flutuante (float)
- Rejeição de profundidade excessiva de aninhamento (> 32)
- Formatação canônica determinística com indentação consistente
"""

import json
from fractions import Fraction
from typing import Any

from .models import (
    AparelhoConsumo,
    GasCombustivel,
    ResultadoDimensionamentoRede,
    TrechoRede,
    TubulacaoItem,
)

LIMITE_PROFUNDIDADE_MAXIMA = 32


def verificar_profundidade(obj: Any, profundidade_atual: int = 0) -> None:
    """Valida se a profundidade da estrutura não excede o limite de segurança."""
    if profundidade_atual > LIMITE_PROFUNDIDADE_MAXIMA:
        raise ValueError(
            f"Profundidade de aninhamento excessiva (> {LIMITE_PROFUNDIDADE_MAXIMA})."
        )
    if isinstance(obj, dict):
        for v in obj.values():
            verificar_profundidade(v, profundidade_atual + 1)
    elif isinstance(obj, list):
        for item in obj:
            verificar_profundidade(item, profundidade_atual + 1)


def parsear_fracao_segura(valor: Any) -> Fraction:
    """Converte representações seguras em Fraction, rejeitando estritamente floats."""
    if isinstance(valor, bool):
        raise TypeError(f"Booleano não é valor numérico válido: {valor}")
    if isinstance(valor, float):
        raise ValueError(f"Ponto flutuante (float) estritamente proibido: {valor}")
    if isinstance(valor, int):
        return Fraction(valor, 1)
    if isinstance(valor, str):
        texto = valor.strip()
        if not texto:
            raise ValueError("String vazia não é representação numérica válida.")
        if "/" in texto:
            partes = texto.split("/")
            if len(partes) != 2:
                raise ValueError(f"Fração em string malformatada: '{texto}'")
            return Fraction(int(partes[0].strip()), int(partes[1].strip()))
        if "." in texto or "," in texto:
            texto_norm = texto.replace(",", ".")
            if texto_norm.count(".") != 1:
                raise ValueError(f"Número decimal inválido: '{texto}'")
            inteira, decimal = texto_norm.split(".")
            denominador = 10 ** len(decimal)
            numerador = int(inteira) * denominador + (int(decimal) if int(inteira) >= 0 else -int(decimal))
            return Fraction(numerador, denominador)
        return Fraction(int(texto), 1)
    if isinstance(valor, (list, tuple)) and len(valor) == 2:
        return Fraction(int(valor[0]), int(valor[1]))
    if isinstance(valor, Fraction):
        return valor
    raise TypeError(f"Tipo não conversível para Fraction de forma exata: {type(valor)}")


def _gancho_chaves_duplicadas(pares: list[tuple[str, Any]]) -> dict[str, Any]:
    """Detecta e rejeita chaves duplicadas em objetos JSON."""
    dicionario: dict[str, Any] = {}
    for chave, valor in pares:
        if chave in dicionario:
            raise ValueError(f"Chave duplicada detectada no JSON: '{chave}'")
        dicionario[chave] = valor
    return dicionario


def parsear_json_seguro(conteudo: str | bytes) -> dict[str, Any]:
    """Lê JSON estrito com verificação de BOM, duplicatas e profundidade."""
    if isinstance(conteudo, bytes):
        if conteudo.startswith(b"\xef\xbb\xbf"):
            raise ValueError("Byte Order Mark (BOM) UTF-8 detectado e rejeitado.")
        texto = conteudo.decode("utf-8")
    else:
        if conteudo.startswith("\ufeff"):
            raise ValueError("Byte Order Mark (BOM) UTF-8 detectado e rejeitado.")
        texto = conteudo

    dados = json.loads(
        texto,
        object_pairs_hook=_gancho_chaves_duplicadas,
        parse_float=lambda x: (_ for _ in ()).throw(
            ValueError(f"Ponto flutuante nativo detectado no JSON: '{x}'")
        ),
    )
    verificar_profundidade(dados)
    return dados


def fracao_para_str(f: Fraction) -> str:
    """Formata fração para string amigável ou decimal exato sem floats."""
    if f.denominator == 1:
        return str(f.numerator)
    # Testa se denominador tem apenas fatores primos de 2 e 5
    temp_den = f.denominator
    p2 = 0
    while temp_den % 2 == 0:
        temp_den //= 2
        p2 += 1
    p5 = 0
    while temp_den % 5 == 0:
        temp_den //= 5
        p5 += 1

    if temp_den == 1:
        k = max(p2, p5)
        pot10 = 10**k
        mult = pot10 // f.denominator
        num = abs(f.numerator) * mult
        str_num = str(num).zfill(k + 1)
        ponto = len(str_num) - k
        res = str_num[:ponto] + "." + str_num[ponto:]
        sinal = "-" if f.numerator < 0 else ""
        return f"{sinal}{res}"
    return f"{f.numerator}/{f.denominator}"


def carregar_entrada_json(conteudo: str | bytes) -> dict[str, Any]:
    """Carrega e valida a estrutura de entrada para dimensionamento de rede de gás."""
    dados = parsear_json_seguro(conteudo)
    if not isinstance(dados, dict):
        raise ValueError("O documento JSON raiz deve ser um objeto/dicionário.")

    if "tipo_gas" not in dados:
        raise ValueError("Campo obrigatório ausente: 'tipo_gas' ('GN' ou 'GLP').")
    if "aparelhos" not in dados or not isinstance(dados["aparelhos"], list):
        raise ValueError("Campo obrigatório ausente ou inválido: 'aparelhos' (lista).")
    if "trechos" not in dados or not isinstance(dados["trechos"], list):
        raise ValueError("Campo obrigatório ausente ou inválido: 'trechos' (lista).")

    aparelhos_processados: list[dict[str, Any]] = []
    for ap in dados["aparelhos"]:
        if not isinstance(ap, dict):
            raise ValueError("Cada aparelho na lista deve ser um objeto JSON.")
        ap_dict: dict[str, Any] = {
            "identificador": str(ap.get("identificador", "AP")).strip(),
            "descricao": str(ap.get("descricao", "Aparelho")).strip(),
            "quantidade": int(ap.get("quantidade", 1)),
        }
        if "potencia_kw" in ap:
            ap_dict["potencia_kw"] = parsear_fracao_segura(ap["potencia_kw"])
        if "tipo_padrao" in ap:
            ap_dict["tipo_padrao"] = str(ap["tipo_padrao"]).strip()
        aparelhos_processados.append(ap_dict)

    trechos_processados: list[dict[str, Any]] = []
    for tr in dados["trechos"]:
        if not isinstance(tr, dict):
            raise ValueError("Cada trecho na lista deve ser um objeto JSON.")
        if "comprimento_real_m" not in tr:
            raise ValueError("Campo 'comprimento_real_m' é obrigatório no trecho.")
        tr_dict: dict[str, Any] = {
            "identificador": str(tr.get("identificador", "Trecho")).strip(),
            "comprimento_real_m": parsear_fracao_segura(tr["comprimento_real_m"]),
            "tubulacao_codigo": str(tr.get("tubulacao_codigo", "CU_DN22")).strip().upper(),
        }
        if "conexoes" in tr and isinstance(tr["conexoes"], dict):
            tr_dict["conexoes"] = tr["conexoes"]
        if "vazao_m3_h" in tr:
            tr_dict["vazao_m3_h"] = parsear_fracao_segura(tr["vazao_m3_h"])
        trechos_processados.append(tr_dict)

    return {
        "tipo_gas": str(dados["tipo_gas"]).strip().upper(),
        "aparelhos": aparelhos_processados,
        "trechos": trechos_processados,
        "aplicar_fator_simultaneidade": bool(dados.get("aplicar_fator_simultaneidade", True)),
    }


def serializar_resultado_dict(res: ResultadoDimensionamentoRede) -> dict[str, Any]:
    """Serializa o resultado de dimensionamento da rede de gás sem floats."""
    d: dict[str, Any] = {
        "norma": "ABNT NBR 15526:2016",
        "status_global": "APROVADO" if res.aprovado_global else "REPROVADO",
        "resumo": res.resumo_status,
        "gas": {
            "sigla": res.gas.sigla,
            "nome": res.gas.nome,
            "densidade_relativa": fracao_para_str(res.gas.densidade_relativa_ar),
            "pcs_kcal_m3": res.gas.pcs_kcal_m3,
            "pressao_nominal_mmca": res.gas.pressao_nominal_baixa_mmca,
            "perda_carga_maxima_mmca": fracao_para_str(res.gas.perda_carga_maxima_mmca),
        },
        "demanda": {
            "potencia_total_instalada_kw": fracao_para_str(res.potencia_total_instalada_kw),
            "fator_simultaneidade": fracao_para_str(res.fator_simultaneidade),
            "potencia_simultanea_kw": fracao_para_str(res.potencia_simultanea_kw),
            "vazao_total_simultanea_m3_h": fracao_para_str(res.vazao_total_simultanea_m3_h),
        },
        "aparelhos": [
            {
                "identificador": ap.identificador,
                "descricao": ap.descricao,
                "quantidade": ap.quantidade,
                "potencia_unitaria_kw": fracao_para_str(ap.potencia_unitaria_kw),
                "potencia_total_kw": fracao_para_str(ap.potencia_total_kw),
                "vazao_unitaria_m3_h": fracao_para_str(ap.vazao_unitaria_m3_h),
                "vazao_total_m3_h": fracao_para_str(ap.vazao_total_m3_h),
            }
            for ap in res.aparelhos
        ],
        "trechos": [
            {
                "identificador": tr.identificador,
                "tubulacao": tr.tubulacao.codigo,
                "rotulo": tr.tubulacao.rotulo,
                "diametro_interno_mm": fracao_para_str(tr.tubulacao.diametro_interno_mm),
                "comprimento_real_m": fracao_para_str(tr.comprimento_real_m),
                "comprimento_eq_conexoes_m": fracao_para_str(tr.conexoes.comprimento_equivalente_m),
                "comprimento_total_eq_m": fracao_para_str(tr.comprimento_total_equivalente_m),
                "vazao_m3_h": fracao_para_str(tr.vazao_m3_h),
                "perda_carga_trecho_mmca": fracao_para_str(tr.perda_carga_trecho_mmca),
                "velocidade_m_s": fracao_para_str(tr.velocidade_m_s),
                "velocidade_aprovada": tr.velocidade_aprovada,
            }
            for tr in res.trechos
        ],
        "totais_verificacao": {
            "perda_carga_acumulada_mmca": fracao_para_str(res.perda_carga_total_acumulada_mmca),
            "perda_carga_admissivel_mmca": fracao_para_str(res.perda_carga_admissivel_mmca),
            "taxa_perda_carga": fracao_para_str(res.taxa_perda_carga),
            "taxa_perda_carga_percentual": f"{int((res.taxa_perda_carga * 100).numerator // max(1, (res.taxa_perda_carga * 100).denominator))}%",
            "velocidade_maxima_m_s": fracao_para_str(res.velocidade_maxima_m_s),
            "aprovado_perda_carga": res.aprovado_perda_carga,
            "aprovado_velocidade": res.aprovado_velocidade,
            "aprovado_global": res.aprovado_global,
        },
    }
    return d


def exportar_resultado_json(res: ResultadoDimensionamentoRede) -> str:
    """Gera string JSON canônica formatada sem floats."""
    d = serializar_resultado_dict(res)
    return json.dumps(d, indent=2, ensure_ascii=False)
