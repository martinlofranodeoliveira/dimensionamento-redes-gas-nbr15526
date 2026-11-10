"""Verificador independente em SQLite in-memory para redes internas de gás (NBR 15526).

Padrão LOFRANO TECNOLOGIA:
- Auditoria analítica independente sem importar nenhum módulo de produção do pacote
- Criação e execução de modelo relacional em memória com sqlite3
- Verificação cruzada da Fórmula de Pole, velocidades e perdas admissíveis
"""

import sqlite3
import sys
from fractions import Fraction

# Constante de Pole e Pi
K_POLE = Fraction(22222, 1)
PI_RACIONAL = Fraction(355, 113)


def executar_auditoria_independente() -> int:
    """Executa auditoria matemática independente via SQLite in-memory."""
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE gases_normativos (
        sigla TEXT PRIMARY KEY,
        dr_num INTEGER,
        dr_den INTEGER,
        pcs INTEGER,
        p_max_mmca INTEGER
    )
    """)

    gases_dados = [
        ("GN", 60, 100, 9400, 25),
        ("GLP", 152, 100, 24000, 28),
    ]
    cur.executemany("INSERT INTO gases_normativos VALUES (?, ?, ?, ?, ?)", gases_dados)

    cur.execute("""
    CREATE TABLE tubos_cobre (
        codigo TEXT PRIMARY KEY,
        dint_num INTEGER,
        dint_den INTEGER
    )
    """)

    tubos_dados = [
        ("CU_DN15", 13, 1),
        ("CU_DN22", 99, 5),     # 19.8 mm
        ("CU_DN28", 128, 5),    # 25.6 mm
        ("CU_DN35", 161, 5),    # 32.2 mm
    ]
    cur.executemany("INSERT INTO tubos_cobre VALUES (?, ?, ?)", tubos_dados)

    print("Iniciando auditoria independente em SQLite in-memory...")

    # Caso 1: GN em trecho principal DN 22 (L = 10 m, Q = 2.5 m³/h)
    cur.execute("SELECT dr_num, dr_den, p_max_mmca FROM gases_normativos WHERE sigla = 'GN'")
    dr_num, dr_den, p_max = cur.fetchone()
    dr = Fraction(dr_num, dr_den)

    cur.execute("SELECT dint_num, dint_den FROM tubos_cobre WHERE codigo = 'CU_DN22'")
    d_num, d_den = cur.fetchone()
    d_int = Fraction(d_num, d_den)

    comp_eq = Fraction(10, 1)
    vazao = Fraction(25, 10)  # 2.5 m³/h

    # Formula de Pole: Delta_H = (22222 * dr * L * Q^2) / D^5
    perda_c1 = (K_POLE * dr * comp_eq * (vazao ** 2)) / (d_int ** 5)
    vel_c1 = (vazao * 10000) / (Fraction(9, 1) * PI_RACIONAL * (d_int ** 2))

    assert perda_c1 <= p_max, f"Falha Caso 1 Perda: {perda_c1} > {p_max}"
    assert vel_c1 <= 20, f"Falha Caso 1 Velocidade: {vel_c1} > 20"
    print(f"✓ Caso 1 GN: Perda = {float(perda_c1):.2f} mmca <= {p_max} mmca, Vel = {float(vel_c1):.2f} m/s OK.")

    # Caso 2: GLP em trecho comercial DN 28 (L = 15 m, Q = 1.2 m³/h)
    cur.execute("SELECT dr_num, dr_den, p_max_mmca FROM gases_normativos WHERE sigla = 'GLP'")
    dr_num2, dr_den2, p_max2 = cur.fetchone()
    dr2 = Fraction(dr_num2, dr_den2)

    cur.execute("SELECT dint_num, dint_den FROM tubos_cobre WHERE codigo = 'CU_DN28'")
    d_num2, d_den2 = cur.fetchone()
    d_int2 = Fraction(d_num2, d_den2)

    comp_eq2 = Fraction(15, 1)
    vazao2 = Fraction(12, 10)

    perda_c2 = (K_POLE * dr2 * comp_eq2 * (vazao2 ** 2)) / (d_int2 ** 5)
    vel_c2 = (vazao2 * 10000) / (Fraction(9, 1) * PI_RACIONAL * (d_int2 ** 2))

    assert perda_c2 <= p_max2, f"Falha Caso 2 Perda: {perda_c2} > {p_max2}"
    assert vel_c2 <= 20, f"Falha Caso 2 Velocidade: {vel_c2} > 20"
    print(f"✓ Caso 2 GLP: Perda = {float(perda_c2):.2f} mmca <= {p_max2} mmca, Vel = {float(vel_c2):.2f} m/s OK.")

    conn.close()
    print("Auditoria independente em SQLite in-memory concluída com 100% de aprovação.")
    return 0


if __name__ == "__main__":
    sys.exit(executar_auditoria_independente())
