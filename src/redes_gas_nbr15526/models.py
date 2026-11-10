"""Modelos de dados imutáveis para dimensionamento de redes internas de gás (NBR 15526).

Todas as grandezas físicas (vazões, pressões, perdas de carga, velocidades)
operam com Fraction ou inteiros, eliminando floats e arredondamentos imprecisos.
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Final, Literal


@dataclass(frozen=True)
class GasCombustivel:
    """Propriedades do gás combustível (GN ou GLP)."""

    sigla: Literal["GN", "GLP"]
    nome: str
    densidade_relativa_ar: Fraction
    pcs_kcal_m3: int
    pressao_nominal_baixa_mmca: int
    perda_carga_maxima_mmca: Fraction


@dataclass(frozen=True)
class AparelhoConsumo:
    """Aparelho a gás e sua respectiva potência e vazão de consumo."""

    identificador: str
    descricao: str
    quantidade: int
    potencia_unitaria_kw: Fraction
    potencia_total_kw: Fraction
    vazao_unitaria_m3_h: Fraction
    vazao_total_m3_h: Fraction


@dataclass(frozen=True)
class TubulacaoItem:
    """Tubo comercial normatizado e seu diâmetro interno exato."""

    codigo: str
    tipo: Literal["cobre", "aco_carbono"]
    rotulo: str
    diametro_externo_mm: Fraction
    espessura_mm: Fraction
    diametro_interno_mm: Fraction

    @property
    def area_interna_mm2(self) -> Fraction:
        """Área interna da seção transversal em mm² (pi * D² / 4)."""
        # Aproximação pi = 355/113
        pi_frac = Fraction(355, 113)
        return pi_frac * (self.diametro_interno_mm ** 2) / 4


@dataclass(frozen=True)
class ConexoesTrecho:
    """Quantitativo de conexões e acessórios em um trecho de tubulação."""

    joelho_90: int = 0
    joelho_45: int = 0
    te_passagem_direta: int = 0
    te_saida_lateral: int = 0
    valvula_esfera: int = 0
    comprimento_equivalente_m: Fraction = Fraction(0, 1)


@dataclass(frozen=True)
class TrechoRede:
    """Trecho de tubulação com parâmetros hidráulicos calculados."""

    identificador: str
    comprimento_real_m: Fraction
    tubulacao: TubulacaoItem
    conexoes: ConexoesTrecho
    vazao_m3_h: Fraction
    comprimento_total_equivalente_m: Fraction
    perda_carga_trecho_mmca: Fraction
    velocidade_m_s: Fraction
    velocidade_aprovada: bool


@dataclass(frozen=True)
class ResultadoDimensionamentoRede:
    """Resultado analítico consolidado do dimensionamento da rede de gás."""

    gas: GasCombustivel
    aparelhos: list[AparelhoConsumo]
    potencia_total_instalada_kw: Fraction
    fator_simultaneidade: Fraction
    potencia_simultanea_kw: Fraction
    vazao_total_simultanea_m3_h: Fraction
    trechos: list[TrechoRede]
    perda_carga_total_acumulada_mmca: Fraction
    perda_carga_admissivel_mmca: Fraction
    taxa_perda_carga: Fraction
    velocidade_maxima_m_s: Fraction
    aprovado_perda_carga: bool
    aprovado_velocidade: bool
    aprovado_global: bool
    resumo_status: str
