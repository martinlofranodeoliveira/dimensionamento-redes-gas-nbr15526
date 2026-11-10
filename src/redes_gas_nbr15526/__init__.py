"""Pacote de dimensionamento analítico de redes internas de gás conforme ABNT NBR 15526.

Padrão LOFRANO TECNOLOGIA:
- Aritmética racional exata com Fraction
- Zero dependências de terceiros
- Zero floats
"""

from .calculator import (
    calcular_comprimento_equivalente_conexoes,
    calcular_fator_simultaneidade,
    calcular_perda_carga_pole,
    calcular_vazao_aparelho,
    calcular_velocidade_gas,
    dimensionar_rede_gas,
    obter_gas_combustivel,
    obter_tubulacao_catalogo,
)
from .codecs import (
    carregar_entrada_json,
    exportar_resultado_json,
    fracao_para_str,
    parsear_fracao_segura,
    parsear_json_seguro,
)
from .constants import (
    APARELHOS_PADRAO,
    CATALOGO_TUBULACOES,
    CONSTANTE_POLE,
    GASES_COMBUSTIVEIS,
    PERDAS_CONEXOES_COBRE,
    TUBOS_ACO_CARBONO,
    TUBOS_COBRE_CLASSE_A,
    VELOCIDADE_MAXIMA_GAS_M_S,
)
from .exporters import (
    gerar_csv_sanitizado,
    gerar_pacote_zip_deterministico,
    gerar_relatorio_texto,
)
from .models import (
    AparelhoConsumo,
    ConexoesTrecho,
    GasCombustivel,
    ResultadoDimensionamentoRede,
    TrechoRede,
    TubulacaoItem,
)
from .svg_generator import gerar_painel_svg

__version__ = "1.0.0"
VERSAO = "1.0.0"

__all__ = [
    "__version__",
    "VERSAO",
    "dimensionar_rede_gas",
    "obter_gas_combustivel",
    "obter_tubulacao_catalogo",
    "calcular_vazao_aparelho",
    "calcular_fator_simultaneidade",
    "calcular_comprimento_equivalente_conexoes",
    "calcular_perda_carga_pole",
    "calcular_velocidade_gas",
    "carregar_entrada_json",
    "exportar_resultado_json",
    "parsear_fracao_segura",
    "parsear_json_seguro",
    "fracao_para_str",
    "gerar_relatorio_texto",
    "gerar_csv_sanitizado",
    "gerar_pacote_zip_deterministico",
    "gerar_painel_svg",
    "GasCombustivel",
    "AparelhoConsumo",
    "TubulacaoItem",
    "ConexoesTrecho",
    "TrechoRede",
    "ResultadoDimensionamentoRede",
    "GASES_COMBUSTIVEIS",
    "APARELHOS_PADRAO",
    "CATALOGO_TUBULACOES",
    "TUBOS_COBRE_CLASSE_A",
    "TUBOS_ACO_CARBONO",
    "PERDAS_CONEXOES_COBRE",
    "CONSTANTE_POLE",
    "VELOCIDADE_MAXIMA_GAS_M_S",
]
