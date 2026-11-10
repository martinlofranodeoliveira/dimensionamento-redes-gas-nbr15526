"""Gerador de painel técnico visual em SVG (1440x900) para redes de gás (NBR 15526).

Conforme o padrão LOFRANO TECNOLOGIA:
- Painel vetorial autossuficiente e escalável
- Esquema de cores dark theme com tubulações em amarelo segurança (NBR 6493)
- Diagrama isométrico da instalação, medidor, aparelhos (fogão e aquecedor), perdas e velocidades
- Cards analíticos com barras de taxa de perda de carga
"""

from fractions import Fraction

from .codecs import fracao_para_str
from .exporters import formatar_taxa_pct
from .models import ResultadoDimensionamentoRede


def gerar_painel_svg(res: ResultadoDimensionamentoRede) -> str:
    """Gera documento SVG em 1440x900 detalhando o dimensionamento da rede de gás."""
    largura = 1440
    altura = 900

    cor_fundo = "#0d1117"
    cor_card = "#161b22"
    cor_borda = "#30363d"
    cor_texto_principal = "#f0f6fc"
    cor_texto_secundario = "#8b949e"
    cor_tubo_gas = "#f1e05a"        # Amarelo gás padrão NBR 6493
    cor_tubo_sombra = "#b89e14"
    cor_chama = "#ff7b72"
    cor_acento = "#58a6ff"
    cor_sucesso = "#3fb950"
    cor_perigo = "#f85149"
    cor_aviso = "#d29922"

    status_cor = cor_sucesso if res.aprovado_global else cor_perigo
    status_texto = "APROVADO" if res.aprovado_global else "REPROVADO"

    linhas_svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {altura}" width="{largura}" height="{altura}">',
        f'  <defs>',
        f'    <linearGradient id="gradFundo" x1="0%" y1="0%" x2="100%" y2="100%">',
        f'      <stop offset="0%" stop-color="#090d12"/>',
        f'      <stop offset="100%" stop-color="#121820"/>',
        f'    </linearGradient>',
        f'    <linearGradient id="gradTubo" x1="0%" y1="0%" x2="0%" y2="100%">',
        f'      <stop offset="0%" stop-color="#fff59d"/>',
        f'      <stop offset="40%" stop-color="{cor_tubo_gas}"/>',
        f'      <stop offset="100%" stop-color="{cor_tubo_sombra}"/>',
        f'    </linearGradient>',
        f'    <filter id="sombraCard" x="-10%" y="-10%" width="120%" height="120%">',
        f'      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000" flood-opacity="0.3"/>',
        f'    </filter>',
        f'  </defs>',
        f'  <!-- Fundo Principal -->',
        f'  <rect width="{largura}" height="{altura}" fill="url(#gradFundo)"/>',
        f'',
        f'  <!-- Cabeçalho -->',
        f'  <rect x="40" y="30" width="1360" height="90" rx="12" fill="{cor_card}" stroke="{cor_borda}" stroke-width="1" filter="url(#sombraCard)"/>',
        f'  <text x="70" y="65" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="700" fill="{cor_acento}" letter-spacing="1.5">LOFRANO TECNOLOGIA · INSTALAÇÕES PREDIAIS DE GÁS</text>',
        f'  <text x="70" y="96" font-family="system-ui, -apple-system, sans-serif" font-size="22" font-weight="700" fill="{cor_texto_principal}">DIMENSIONAMENTO DE REDES INTERNAS DE GASES COMBUSTÍVEIS · ABNT NBR 15526</text>',
        f'  <rect x="1220" y="50" width="150" height="48" rx="8" fill="{status_cor}" fill-opacity="0.15" stroke="{status_cor}" stroke-width="1.5"/>',
        f'  <text x="1295" y="80" font-family="system-ui, -apple-system, sans-serif" font-size="16" font-weight="800" fill="{status_cor}" text-anchor="middle">{status_texto}</text>',
        f'',
        f'  <!-- Painel Esquerdo: Esquema Isométrico da Rede de Gás -->',
        f'  <rect x="40" y="140" width="840" height="470" rx="12" fill="{cor_card}" stroke="{cor_borda}" stroke-width="1" filter="url(#sombraCard)"/>',
        f'  <text x="70" y="175" font-family="system-ui, -apple-system, sans-serif" font-size="15" font-weight="700" fill="{cor_texto_principal}">ESQUEMA ISOMÉTRICO DA REDE DE DISTRIBUIÇÃO</text>',
        f'  <text x="70" y="195" font-family="system-ui, -apple-system, sans-serif" font-size="12" fill="{cor_texto_secundario}">Gás: {res.gas.nome} ({res.gas.sigla}) · Fórmula de Pole (Baixa Pressão) · Tubos de Cobre/Aço</text>',
        f'',
        f'  <!-- Desenho Isométrico Estilizado da Rede de Gás -->',
        f'  <g transform="translate(80, 220)">',
        f'    <!-- Medidor / Regulador (Ponto Inicial A) -->',
        f'    <rect x="20" y="150" width="60" height="80" rx="6" fill="#21262d" stroke="{cor_acento}" stroke-width="2"/>',
        f'    <circle cx="50" cy="180" r="16" fill="#161b22" stroke="{cor_borda}" stroke-width="1.5"/>',
        f'    <line x1="50" y1="180" x2="58" y2="172" stroke="{cor_acento}" stroke-width="2"/>',
        f'    <text x="50" y="215" font-family="system-ui, sans-serif" font-size="9" font-weight="700" fill="{cor_texto_principal}" text-anchor="middle">MEDIDOR</text>',
        f'    <text x="50" y="140" font-family="system-ui, sans-serif" font-size="12" font-weight="800" fill="{cor_acento}" text-anchor="middle">Ponto A</text>',
        f'',
        f'    <!-- Tubulação Principal: A até Derivação B -->',
        f'    <line x1="80" y1="190" x2="280" y2="190" stroke="url(#gradTubo)" stroke-width="10" stroke-linecap="round"/>',
        f'    <!-- Cotas do Trecho A-B -->',
        f'    <text x="180" y="175" font-family="system-ui, sans-serif" font-size="11" font-weight="700" fill="{cor_tubo_gas}" text-anchor="middle">Trecho Principal (A-B)</text>',
        f'    <text x="180" y="215" font-family="system-ui, sans-serif" font-size="10" fill="{cor_texto_secundario}" text-anchor="middle">Q_simult = {fracao_para_str(res.vazao_total_simultanea_m3_h)} m³/h</text>',
        f'',
        f'    <!-- Derivação B (Tê de gás) -->',
        f'    <circle cx="280" cy="190" r="8" fill="{cor_tubo_sombra}" stroke="#fff" stroke-width="2"/>',
        f'    <text x="280" y="215" font-family="system-ui, sans-serif" font-size="12" font-weight="800" fill="{cor_acento}" text-anchor="middle">B</text>',
        f'',
        f'    <!-- Ramal 1: B sobe até Aquecedor de Água -->',
        f'    <line x1="280" y1="190" x2="280" y2="70" stroke="url(#gradTubo)" stroke-width="8" stroke-linecap="round"/>',
        f'    <line x1="280" y1="70" x2="480" y2="70" stroke="url(#gradTubo)" stroke-width="8" stroke-linecap="round"/>',
        f'    <!-- Bloco Aquecedor de Água -->',
        f'    <rect x="480" y="30" width="80" height="90" rx="6" fill="#21262d" stroke="{cor_aviso}" stroke-width="2"/>',
        f'    <circle cx="520" cy="65" r="14" fill="#30363d"/>',
        f'    <path d="M 520 55 Q 528 65 520 75 Q 512 65 520 55 Z" fill="{cor_chama}"/>',
        f'    <text x="520" y="105" font-family="system-ui, sans-serif" font-size="9" font-weight="700" fill="{cor_texto_principal}" text-anchor="middle">AQUECEDOR</text>',
        f'    <text x="380" y="60" font-family="system-ui, sans-serif" font-size="10" font-weight="600" fill="{cor_tubo_gas}" text-anchor="middle">Ramal Aquecedor</text>',
        f'',
        f'    <!-- Ramal 2: B segue reto até Fogão / Cooktop -->',
        f'    <line x1="280" y1="190" x2="480" y2="190" stroke="url(#gradTubo)" stroke-width="8" stroke-linecap="round"/>',
        f'    <!-- Bloco Fogão / Cooktop -->',
        f'    <rect x="480" y="160" width="90" height="70" rx="6" fill="#21262d" stroke="{cor_acento}" stroke-width="2"/>',
        f'    <circle cx="500" cy="185" r="7" fill="#30363d" stroke="{cor_chama}" stroke-width="1.5"/>',
        f'    <circle cx="525" cy="185" r="7" fill="#30363d" stroke="{cor_chama}" stroke-width="1.5"/>',
        f'    <circle cx="550" cy="185" r="7" fill="#30363d" stroke="{cor_chama}" stroke-width="1.5"/>',
        f'    <text x="525" y="215" font-family="system-ui, sans-serif" font-size="9" font-weight="700" fill="{cor_texto_principal}" text-anchor="middle">FOGÃO/FORNO</text>',
        f'    <text x="380" y="180" font-family="system-ui, sans-serif" font-size="10" font-weight="600" fill="{cor_tubo_gas}" text-anchor="middle">Ramal Fogão</text>',
        f'  </g>',
        f'',
        f'  <!-- Painel Direito: Parâmetros Físicos e Demanda -->',
        f'  <rect x="900" y="140" width="500" height="470" rx="12" fill="{cor_card}" stroke="{cor_borda}" stroke-width="1" filter="url(#sombraCard)"/>',
        f'  <text x="930" y="175" font-family="system-ui, -apple-system, sans-serif" font-size="15" font-weight="700" fill="{cor_texto_principal}">PARÂMETROS DE CÁLCULO E DEMANDA</text>',
        f'',
        f'  <!-- Card 1: Gás Combustível -->',
        f'  <g transform="translate(930, 200)">',
        f'    <rect x="0" y="0" width="440" height="90" rx="8" fill="#1c2128" stroke="{cor_borda}" stroke-width="1"/>',
        f'    <text x="16" y="24" font-family="system-ui, sans-serif" font-size="11" font-weight="700" fill="{cor_acento}">PROPRIEDADES DO GÁS ({res.gas.sigla})</text>',
        f'    <text x="16" y="46" font-family="system-ui, sans-serif" font-size="12" fill="{cor_texto_principal}">Gás: {res.gas.nome} · Densidade Relativa d_r = {fracao_para_str(res.gas.densidade_relativa_ar)}</text>',
        f'    <text x="16" y="66" font-family="system-ui, sans-serif" font-size="12" fill="{cor_texto_principal}">PCS = {res.gas.pcs_kcal_m3} kcal/m³ · Pressão Nominal = {res.gas.pressao_nominal_baixa_mmca} mmca</text>',
        f'    <text x="16" y="84" font-family="system-ui, sans-serif" font-size="11" font-weight="700" fill="{cor_aviso}">Perda de Carga Máxima Permitida = {fracao_para_str(res.gas.perda_carga_maxima_mmca)} mmca</text>',
        f'  </g>',
        f'',
        f'  <!-- Card 2: Demanda Instalada e Simultaneidade -->',
        f'  <g transform="translate(930, 305)">',
        f'    <rect x="0" y="0" width="440" height="95" rx="8" fill="#1c2128" stroke="{cor_borda}" stroke-width="1"/>',
        f'    <text x="16" y="24" font-family="system-ui, sans-serif" font-size="11" font-weight="700" fill="{cor_acento}">DEMANDA TÉRMICA E SIMULTANEIDADE</text>',
        f'    <text x="16" y="46" font-family="system-ui, sans-serif" font-size="12" fill="{cor_texto_principal}">Potência Total Instalada: {fracao_para_str(res.potencia_total_instalada_kw)} kW</text>',
        f'    <text x="16" y="66" font-family="system-ui, sans-serif" font-size="12" fill="{cor_texto_principal}">Fator de Simultaneidade (F): {fracao_para_str(res.fator_simultaneidade)}</text>',
        f'    <text x="16" y="86" font-family="system-ui, sans-serif" font-size="12" font-weight="700" fill="{cor_sucesso}">Vazão Simultânea Adotada: {fracao_para_str(res.vazao_total_simultanea_m3_h)} m³/h</text>',
        f'  </g>',
        f'',
        f'  <!-- Card 3: Verificação de Perda e Velocidade -->',
        f'  <g transform="translate(930, 415)">',
        f'    <rect x="0" y="0" width="440" height="175" rx="8" fill="#1c2128" stroke="{cor_borda}" stroke-width="1"/>',
        f'    <text x="16" y="24" font-family="system-ui, sans-serif" font-size="11" font-weight="700" fill="{cor_acento}">BALANÇO HIDRÁULICO E CONFORMIDADE</text>',
        f'    <text x="16" y="48" font-family="system-ui, sans-serif" font-size="12" fill="{cor_texto_principal}">Perda de Carga Acumulada: {fracao_para_str(res.perda_carga_total_acumulada_mmca)} mmca</text>',
        f'    <text x="16" y="68" font-family="system-ui, sans-serif" font-size="12" fill="{cor_texto_principal}">Perda de Carga Limite: {fracao_para_str(res.perda_carga_admissivel_mmca)} mmca</text>',
        f'    <text x="16" y="88" font-family="system-ui, sans-serif" font-size="12" fill="{cor_texto_principal}">Taxa de Trabalho da Perda: {formatar_taxa_pct(res.taxa_perda_carga)}</text>',
        f'    <text x="16" y="108" font-family="system-ui, sans-serif" font-size="12" fill="{cor_texto_principal}">Velocidade Máxima do Gás: {fracao_para_str(res.velocidade_maxima_m_s)} m/s (Limite: 20 m/s)</text>',
        f'    <text x="16" y="132" font-family="system-ui, sans-serif" font-size="13" font-weight="800" fill="{status_cor}">Veredito: {status_texto}</text>',
        f'    <text x="16" y="154" font-family="system-ui, sans-serif" font-size="10" fill="{cor_texto_secundario}">Cálculo conforme ABNT NBR 15526:2016 e Fórmula de Pole</text>',
        f'  </g>',
        f'',
        f'  <!-- Painel Inferior: Quadro Analítico de Trechos -->',
        f'  <rect x="40" y="630" width="1360" height="235" rx="12" fill="{cor_card}" stroke="{cor_borda}" stroke-width="1" filter="url(#sombraCard)"/>',
        f'  <text x="70" y="665" font-family="system-ui, -apple-system, sans-serif" font-size="15" font-weight="700" fill="{cor_texto_principal}">DIMENSIONAMENTO POR TRECHO (FÓRMULA DE POLE)</text>',
    ]

    base_y = 690
    largura_max_barra = 260
    for idx, tr in enumerate(res.trechos):
        y_pos = base_y + (idx * 27)
        if y_pos > 840:
            break
        cor_item = cor_sucesso if tr.velocidade_aprovada else cor_perigo
        taxa_perda_trecho = (
            tr.perda_carga_trecho_mmca / res.perda_carga_admissivel_mmca
            if res.perda_carga_admissivel_mmca > 0
            else Fraction(0, 1)
        )
        taxa_num = min(100, int((taxa_perda_trecho * 100).numerator // max(1, (taxa_perda_trecho * 100).denominator)))
        largura_barra = int((taxa_num / 100) * largura_max_barra)

        linhas_svg.extend([
            f'  <g transform="translate(70, {y_pos})">',
            f'    <text x="0" y="14" font-family="system-ui, sans-serif" font-size="12" font-weight="600" fill="{cor_texto_principal}">{tr.identificador} ({tr.tubulacao.codigo}, Dint={fracao_para_str(tr.tubulacao.diametro_interno_mm)}mm)</text>',
            f'    <text x="360" y="14" font-family="system-ui, sans-serif" font-size="12" fill="{cor_texto_secundario}">Leq={fracao_para_str(tr.comprimento_total_equivalente_m)}m · Q={fracao_para_str(tr.vazao_m3_h)}m³/h · ΔH={fracao_para_str(tr.perda_carga_trecho_mmca)}mmca</text>',
            f'    <!-- Trilho da barra -->',
            f'    <rect x="740" y="3" width="{largura_max_barra}" height="14" rx="4" fill="#21262d"/>',
            f'    <!-- Preenchimento da barra -->',
            f'    <rect x="740" y="3" width="{largura_barra}" height="14" rx="4" fill="{cor_tubo_gas}"/>',
            f'    <text x="1020" y="14" font-family="system-ui, sans-serif" font-size="12" font-weight="700" fill="{cor_tubo_gas}">{taxa_num}%</text>',
            f'    <text x="1080" y="14" font-family="system-ui, sans-serif" font-size="12" fill="{cor_texto_principal}">Vel: {fracao_para_str(tr.velocidade_m_s)} m/s</text>',
            f'    <text x="1220" y="14" font-family="system-ui, sans-serif" font-size="11" font-weight="700" fill="{cor_item}">{"✓ OK" if tr.velocidade_aprovada else "✗ VEL EXC"}</text>',
            f'  </g>',
        ])

    linhas_svg.extend([
        f'</svg>',
    ])
    return "\n".join(linhas_svg) + "\n"
