"""Constantes normativas e propriedades físicas dos gases e tubulações (NBR 15526).

Todas as grandezas de cálculo operam com Fraction e tipos inteiros,
eliminando estritamente qualquer aproximação por ponto flutuante (float).
"""

from fractions import Fraction
from typing import Final

# ---------------------------------------------------------------------------
# Propriedades Físicas dos Gases Combustíveis (ABNT NBR 15526)
# ---------------------------------------------------------------------------

GASES_COMBUSTIVEIS: Final[dict[str, dict[str, Fraction | int | str]]] = {
    "GN": {
        "nome": "Gás Natural",
        "sigla": "GN",
        "densidade_relativa_ar": Fraction(60, 100),       # 0,60 (adimensional em relação ao ar)
        "pcs_kcal_m3": 9400,                              # Poder Calorífico Superior (kcal/m³)
        "pressao_nominal_baixa_mmca": 200,                # 200 mmca = 2,0 kPa (20 mbar)
        "perda_carga_maxima_mmca": Fraction(25, 1),       # 25 mmca (limite normativo usual ~ 10% de P)
    },
    "GLP": {
        "nome": "Gás Liquefeito de Petróleo (Vapor)",
        "sigla": "GLP",
        "densidade_relativa_ar": Fraction(152, 100),      # 1,52 (adimensional)
        "pcs_kcal_m3": 24000,                             # Poder Calorífico Superior (kcal/m³)
        "pressao_nominal_baixa_mmca": 280,                # 280 mmca = 2,8 kPa (28 mbar)
        "perda_carga_maxima_mmca": Fraction(28, 1),       # 28 mmca (~ 10% de P)
    },
}

# ---------------------------------------------------------------------------
# Aparelhos a Gás e Potências Nominais Usuais (kW e kcal/h)
# 1 kW = 860 kcal/h
# ---------------------------------------------------------------------------

APARELHOS_PADRAO: Final[dict[str, dict[str, str | int]]] = {
    "fogao_4_bocas": {
        "descricao": "Fogão doméstico 4 bocas com forno",
        "potencia_kw": 7,
        "potencia_kcal_h": 6020,
    },
    "fogao_5_bocas": {
        "descricao": "Fogão doméstico 5 bocas com forno",
        "potencia_kw": 10,
        "potencia_kcal_h": 8600,
    },
    "fogao_6_bocas": {
        "descricao": "Fogão doméstico 6 bocas com forno",
        "potencia_kw": 11,
        "potencia_kcal_h": 9460,
    },
    "cooktop_4_bocas": {
        "descricao": "Mesa de cocção (cooktop) 4 bocas",
        "potencia_kw": 6,
        "potencia_kcal_h": 5160,
    },
    "cooktop_5_bocas": {
        "descricao": "Mesa de cocção (cooktop) 5 bocas",
        "potencia_kw": 8,
        "potencia_kcal_h": 6880,
    },
    "forno_embutir": {
        "descricao": "Forno de embutir a gás",
        "potencia_kw": 3,
        "potencia_kcal_h": 2580,
    },
    "aquecedor_passagem_15l": {
        "descricao": "Aquecedor de passagem 15 L/min",
        "potencia_kw": 21,
        "potencia_kcal_h": 18060,
    },
    "aquecedor_passagem_20l": {
        "descricao": "Aquecedor de passagem 20 L/min",
        "potencia_kw": 28,
        "potencia_kcal_h": 24080,
    },
    "aquecedor_passagem_30l": {
        "descricao": "Aquecedor de passagem 30 L/min",
        "potencia_kw": 42,
        "potencia_kcal_h": 36120,
    },
    "aquecedor_acumulacao_100l": {
        "descricao": "Aquecedor por acumulação 100 L",
        "potencia_kw": 8,
        "potencia_kcal_h": 6880,
    },
}

# ---------------------------------------------------------------------------
# Catálogo de Tubulações Comerciais Normatizadas (NBR 13206 e NBR 5580)
# Diâmetros internos em mm expressos em frações exatas
# ---------------------------------------------------------------------------

# Tubos de Cobre Rígido Classe A (ABNT NBR 13206)
TUBOS_COBRE_CLASSE_A: Final[dict[str, dict[str, str | Fraction]]] = {
    "CU_DN15": {
        "tipo": "cobre",
        "rotulo": "Cobre DN 15 (15 mm)",
        "diametro_externo_mm": Fraction(15, 1),
        "espessura_mm": Fraction(1, 1),
        "diametro_interno_mm": Fraction(13, 1),           # 15 - 2*1 = 13 mm
    },
    "CU_DN22": {
        "tipo": "cobre",
        "rotulo": "Cobre DN 22 (22 mm)",
        "diametro_externo_mm": Fraction(22, 1),
        "espessura_mm": Fraction(11, 10),
        "diametro_interno_mm": Fraction(99, 5),          # 22 - 2*1.1 = 19.8 mm
    },
    "CU_DN28": {
        "tipo": "cobre",
        "rotulo": "Cobre DN 28 (28 mm)",
        "diametro_externo_mm": Fraction(28, 1),
        "espessura_mm": Fraction(12, 10),
        "diametro_interno_mm": Fraction(128, 5),         # 28 - 2*1.2 = 25.6 mm
    },
    "CU_DN35": {
        "tipo": "cobre",
        "rotulo": "Cobre DN 35 (35 mm)",
        "diametro_externo_mm": Fraction(35, 1),
        "espessura_mm": Fraction(14, 10),
        "diametro_interno_mm": Fraction(161, 5),         # 35 - 2*1.4 = 32.2 mm
    },
    "CU_DN42": {
        "tipo": "cobre",
        "rotulo": "Cobre DN 42 (42 mm)",
        "diametro_externo_mm": Fraction(42, 1),
        "espessura_mm": Fraction(14, 10),
        "diametro_interno_mm": Fraction(196, 5),         # 42 - 2*1.4 = 39.2 mm
    },
    "CU_DN54": {
        "tipo": "cobre",
        "rotulo": "Cobre DN 54 (54 mm)",
        "diametro_externo_mm": Fraction(54, 1),
        "espessura_mm": Fraction(15, 10),
        "diametro_interno_mm": Fraction(51, 1),          # 54 - 2*1.5 = 51.0 mm
    },
}

# Tubos de Aço-Carbono Médio (ABNT NBR 5580 Classe Média)
TUBOS_ACO_CARBONO: Final[dict[str, dict[str, str | Fraction]]] = {
    "ACO_1/2": {
        "tipo": "aco_carbono",
        "rotulo": "Aço 1/2 pol (DN 15)",
        "diametro_externo_mm": Fraction(213, 10),
        "espessura_mm": Fraction(265, 100),
        "diametro_interno_mm": Fraction(16, 1),           # ~ 16.0 mm
    },
    "ACO_3/4": {
        "tipo": "aco_carbono",
        "rotulo": "Aço 3/4 pol (DN 20)",
        "diametro_externo_mm": Fraction(269, 10),
        "espessura_mm": Fraction(265, 100),
        "diametro_interno_mm": Fraction(216, 10),         # ~ 21.6 mm
    },
    "ACO_1": {
        "tipo": "aco_carbono",
        "rotulo": "Aço 1 pol (DN 25)",
        "diametro_externo_mm": Fraction(337, 10),
        "espessura_mm": Fraction(335, 100),
        "diametro_interno_mm": Fraction(27, 1),           # ~ 27.0 mm
    },
    "ACO_1.1/4": {
        "tipo": "aco_carbono",
        "rotulo": "Aço 1.1/4 pol (DN 32)",
        "diametro_externo_mm": Fraction(424, 10),
        "espessura_mm": Fraction(335, 100),
        "diametro_interno_mm": Fraction(357, 10),         # ~ 35.7 mm
    },
    "ACO_1.1/2": {
        "tipo": "aco_carbono",
        "rotulo": "Aço 1.1/2 pol (DN 40)",
        "diametro_externo_mm": Fraction(483, 10),
        "espessura_mm": Fraction(335, 100),
        "diametro_interno_mm": Fraction(416, 10),         # ~ 41.6 mm
    },
    "ACO_2": {
        "tipo": "aco_carbono",
        "rotulo": "Aço 2 pol (DN 50)",
        "diametro_externo_mm": Fraction(603, 10),
        "espessura_mm": Fraction(375, 100),
        "diametro_interno_mm": Fraction(528, 10),         # ~ 52.8 mm
    },
}

# Catálogo consolidado de tubulações
CATALOGO_TUBULACOES: Final[dict[str, dict[str, str | Fraction]]] = {
    **TUBOS_COBRE_CLASSE_A,
    **TUBOS_ACO_CARBONO,
}

# ---------------------------------------------------------------------------
# Comprimentos Equivalentes de Conexões em Metros (ABNT NBR 15526)
# Mapeados por código de tubo comercial
# ---------------------------------------------------------------------------

PERDAS_CONEXOES_COBRE: Final[dict[str, dict[str, Fraction]]] = {
    "CU_DN15": {
        "joelho_90": Fraction(5, 10),
        "joelho_45": Fraction(2, 10),
        "te_passagem_direta": Fraction(2, 10),
        "te_saida_lateral": Fraction(8, 10),
        "valvula_esfera": Fraction(1, 10),
    },
    "CU_DN22": {
        "joelho_90": Fraction(7, 10),
        "joelho_45": Fraction(3, 10),
        "te_passagem_direta": Fraction(3, 10),
        "te_saida_lateral": Fraction(12, 10),
        "valvula_esfera": Fraction(2, 10),
    },
    "CU_DN28": {
        "joelho_90": Fraction(9, 10),
        "joelho_45": Fraction(4, 10),
        "te_passagem_direta": Fraction(4, 10),
        "te_saida_lateral": Fraction(16, 10),
        "valvula_esfera": Fraction(2, 10),
    },
    "CU_DN35": {
        "joelho_90": Fraction(12, 10),
        "joelho_45": Fraction(5, 10),
        "te_passagem_direta": Fraction(5, 10),
        "te_saida_lateral": Fraction(21, 10),
        "valvula_esfera": Fraction(3, 10),
    },
    "CU_DN42": {
        "joelho_90": Fraction(15, 10),
        "joelho_45": Fraction(6, 10),
        "te_passagem_direta": Fraction(6, 10),
        "te_saida_lateral": Fraction(26, 10),
        "valvula_esfera": Fraction(4, 10),
    },
    "CU_DN54": {
        "joelho_90": Fraction(19, 10),
        "joelho_45": Fraction(8, 10),
        "te_passagem_direta": Fraction(8, 10),
        "te_saida_lateral": Fraction(34, 10),
        "valvula_esfera": Fraction(5, 10),
    },
}

# Limite de velocidade do gás na tubulação
VELOCIDADE_MAXIMA_GAS_M_S: Final[Fraction] = Fraction(20, 1)      # 20 m/s
VELOCIDADE_RECOMENDADA_M_S: Final[Fraction] = Fraction(15, 1)     # 15 m/s

# Constante de Pole para perda de carga em baixa pressão (P <= 5 kPa)
# Delta_P (mmca) = (K_POLE * d_r * L_eq * Q^2) / D^5
# Onde Q é vazão em m³/h, L_eq em m, D em mm, d_r em relação ao ar
CONSTANTE_POLE: Final[Fraction] = Fraction(22222, 1)
