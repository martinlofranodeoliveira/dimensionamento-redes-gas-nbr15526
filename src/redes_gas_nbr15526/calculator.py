"""Motor analítico de cálculo e dimensionamento de redes internas de gás (NBR 15526).

Todos os cálculos de vazão, perda de carga pela fórmula de Pole e velocidades
operam estritamente em Fraction e inteiros. Banimento total de floats.
"""

from fractions import Fraction
from typing import Final

from .constants import (
    APARELHOS_PADRAO,
    CATALOGO_TUBULACOES,
    CONSTANTE_POLE,
    GASES_COMBUSTIVEIS,
    PERDAS_CONEXOES_COBRE,
    VELOCIDADE_MAXIMA_GAS_M_S,
)
from .models import (
    AparelhoConsumo,
    ConexoesTrecho,
    GasCombustivel,
    ResultadoDimensionamentoRede,
    TrechoRede,
    TubulacaoItem,
)

# Aproximação pi = 355/113
PI_RACIONAL: Final[Fraction] = Fraction(355, 113)


def obter_gas_combustivel(sigla: str) -> GasCombustivel:
    """Valida e recupera as propriedades do gás combustível (GN ou GLP)."""
    chave = sigla.strip().upper()
    if chave not in GASES_COMBUSTIVEIS:
        opcoes = ", ".join(sorted(GASES_COMBUSTIVEIS.keys()))
        raise ValueError(f"Gás '{sigla}' não reconhecido. Opções normativas: {opcoes}")

    info = GASES_COMBUSTIVEIS[chave]
    return GasCombustivel(
        sigla=chave,  # type: ignore[arg-type]
        nome=str(info["nome"]),
        densidade_relativa_ar=Fraction(info["densidade_relativa_ar"]),  # type: ignore[arg-type]
        pcs_kcal_m3=int(info["pcs_kcal_m3"]),
        pressao_nominal_baixa_mmca=int(info["pressao_nominal_baixa_mmca"]),
        perda_carga_maxima_mmca=Fraction(info["perda_carga_maxima_mmca"]),  # type: ignore[arg-type]
    )


def obter_tubulacao_catalogo(codigo: str) -> TubulacaoItem:
    """Recupera tubo comercial e seu diâmetro interno a partir do catálogo."""
    chave = codigo.strip().upper()
    if chave not in CATALOGO_TUBULACOES:
        opcoes = ", ".join(sorted(CATALOGO_TUBULACOES.keys()))
        raise ValueError(f"Tubulação '{codigo}' não encontrada no catálogo. Opções: {opcoes}")

    info = CATALOGO_TUBULACOES[chave]
    return TubulacaoItem(
        codigo=chave,
        tipo=str(info["tipo"]),  # type: ignore[arg-type]
        rotulo=str(info["rotulo"]),
        diametro_externo_mm=Fraction(info["diametro_externo_mm"]),
        espessura_mm=Fraction(info["espessura_mm"]),
        diametro_interno_mm=Fraction(info["diametro_interno_mm"]),
    )


def calcular_vazao_aparelho(potencia_kw: Fraction, gas: GasCombustivel) -> Fraction:
    """Calcula a vazão nominal de um aparelho em m³/h a partir da potência em kW.

    1 kW = 860 kcal/h.
    Vazão (m³/h) = (Potência em kW * 860) / PCS
    """
    if potencia_kw < 0:
        raise ValueError("Potência do aparelho não pode ser negativa.")
    kcal_h = potencia_kw * 860
    return kcal_h / Fraction(gas.pcs_kcal_m3, 1)


def calcular_fator_simultaneidade(num_aparelhos: int) -> Fraction:
    """Calcula o fator de simultaneidade F para rede residencial (ABNT NBR 15526)."""
    if num_aparelhos <= 0:
        return Fraction(0, 1)
    if num_aparelhos <= 2:
        return Fraction(1, 1)
    if num_aparelhos == 3:
        return Fraction(85, 100)      # 0,85
    if num_aparelhos == 4:
        return Fraction(75, 100)      # 0,75
    if num_aparelhos <= 6:
        return Fraction(65, 100)      # 0,65
    if num_aparelhos <= 10:
        return Fraction(55, 100)      # 0,55
    if num_aparelhos <= 20:
        return Fraction(45, 100)      # 0,45
    return Fraction(35, 100)          # 0,35


def calcular_comprimento_equivalente_conexoes(
    tubo_codigo: str, conexoes: ConexoesTrecho
) -> Fraction:
    """Calcula o comprimento equivalente total em metros das conexões de um trecho."""
    codigo = tubo_codigo.strip().upper()
    tabela = PERDAS_CONEXOES_COBRE.get(codigo)
    if tabela is None:
        # Se for aço ou outro tubo sem tabela específica, adota tabela padrão proporcional
        return (
            Fraction(conexoes.joelho_90, 1) * Fraction(7, 10)
            + Fraction(conexoes.joelho_45, 1) * Fraction(3, 10)
            + Fraction(conexoes.te_passagem_direta, 1) * Fraction(3, 10)
            + Fraction(conexoes.te_saida_lateral, 1) * Fraction(12, 10)
            + Fraction(conexoes.valvula_esfera, 1) * Fraction(2, 10)
        )

    comp_eq = (
        Fraction(conexoes.joelho_90, 1) * tabela["joelho_90"]
        + Fraction(conexoes.joelho_45, 1) * tabela["joelho_45"]
        + Fraction(conexoes.te_passagem_direta, 1) * tabela["te_passagem_direta"]
        + Fraction(conexoes.te_saida_lateral, 1) * tabela["te_saida_lateral"]
        + Fraction(conexoes.valvula_esfera, 1) * tabela["valvula_esfera"]
    )
    return comp_eq


def calcular_perda_carga_pole(
    vazao_m3_h: Fraction,
    diametro_interno_mm: Fraction,
    comprimento_total_m: Fraction,
    densidade_relativa: Fraction,
) -> Fraction:
    """Calcula a perda de carga em baixa pressão (mmca) pela Fórmula de Pole.

    Delta_H (mmca) = (22222 * d_r * L_eq * Q^2) / D^5
    """
    if vazao_m3_h <= 0 or comprimento_total_m <= 0:
        return Fraction(0, 1)
    if diametro_interno_mm <= 0:
        raise ValueError("Diâmetro interno deve ser estritamente positivo.")

    numerador = CONSTANTE_POLE * densidade_relativa * comprimento_total_m * (vazao_m3_h ** 2)
    denominador = diametro_interno_mm ** 5
    return numerador / denominador


def calcular_velocidade_gas(vazao_m3_h: Fraction, diametro_interno_mm: Fraction) -> Fraction:
    """Calcula a velocidade média do gás na tubulação em m/s.

    V = (Q / 3600) / (pi * (D/1000)^2 / 4) = (Q * 10000) / (9 * pi * D^2)
    """
    if vazao_m3_h <= 0:
        return Fraction(0, 1)
    if diametro_interno_mm <= 0:
        raise ValueError("Diâmetro interno deve ser estritamente positivo.")

    # V = (Q * 10000) / (9 * pi * D^2)
    num = vazao_m3_h * 10000
    den = Fraction(9, 1) * PI_RACIONAL * (diametro_interno_mm ** 2)
    return num / den


def dimensionar_rede_gas(
    tipo_gas: str,
    aparelhos_entrada: list[dict[str, str | int | Fraction]],
    trechos_entrada: list[dict[str, str | int | Fraction]],
    aplicar_fator_simultaneidade: bool = True,
) -> ResultadoDimensionamentoRede:
    """Executa o dimensionamento e a verificação completa de uma rede interna de gás."""
    gas = obter_gas_combustivel(tipo_gas)

    # 1. Processar Aparelhos de Consumo
    aparelhos: list[AparelhoConsumo] = []
    potencia_total_kw = Fraction(0, 1)
    total_unidades = 0

    for idx, ap in enumerate(aparelhos_entrada):
        ident = str(ap.get("identificador", f"AP_{idx + 1}")).strip()
        desc = str(ap.get("descricao", "Aparelho a Gás")).strip()
        qtd = int(ap.get("quantidade", 1))
        if qtd <= 0:
            raise ValueError(f"Quantidade do aparelho '{ident}' deve ser >= 1.")

        # Potência em kW
        pot_kw_raw = ap.get("potencia_kw")
        if pot_kw_raw is not None:
            pot_un_kw = Fraction(pot_kw_raw)  # type: ignore[arg-type]
        else:
            tipo_padrao = str(ap.get("tipo_padrao", "")).strip().lower()
            if tipo_padrao in APARELHOS_PADRAO:
                pot_un_kw = Fraction(APARELHOS_PADRAO[tipo_padrao]["potencia_kw"], 1)
                desc = str(APARELHOS_PADRAO[tipo_padrao]["descricao"])
            else:
                raise ValueError(
                    f"Aparelho '{ident}' precisa especificar 'potencia_kw' ou 'tipo_padrao' válido."
                )

        pot_tot_kw = pot_un_kw * qtd
        vazao_un_m3_h = calcular_vazao_aparelho(pot_un_kw, gas)
        vazao_tot_m3_h = vazao_un_m3_h * qtd

        aparelhos.append(
            AparelhoConsumo(
                identificador=ident,
                descricao=desc,
                quantidade=qtd,
                potencia_unitaria_kw=pot_un_kw,
                potencia_total_kw=pot_tot_kw,
                vazao_unitaria_m3_h=vazao_un_m3_h,
                vazao_total_m3_h=vazao_tot_m3_h,
            )
        )
        potencia_total_kw += pot_tot_kw
        total_unidades += qtd

    fator_simult = (
        calcular_fator_simultaneidade(total_unidades)
        if aplicar_fator_simultaneidade
        else Fraction(1, 1)
    )
    potencia_simult_kw = potencia_total_kw * fator_simult
    vazao_total_simult_m3_h = calcular_vazao_aparelho(potencia_simult_kw, gas)

    # 2. Processar e Dimensionar Trechos da Tubulação
    trechos_processados: list[TrechoRede] = []
    perda_carga_acumulada_mmca = Fraction(0, 1)
    velocidades: list[Fraction] = []

    for tr in trechos_entrada:
        ident_tr = str(tr.get("identificador", "Trecho")).strip()
        comp_real = Fraction(tr.get("comprimento_real_m", 0))  # type: ignore[arg-type]
        if comp_real <= 0:
            raise ValueError(f"Comprimento do trecho '{ident_tr}' deve ser > 0.")

        cod_tubo = str(tr.get("tubulacao_codigo", "CU_DN22")).strip().upper()
        tubo = obter_tubulacao_catalogo(cod_tubo)

        # Conexões
        conexoes_raw = tr.get("conexoes", {})
        if isinstance(conexoes_raw, dict):
            conexoes = ConexoesTrecho(
                joelho_90=int(conexoes_raw.get("joelho_90", 0)),
                joelho_45=int(conexoes_raw.get("joelho_45", 0)),
                te_passagem_direta=int(conexoes_raw.get("te_passagem_direta", 0)),
                te_saida_lateral=int(conexoes_raw.get("te_saida_lateral", 0)),
                valvula_esfera=int(conexoes_raw.get("valvula_esfera", 0)),
            )
        else:
            conexoes = ConexoesTrecho()

        comp_eq_conexoes = calcular_comprimento_equivalente_conexoes(tubo.codigo, conexoes)
        conexoes_com_eq = ConexoesTrecho(
            joelho_90=conexoes.joelho_90,
            joelho_45=conexoes.joelho_45,
            te_passagem_direta=conexoes.te_passagem_direta,
            te_saida_lateral=conexoes.te_saida_lateral,
            valvula_esfera=conexoes.valvula_esfera,
            comprimento_equivalente_m=comp_eq_conexoes,
        )

        comp_total_eq = comp_real + comp_eq_conexoes

        # Vazão do trecho: se especificada, usa ela; se omitida, usa a vazão total simultânea
        vazao_trecho_raw = tr.get("vazao_m3_h")
        if vazao_trecho_raw is not None:
            vazao_trecho = Fraction(vazao_trecho_raw)  # type: ignore[arg-type]
        else:
            vazao_trecho = vazao_total_simult_m3_h

        # Perda de carga pela Fórmula de Pole
        perda_trecho_mmca = calcular_perda_carga_pole(
            vazao_m3_h=vazao_trecho,
            diametro_interno_mm=tubo.diametro_interno_mm,
            comprimento_total_m=comp_total_eq,
            densidade_relativa=gas.densidade_relativa_ar,
        )

        # Velocidade do gás
        velocidade = calcular_velocidade_gas(vazao_trecho, tubo.diametro_interno_mm)
        velocidade_ok = velocidade <= VELOCIDADE_MAXIMA_GAS_M_S

        trecho_obj = TrechoRede(
            identificador=ident_tr,
            comprimento_real_m=comp_real,
            tubulacao=tubo,
            conexoes=conexoes_com_eq,
            vazao_m3_h=vazao_trecho,
            comprimento_total_equivalente_m=comp_total_eq,
            perda_carga_trecho_mmca=perda_trecho_mmca,
            velocidade_m_s=velocidade,
            velocidade_aprovada=velocidade_ok,
        )
        trechos_processados.append(trecho_obj)
        perda_carga_acumulada_mmca += perda_trecho_mmca
        velocidades.append(velocidade)

    velocidade_maxima = max(velocidades) if velocidades else Fraction(0, 1)
    taxa_perda = (
        perda_carga_acumulada_mmca / gas.perda_carga_maxima_mmca
        if gas.perda_carga_maxima_mmca > 0
        else Fraction(999, 1)
    )

    aprovado_perda = perda_carga_acumulada_mmca <= gas.perda_carga_maxima_mmca
    aprovado_vel = all(tr.velocidade_aprovada for tr in trechos_processados)
    aprovado_global = aprovado_perda and aprovado_vel

    if aprovado_global:
        pct = (taxa_perda * 100).numerator // max(1, (taxa_perda * 100).denominator)
        resumo = f"APROVADO: Rede atende aos limites da NBR 15526 (perda acumulada: {pct}% do limite, vel máx: {(velocidade_maxima).numerator // max(1, velocidade_maxima.denominator)} m/s)."
    elif not aprovado_perda:
        resumo = f"REPROVADO: Perda de carga acumulada ({perda_carga_acumulada_mmca} mmca) excede o limite normativo ({gas.perda_carga_maxima_mmca} mmca)."
    else:
        resumo = f"REPROVADO: Velocidade do gás excede o limite normativo ({VELOCIDADE_MAXIMA_GAS_M_S} m/s)."

    return ResultadoDimensionamentoRede(
        gas=gas,
        aparelhos=aparelhos,
        potencia_total_instalada_kw=potencia_total_kw,
        fator_simultaneidade=fator_simult,
        potencia_simultanea_kw=potencia_simult_kw,
        vazao_total_simultanea_m3_h=vazao_total_simult_m3_h,
        trechos=trechos_processados,
        perda_carga_total_acumulada_mmca=perda_carga_acumulada_mmca,
        perda_carga_admissivel_mmca=gas.perda_carga_maxima_mmca,
        taxa_perda_carga=taxa_perda,
        velocidade_maxima_m_s=velocidade_maxima,
        aprovado_perda_carga=aprovado_perda,
        aprovado_velocidade=aprovado_vel,
        aprovado_global=aprovado_global,
        resumo_status=resumo,
    )
