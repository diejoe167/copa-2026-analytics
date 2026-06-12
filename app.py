# -*- coding: utf-8 -*-
"""
⚽ COPA 2026 ANALYTICS — Análise Histórica & Previsões Preditivas
=================================================================
Aplicativo Streamlit que une ciência de dados de futebol e narrativa
de jornalismo esportivo para a Copa do Mundo de 2026 (formato de 48 seleções).

Execução:
    streamlit run app.py

Stack: streamlit, pandas, numpy, plotly
"""

import math
from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================================
# CONFIGURAÇÃO GERAL E ESTILO
# ============================================================================

st.set_page_config(
    page_title="Copa 2026 Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

CORES = {
    "primaria": "#1B5E20",      # verde gramado
    "secundaria": "#FFC107",    # dourado taça
    "vitoria": "#2E7D32",
    "empate": "#9E9E9E",
    "derrota": "#C62828",
    "destaque": "#1565C0",
}

PALETA_SELECOES = {
    "Brasil": "#FFD700", "Argentina": "#74ACDF", "França": "#003399",
    "Alemanha": "#000000", "Espanha": "#C60B1E", "Inglaterra": "#CF081F",
    "Portugal": "#006600", "Países Baixos": "#FF6600", "Croácia": "#E63946",
    "Uruguai": "#5CB8E4", "Bélgica": "#E30613", "Marrocos": "#C1272D",
    "Japão": "#BC002D", "México": "#006847", "Estados Unidos": "#3C3B6E",
    "Colômbia": "#FCD116",
}

CSS_CUSTOM = """
<style>
    .main-title {
        font-size: 2.3rem; font-weight: 800;
        background: linear-gradient(90deg, #1B5E20 0%, #FFC107 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .subtitle { color: #666; font-size: 1.05rem; margin-top: 0; }
    div[data-testid="stMetric"] {
        background: rgba(27, 94, 32, 0.06);
        border: 1px solid rgba(27, 94, 32, 0.18);
        border-radius: 12px; padding: 12px 16px;
    }
    .cronica-box {
        background: rgba(255, 193, 7, 0.07);
        border-left: 5px solid #FFC107;
        border-radius: 8px; padding: 18px 24px; line-height: 1.75;
    }
</style>
"""


# ============================================================================
# CAMADA DE DADOS (MOCK DATA — fictícios, porém realistas)
# ============================================================================

@st.cache_data
def carregar_historico_copas() -> pd.DataFrame:
    """Desempenho das principais seleções nas últimas 5 edições da Copa.

    Aproveitamento = pontos conquistados / pontos disputados (jogos x 3).
    Jogos decididos nos pênaltis são contabilizados como empates (critério FIFA).
    """
    registros = [
        # (seleção, edição, jogos, V, E, D, gols_pro, gols_contra, fase_final)
        ("Brasil",        2006, 5, 4, 0, 1, 10,  2, "Quartas"),
        ("Brasil",        2010, 5, 3, 1, 1,  9,  4, "Quartas"),
        ("Brasil",        2014, 7, 3, 2, 2, 11, 14, "4º lugar"),
        ("Brasil",        2018, 5, 3, 1, 1,  8,  3, "Quartas"),
        ("Brasil",        2022, 5, 3, 1, 1,  8,  3, "Quartas"),
        ("Argentina",     2006, 5, 3, 2, 0, 11,  3, "Quartas"),
        ("Argentina",     2010, 5, 4, 0, 1, 10,  6, "Quartas"),
        ("Argentina",     2014, 7, 5, 1, 1,  8,  4, "Vice"),
        ("Argentina",     2018, 4, 1, 1, 2,  6,  9, "Oitavas"),
        ("Argentina",     2022, 7, 5, 1, 1, 15,  8, "Campeã"),
        ("França",        2006, 7, 3, 4, 0,  9,  3, "Vice"),
        ("França",        2010, 3, 0, 1, 2,  1,  4, "Grupos"),
        ("França",        2014, 5, 3, 1, 1, 10,  3, "Quartas"),
        ("França",        2018, 7, 6, 1, 0, 14,  6, "Campeã"),
        ("França",        2022, 7, 5, 1, 1, 16,  8, "Vice"),
        ("Alemanha",      2006, 7, 5, 1, 1, 14,  6, "3º lugar"),
        ("Alemanha",      2010, 7, 5, 0, 2, 16,  5, "3º lugar"),
        ("Alemanha",      2014, 7, 6, 1, 0, 18,  4, "Campeã"),
        ("Alemanha",      2018, 3, 1, 0, 2,  2,  4, "Grupos"),
        ("Alemanha",      2022, 3, 1, 1, 1,  6,  5, "Grupos"),
        ("Espanha",       2006, 4, 3, 0, 1,  9,  4, "Oitavas"),
        ("Espanha",       2010, 7, 6, 0, 1,  8,  2, "Campeã"),
        ("Espanha",       2014, 3, 1, 0, 2,  4,  7, "Grupos"),
        ("Espanha",       2018, 4, 1, 3, 0,  7,  6, "Oitavas"),
        ("Espanha",       2022, 4, 1, 2, 1,  9,  3, "Oitavas"),
        ("Inglaterra",    2006, 5, 3, 2, 0,  6,  2, "Quartas"),
        ("Inglaterra",    2010, 4, 1, 2, 1,  3,  5, "Oitavas"),
        ("Inglaterra",    2014, 3, 0, 1, 2,  2,  4, "Grupos"),
        ("Inglaterra",    2018, 7, 3, 1, 3, 12,  8, "4º lugar"),
        ("Inglaterra",    2022, 5, 3, 1, 1, 13,  4, "Quartas"),
        ("Portugal",      2006, 7, 4, 1, 2,  7,  5, "4º lugar"),
        ("Portugal",      2010, 4, 1, 2, 1,  7,  1, "Oitavas"),
        ("Portugal",      2014, 3, 1, 1, 1,  4,  7, "Grupos"),
        ("Portugal",      2018, 4, 1, 2, 1,  6,  6, "Oitavas"),
        ("Portugal",      2022, 5, 4, 0, 1, 12,  6, "Quartas"),
        ("Países Baixos", 2006, 4, 2, 1, 1,  3,  2, "Oitavas"),
        ("Países Baixos", 2010, 7, 6, 0, 1, 12,  6, "Vice"),
        ("Países Baixos", 2014, 7, 5, 2, 0, 15,  4, "3º lugar"),
        ("Países Baixos", 2018, 0, 0, 0, 0,  0,  0, "Não classif."),
        ("Países Baixos", 2022, 5, 3, 2, 0, 10,  4, "Quartas"),
        ("Croácia",       2006, 3, 0, 2, 1,  2,  3, "Grupos"),
        ("Croácia",       2010, 0, 0, 0, 0,  0,  0, "Não classif."),
        ("Croácia",       2014, 3, 1, 0, 2,  6,  6, "Grupos"),
        ("Croácia",       2018, 7, 4, 2, 1, 14,  9, "Vice"),
        ("Croácia",       2022, 7, 2, 4, 1,  8,  7, "3º lugar"),
        ("Uruguai",       2006, 0, 0, 0, 0,  0,  0, "Não classif."),
        ("Uruguai",       2010, 7, 3, 2, 2, 11,  8, "4º lugar"),
        ("Uruguai",       2014, 4, 2, 0, 2,  4,  6, "Oitavas"),
        ("Uruguai",       2018, 5, 4, 0, 1,  7,  3, "Quartas"),
        ("Uruguai",       2022, 3, 1, 1, 1,  2,  2, "Grupos"),
        ("Marrocos",      2006, 0, 0, 0, 0,  0,  0, "Não classif."),
        ("Marrocos",      2010, 0, 0, 0, 0,  0,  0, "Não classif."),
        ("Marrocos",      2014, 0, 0, 0, 0,  0,  0, "Não classif."),
        ("Marrocos",      2018, 3, 0, 1, 2,  2,  4, "Grupos"),
        ("Marrocos",      2022, 7, 4, 2, 1,  6,  5, "4º lugar"),
        ("Japão",         2006, 3, 0, 1, 2,  2,  7, "Grupos"),
        ("Japão",         2010, 4, 2, 1, 1,  4,  2, "Oitavas"),
        ("Japão",         2014, 3, 0, 1, 2,  2,  6, "Grupos"),
        ("Japão",         2018, 4, 1, 1, 2,  6,  7, "Oitavas"),
        ("Japão",         2022, 4, 2, 1, 1,  5,  4, "Oitavas"),
    ]
    df = pd.DataFrame(
        registros,
        columns=["selecao", "edicao", "jogos", "vitorias", "empates",
                 "derrotas", "gols_pro", "gols_contra", "fase"],
    )
    df["pontos"] = df["vitorias"] * 3 + df["empates"]
    df["aproveitamento"] = np.where(
        df["jogos"] > 0, (df["pontos"] / (df["jogos"] * 3) * 100).round(1), np.nan
    )
    df["saldo_gols"] = df["gols_pro"] - df["gols_contra"]
    return df


@st.cache_data
def carregar_forcas_2026() -> pd.DataFrame:
    """Parâmetros de força das 48 classificadas, nos GRUPOS OFICIAIS do sorteio.

    Grupos conforme o sorteio oficial da FIFA (dez/2025) + repescagens (mar/2026).
    - ataque: média esperada de gols marcados por jogo contra adversário mediano
    - defesa: média esperada de gols sofridos por jogo contra adversário mediano
    - forma_recente: aproveitamento (%) nos últimos 12 meses (amistosos + eliminatórias)
    - rating: índice Elo-like sintético (calibrado em rankings reais; mock)
    """
    dados = [
        # (seleção, grupo, ataque, defesa, forma_recente, rating)
        ("México",              "A", 1.35, 1.10, 58, 1700),
        ("Coreia do Sul",       "A", 1.30, 1.15, 60, 1670),
        ("Rep. Checa",          "A", 1.30, 1.15, 57, 1655),
        ("África do Sul",       "A", 1.10, 1.25, 53, 1585),
        ("Canadá",              "B", 1.35, 1.10, 62, 1685),
        ("Bósnia e Herzegovina","B", 1.20, 1.20, 54, 1600),
        ("Catar",               "B", 1.10, 1.30, 50, 1560),
        ("Suíça",               "B", 1.40, 1.05, 64, 1750),
        ("Brasil",              "C", 1.95, 0.85, 72, 1920),
        ("Marrocos",            "C", 1.40, 0.80, 71, 1800),
        ("Haiti",               "C", 0.90, 1.40, 44, 1500),
        ("Escócia",             "C", 1.25, 1.15, 58, 1645),
        ("Estados Unidos",      "D", 1.30, 1.15, 60, 1690),
        ("Paraguai",            "D", 1.20, 1.00, 60, 1665),
        ("Austrália",           "D", 1.25, 1.15, 58, 1640),
        ("Turquia",             "D", 1.45, 1.10, 63, 1720),
        ("Alemanha",            "E", 1.80, 1.00, 69, 1840),
        ("Curaçao",             "E", 0.95, 1.35, 47, 1525),
        ("Costa do Marfim",     "E", 1.30, 1.10, 60, 1670),
        ("Equador",             "E", 1.30, 0.90, 64, 1730),
        ("Países Baixos",       "F", 1.75, 0.95, 70, 1845),
        ("Japão",               "F", 1.50, 1.00, 68, 1785),
        ("Suécia",              "F", 1.35, 1.10, 58, 1660),
        ("Tunísia",             "F", 1.15, 1.10, 55, 1610),
        ("Bélgica",             "G", 1.65, 1.05, 62, 1770),
        ("Egito",               "G", 1.25, 1.00, 64, 1680),
        ("Irã",                 "G", 1.25, 1.10, 61, 1650),
        ("Nova Zelândia",       "G", 1.00, 1.30, 48, 1530),
        ("Espanha",             "H", 2.00, 0.75, 81, 1965),
        ("Cabo Verde",          "H", 1.05, 1.25, 52, 1565),
        ("Arábia Saudita",      "H", 1.10, 1.25, 52, 1570),
        ("Uruguai",             "H", 1.55, 0.90, 66, 1790),
        ("França",              "I", 2.05, 0.80, 78, 1985),
        ("Senegal",             "I", 1.40, 1.00, 65, 1745),
        ("Iraque",              "I", 0.95, 1.35, 46, 1520),
        ("Noruega",             "I", 1.65, 1.10, 72, 1765),
        ("Argentina",           "J", 2.10, 0.70, 84, 2010),
        ("Argélia",             "J", 1.30, 1.10, 62, 1675),
        ("Áustria",             "J", 1.45, 1.05, 66, 1740),
        ("Jordânia",            "J", 1.00, 1.30, 50, 1545),
        ("Portugal",            "K", 1.90, 0.90, 73, 1880),
        ("RD Congo",            "K", 1.05, 1.25, 54, 1580),
        ("Uzbequistão",         "K", 1.10, 1.20, 55, 1590),
        ("Colômbia",            "K", 1.60, 0.95, 69, 1810),
        ("Inglaterra",          "L", 1.85, 0.85, 75, 1905),
        ("Croácia",             "L", 1.45, 1.05, 63, 1760),
        ("Gana",                "L", 1.20, 1.20, 53, 1605),
        ("Panamá",              "L", 1.10, 1.25, 52, 1575),
    ]
    return pd.DataFrame(
        dados,
        columns=["selecao", "grupo", "ataque", "defesa", "forma_recente", "rating"],
    )


@st.cache_data
def carregar_jogadores() -> pd.DataFrame:
    """Métricas individuais (clube + seleção, últimos 12 meses) — mock realista."""
    dados = [
        # nome, seleção, posição, jogos, minutos, gols, assistências,
        # aproveitamento da seleção c/ ele em campo (%), nota média
        ("Kylian Mbappé",    "França",         "ATA", 52, 4420, 44, 12, 79, 8.4),
        ("Lionel Messi",     "Argentina",      "ATA", 41, 3350, 28, 16, 86, 8.2),
        ("Erling Haaland",   "Noruega",        "ATA", 48, 4100, 46,  6, 74, 8.3),
        ("Jude Bellingham",  "Inglaterra",     "MEI", 50, 4280, 21, 13, 77, 8.1),
        ("Vinícius Júnior",  "Brasil",         "ATA", 49, 4010, 25, 14, 70, 7.9),
        ("Lamine Yamal",     "Espanha",        "ATA", 53, 4150, 19, 21, 83, 8.2),
        ("Harry Kane",       "Inglaterra",     "ATA", 51, 4390, 41,  9, 76, 8.0),
        ("Jamal Musiala",    "Alemanha",       "MEI", 44, 3520, 17, 12, 71, 7.8),
        ("Julián Álvarez",   "Argentina",      "ATA", 54, 4230, 27, 10, 85, 7.9),
        ("Rodri",            "Espanha",        "VOL", 46, 4050,  8,  9, 84, 8.3),
        ("Federico Valverde","Uruguai",        "MEI", 55, 4700, 12, 11, 68, 7.7),
        ("Bukayo Saka",      "Inglaterra",     "ATA", 47, 3880, 18, 15, 75, 7.8),
        ("Achraf Hakimi",    "Marrocos",       "LAT", 50, 4310,  9, 13, 73, 7.9),
        ("Raphinha",         "Brasil",         "ATA", 52, 4180, 30, 17, 72, 8.1),
        ("Florian Wirtz",    "Alemanha",       "MEI", 49, 4020, 16, 18, 70, 8.0),
        ("Cody Gakpo",       "Países Baixos",  "ATA", 50, 3760, 20, 11, 71, 7.6),
        ("Kaoru Mitoma",     "Japão",          "ATA", 45, 3540, 14, 10, 69, 7.5),
        ("Luka Modrić",      "Croácia",        "MEI", 43, 3120,  5,  9, 62, 7.4),
        ("Bruno Fernandes",  "Portugal",       "MEI", 56, 4810, 18, 16, 74, 7.8),
        ("Christian Pulisic","Estados Unidos", "ATA", 48, 3890, 17, 12, 61, 7.6),
        ("Luis Díaz",        "Colômbia",       "ATA", 51, 4220, 22, 11, 70, 7.8),
        ("Santiago Giménez", "México",         "ATA", 47, 3650, 24,  5, 59, 7.4),
    ]
    df = pd.DataFrame(
        dados,
        columns=["jogador", "selecao", "posicao", "jogos", "minutos",
                 "gols", "assistencias", "aproveitamento_selecao", "nota_media"],
    )
    df["participacoes_90"] = ((df["gols"] + df["assistencias"]) / (df["minutos"] / 90)).round(2)
    df["minutos_por_gol"] = np.where(df["gols"] > 0, (df["minutos"] / df["gols"]).round(0), np.nan)
    # Índice de eficiência composto (0-100): produção ofensiva + nota + impacto na seleção
    prod_norm = df["participacoes_90"] / df["participacoes_90"].max()
    nota_norm = (df["nota_media"] - 7.0) / (df["nota_media"].max() - 7.0)
    apr_norm = df["aproveitamento_selecao"] / 100
    df["indice_eficiencia"] = ((0.45 * prod_norm + 0.30 * nota_norm + 0.25 * apr_norm) * 100).round(1)
    return df.sort_values("indice_eficiencia", ascending=False).reset_index(drop=True)


@st.cache_data
def carregar_head_to_head() -> pd.DataFrame:
    """Histórico de confrontos diretos (todas as competições oficiais) — mock realista."""
    dados = [
        # (time_a, time_b, jogos, vitorias_a, empates, vitorias_b)
        ("Brasil", "Argentina", 109, 43, 26, 40),
        ("Brasil", "França", 17, 6, 2, 9),
        ("Brasil", "Alemanha", 23, 13, 5, 5),
        ("Brasil", "Uruguai", 79, 39, 20, 20),
        ("Argentina", "França", 13, 6, 3, 4),
        ("Argentina", "Alemanha", 23, 10, 6, 7),
        ("França", "Alemanha", 34, 14, 7, 13),
        ("França", "Inglaterra", 31, 13, 5, 13),
        ("Espanha", "Portugal", 41, 17, 18, 6),
        ("Espanha", "Inglaterra", 28, 11, 4, 13),
        ("Inglaterra", "Alemanha", 36, 14, 9, 13),
        ("Países Baixos", "Alemanha", 46, 12, 17, 17),
        ("Brasil", "Espanha", 10, 5, 3, 2),
        ("Argentina", "Inglaterra", 14, 7, 4, 3),
        ("México", "Estados Unidos", 78, 38, 17, 23),
    ]
    return pd.DataFrame(
        dados, columns=["time_a", "time_b", "jogos", "vitorias_a", "empates", "vitorias_b"]
    )


@st.cache_data
def carregar_calendario() -> pd.DataFrame:
    """Calendário REAL da fase de grupos da Copa 2026 (72 jogos, 11–27/jun).

    1ª rodada conforme a tabela oficial; 2ª e 3ª seguem o padrão de
    cruzamento da FIFA (validado contra os jogos divulgados dos grupos A–F).
    `resultado` registra placares de jogos já disputados (formato "2x0").
    """
    jogos = [
        # (data, rodada, grupo, time_a, time_b, resultado)
        ("11/06", 1, "A", "México", "África do Sul", "2x0"),
        ("11/06", 1, "A", "Coreia do Sul", "Rep. Checa", "2x1"),
        ("12/06", 1, "B", "Canadá", "Bósnia e Herzegovina", None),
        ("12/06", 1, "D", "Estados Unidos", "Paraguai", None),
        ("13/06", 1, "B", "Catar", "Suíça", None),
        ("13/06", 1, "C", "Brasil", "Marrocos", None),
        ("13/06", 1, "C", "Haiti", "Escócia", None),
        ("14/06", 1, "D", "Austrália", "Turquia", None),
        ("14/06", 1, "E", "Alemanha", "Curaçao", None),
        ("14/06", 1, "E", "Costa do Marfim", "Equador", None),
        ("14/06", 1, "F", "Países Baixos", "Japão", None),
        ("14/06", 1, "F", "Suécia", "Tunísia", None),
        ("15/06", 1, "G", "Bélgica", "Egito", None),
        ("15/06", 1, "G", "Irã", "Nova Zelândia", None),
        ("15/06", 1, "H", "Espanha", "Cabo Verde", None),
        ("15/06", 1, "H", "Arábia Saudita", "Uruguai", None),
        ("16/06", 1, "I", "França", "Senegal", None),
        ("16/06", 1, "I", "Iraque", "Noruega", None),
        ("16/06", 1, "J", "Argentina", "Argélia", None),
        ("17/06", 1, "J", "Áustria", "Jordânia", None),
        ("17/06", 1, "K", "Portugal", "RD Congo", None),
        ("17/06", 1, "K", "Uzbequistão", "Colômbia", None),
        ("17/06", 1, "L", "Inglaterra", "Croácia", None),
        ("17/06", 1, "L", "Gana", "Panamá", None),
        ("18/06", 2, "A", "México", "Coreia do Sul", None),
        ("18/06", 2, "A", "Rep. Checa", "África do Sul", None),
        ("18/06", 2, "B", "Canadá", "Catar", None),
        ("18/06", 2, "B", "Suíça", "Bósnia e Herzegovina", None),
        ("19/06", 2, "C", "Brasil", "Haiti", None),
        ("19/06", 2, "C", "Escócia", "Marrocos", None),
        ("19/06", 2, "D", "Estados Unidos", "Austrália", None),
        ("20/06", 2, "D", "Turquia", "Paraguai", None),
        ("20/06", 2, "E", "Alemanha", "Costa do Marfim", None),
        ("20/06", 2, "E", "Equador", "Curaçao", None),
        ("20/06", 2, "F", "Países Baixos", "Suécia", None),
        ("21/06", 2, "F", "Tunísia", "Japão", None),
        ("21/06", 2, "G", "Bélgica", "Irã", None),
        ("21/06", 2, "G", "Nova Zelândia", "Egito", None),
        ("21/06", 2, "H", "Espanha", "Arábia Saudita", None),
        ("21/06", 2, "H", "Uruguai", "Cabo Verde", None),
        ("22/06", 2, "I", "França", "Iraque", None),
        ("22/06", 2, "I", "Noruega", "Senegal", None),
        ("22/06", 2, "J", "Argentina", "Áustria", None),
        ("22/06", 2, "J", "Jordânia", "Argélia", None),
        ("23/06", 2, "K", "Portugal", "Uzbequistão", None),
        ("23/06", 2, "K", "Colômbia", "RD Congo", None),
        ("23/06", 2, "L", "Inglaterra", "Gana", None),
        ("23/06", 2, "L", "Panamá", "Croácia", None),
        ("24/06", 3, "A", "Rep. Checa", "México", None),
        ("24/06", 3, "A", "África do Sul", "Coreia do Sul", None),
        ("24/06", 3, "B", "Suíça", "Canadá", None),
        ("24/06", 3, "B", "Bósnia e Herzegovina", "Catar", None),
        ("24/06", 3, "C", "Escócia", "Brasil", None),
        ("24/06", 3, "C", "Marrocos", "Haiti", None),
        ("25/06", 3, "D", "Turquia", "Estados Unidos", None),
        ("25/06", 3, "D", "Paraguai", "Austrália", None),
        ("25/06", 3, "E", "Equador", "Alemanha", None),
        ("25/06", 3, "E", "Curaçao", "Costa do Marfim", None),
        ("25/06", 3, "F", "Tunísia", "Países Baixos", None),
        ("25/06", 3, "F", "Japão", "Suécia", None),
        ("26/06", 3, "G", "Nova Zelândia", "Bélgica", None),
        ("26/06", 3, "G", "Egito", "Irã", None),
        ("26/06", 3, "I", "Noruega", "França", None),
        ("26/06", 3, "I", "Senegal", "Iraque", None),
        ("27/06", 3, "H", "Uruguai", "Espanha", None),
        ("27/06", 3, "H", "Cabo Verde", "Arábia Saudita", None),
        ("27/06", 3, "J", "Jordânia", "Argentina", None),
        ("27/06", 3, "J", "Argélia", "Áustria", None),
        ("27/06", 3, "K", "Colômbia", "Portugal", None),
        ("27/06", 3, "K", "RD Congo", "Uzbequistão", None),
        ("27/06", 3, "L", "Panamá", "Inglaterra", None),
        ("27/06", 3, "L", "Croácia", "Gana", None),
    ]
    return pd.DataFrame(
        jogos, columns=["data", "rodada", "grupo", "time_a", "time_b", "resultado"]
    )


def _parse_placar(placar: str) -> tuple[int, int]:
    """Converte "2x0" em (2, 0)."""
    ga, gb = placar.lower().split("x")
    return int(ga), int(gb)


def extrair_resultados_fixos(calendario: pd.DataFrame) -> dict:
    """Placar real dos jogos já disputados: {(time_a, time_b): (gols_a, gols_b)}."""
    fixos = {}
    for _, j in calendario.dropna(subset=["resultado"]).iterrows():
        fixos[(j["time_a"], j["time_b"])] = _parse_placar(j["resultado"])
    return fixos


@st.cache_data
def aplicar_resultados(forcas: pd.DataFrame, calendario: pd.DataFrame) -> tuple:
    """Recalibra o modelo com os resultados reais já disputados.

    Para cada jogo, em ordem cronológica:
    - rating: atualização Elo clássica (K=40, padrão para Copas do Mundo);
    - forma_recente: média móvel exponencial em direção ao resultado (85/15);
    - ataque/defesa: ajuste suave (β=0.15) em direção aos gols observados,
      normalizados pela força do adversário (marcar 2 no Haiti vale menos
      que marcar 2 na Argentina).

    Retorna (forcas_recalibradas, log_de_ajustes).
    """
    jogados = calendario.dropna(subset=["resultado"])
    if jogados.empty:
        return forcas, pd.DataFrame()

    fa = forcas.set_index("selecao").copy()
    colunas_num = ["ataque", "defesa", "forma_recente", "rating"]
    fa[colunas_num] = fa[colunas_num].astype(float)
    defesa_media = forcas["defesa"].mean()
    ataque_medio = forcas["ataque"].mean()
    K, BETA = 40.0, 0.15
    log = []

    for _, j in jogados.iterrows():
        a, b = j["time_a"], j["time_b"]
        ga, gb = _parse_placar(j["resultado"])

        ra, rb = fa.loc[a, "rating"], fa.loc[b, "rating"]
        esperado_a = 1 / (1 + 10 ** ((rb - ra) / 400))
        real_a = 1.0 if ga > gb else 0.5 if ga == gb else 0.0
        delta = K * (real_a - esperado_a)
        fa.loc[a, "rating"] = ra + delta
        fa.loc[b, "rating"] = rb - delta

        fa.loc[a, "forma_recente"] = 0.85 * fa.loc[a, "forma_recente"] + 0.15 * (real_a * 100)
        fa.loc[b, "forma_recente"] = 0.85 * fa.loc[b, "forma_recente"] + 0.15 * ((1 - real_a) * 100)

        ga_ajustado = ga / max(fa.loc[b, "defesa"] / defesa_media, 0.3)
        gb_ajustado = gb / max(fa.loc[a, "defesa"] / defesa_media, 0.3)
        fa.loc[a, "ataque"] = (1 - BETA) * fa.loc[a, "ataque"] + BETA * ga_ajustado
        fa.loc[b, "ataque"] = (1 - BETA) * fa.loc[b, "ataque"] + BETA * gb_ajustado
        sofrido_a = gb / max(fa.loc[b, "ataque"] / ataque_medio, 0.3)
        sofrido_b = ga / max(fa.loc[a, "ataque"] / ataque_medio, 0.3)
        fa.loc[a, "defesa"] = (1 - BETA) * fa.loc[a, "defesa"] + BETA * sofrido_a
        fa.loc[b, "defesa"] = (1 - BETA) * fa.loc[b, "defesa"] + BETA * sofrido_b

        log.append({"data": j["data"], "jogo": f"{a} {ga}x{gb} {b}",
                    "delta_rating": round(delta, 1),
                    "beneficiado": a if delta > 0 else b})

    return fa.reset_index(), pd.DataFrame(log)


ANFITRIOES = {"Estados Unidos", "México", "Canadá"}


@st.cache_data
def aplicar_fatores_extras(forcas: pd.DataFrame, jogadores: pd.DataFrame,
                           bonus_mando: float, impacto_craque: float) -> tuple:
    """Fatores contextuais que impactam a probabilidade de vitória.

    - Anfitrião (EUA/México/Canadá): jogar em casa vale historicamente
      ~0.2–0.4 gol por jogo → ataque +bonus%, defesa -bonus/2%.
    - Craque: o melhor Índice de Eficiência da seleção (aba de atletas)
      escala o ataque em até +impacto% — um decisivo de elite muda jogos
      de mata-mata. Só bonifica (não penaliza quem não tem atleta listado).

    Retorna (forcas_ajustadas, log_de_fatores).
    """
    fa = forcas.copy()
    cols = ["ataque", "defesa", "forma_recente", "rating"]
    fa[cols] = fa[cols].astype(float)
    melhor_craque = jogadores.groupby("selecao")["indice_eficiencia"].max()
    log = []

    for idx, linha in fa.iterrows():
        time, motivos = linha["selecao"], []
        if time in ANFITRIOES and bonus_mando > 0:
            fa.loc[idx, "ataque"] *= 1 + bonus_mando / 100
            fa.loc[idx, "defesa"] *= 1 - bonus_mando / 200
            motivos.append(f"🏟️ anfitrião (+{bonus_mando:.0f}% ataque)")
        if time in melhor_craque.index and impacto_craque > 0:
            peso = max(0.0, min((melhor_craque[time] - 60) / 40, 1.0))
            if peso > 0:
                ganho = impacto_craque * peso
                fa.loc[idx, "ataque"] *= 1 + ganho / 100
                motivos.append(f"⭐ craque {melhor_craque[time]:.0f} (+{ganho:.1f}% ataque)")
        if motivos:
            log.append({"selecao": time, "fatores": " · ".join(motivos)})

    return fa, pd.DataFrame(log)


# ============================================================================
# MÓDULO ANALÍTICO — MODELO DE POISSON E POWER RANKING
# ============================================================================

MAX_GOLS = 7  # teto da matriz de placares (0 a 7 gols por equipe)


def gols_esperados(forcas: pd.DataFrame, time_a: str, time_b: str) -> tuple[float, float]:
    """Calcula os gols esperados (lambda de Poisson) de cada equipe.

    lambda_A = ataque_A x (defesa_B / defesa_média) x fator_forma_A
    O fator de forma escala ±15% conforme o aproveitamento recente.
    """
    fa = forcas.set_index("selecao")
    defesa_media = forcas["defesa"].mean()

    def _lambda(atacante: str, defensor: str) -> float:
        fator_forma = 0.85 + 0.30 * (fa.loc[atacante, "forma_recente"] / 100)
        lam = fa.loc[atacante, "ataque"] * (fa.loc[defensor, "defesa"] / defesa_media) * fator_forma
        return max(0.15, float(lam))

    return _lambda(time_a, time_b), _lambda(time_b, time_a)


def matriz_poisson(lambda_a: float, lambda_b: float, rho: float = 0.0) -> np.ndarray:
    """Matriz (MAX_GOLS+1 x MAX_GOLS+1) com P(placar A x B).

    Base: Poisson independente. Com `rho != 0`, aplica a correção de
    Dixon-Coles (1997) aos placares baixos — o Poisson puro superestima
    0x0 e 1x1; com ρ > 0, esses placares são deflacionados e 1x0/0x1
    inflacionados, aproximando o modelo das frequências reais.
    """
    pa = np.array([math.exp(-lambda_a) * lambda_a**k / math.factorial(k) for k in range(MAX_GOLS + 1)])
    pb = np.array([math.exp(-lambda_b) * lambda_b**k / math.factorial(k) for k in range(MAX_GOLS + 1)])
    m = np.outer(pa, pb)
    if rho:
        m[0, 0] *= max(0.0, 1 - lambda_a * lambda_b * rho)
        m[0, 1] *= 1 + lambda_a * rho
        m[1, 0] *= 1 + lambda_b * rho
        m[1, 1] *= max(0.0, 1 - rho)
    return m / m.sum()


def placar_condicional(matriz: np.ndarray, resultado: str) -> tuple[str, float]:
    """Placar mais provável DENTRO de um desfecho ("vitoria_a"/"empate"/"vitoria_b").

    Evita o vício do 1x1: se o palpite é vitória, o placar exibido é a moda
    entre os placares de vitória, não a moda global da distribuição.
    """
    ii, jj = np.indices(matriz.shape)
    if resultado == "vitoria_a":
        mascara = ii > jj
    elif resultado == "vitoria_b":
        mascara = jj > ii
    else:
        mascara = ii == jj
    recorte = np.where(mascara, matriz, -1.0)
    a, b = np.unravel_index(int(np.argmax(recorte)), matriz.shape)
    return f"{a}x{b}", float(matriz[a, b] / matriz.sum())


def probabilidades_resultado(matriz: np.ndarray) -> dict:
    """Agrega a matriz de placares em P(vitória A), P(empate), P(vitória B)."""
    total = matriz.sum()  # normaliza o truncamento em MAX_GOLS
    return {
        "vitoria_a": float(np.tril(matriz, -1).sum() / total),
        "empate": float(np.trace(matriz) / total),
        "vitoria_b": float(np.triu(matriz, 1).sum() / total),
    }


def placares_mais_provaveis(matriz: np.ndarray, top: int = 5) -> list[tuple[str, float]]:
    """Top N placares com maior probabilidade individual."""
    flat = [
        (f"{a} x {b}", float(matriz[a, b]))
        for a in range(MAX_GOLS + 1)
        for b in range(MAX_GOLS + 1)
    ]
    return sorted(flat, key=lambda x: x[1], reverse=True)[:top]


@st.cache_data
def power_ranking(forcas: pd.DataFrame, historico: pd.DataFrame) -> pd.DataFrame:
    """Probabilidade de título: rating atual + forma + pedigree histórico em Copas.

    O score combina (60%) rating Elo-like, (25%) forma recente e (15%) o
    aproveitamento médio histórico nas últimas 5 Copas. As probabilidades
    são obtidas via softmax calibrado sobre o score.
    """
    pedigree = (
        historico[historico["jogos"] > 0]
        .groupby("selecao")["aproveitamento"].mean()
        .rename("pedigree")
    )
    df = forcas.merge(pedigree, on="selecao", how="left")
    df["pedigree"] = df["pedigree"].fillna(df["pedigree"].min())

    rating_norm = (df["rating"] - df["rating"].min()) / (df["rating"].max() - df["rating"].min())
    forma_norm = df["forma_recente"] / 100
    pedigree_norm = df["pedigree"] / 100
    df["score"] = 0.60 * rating_norm + 0.25 * forma_norm + 0.15 * pedigree_norm

    # Softmax com temperatura: concentra a probabilidade nos favoritos sem zerar o resto
    expos = np.exp(df["score"] * 6.5)
    df["prob_titulo"] = (expos / expos.sum() * 100).round(1)
    return df.sort_values("prob_titulo", ascending=False).reset_index(drop=True)


# ============================================================================
# SIMULAÇÃO DO TORNEIO — CHAVEAMENTO OFICIAL FIFA 2026 + MONTE CARLO
# ============================================================================

# Fase de 32 (jogos 73–88), conforme tabela oficial da FIFA.
# Slots: ("W", "E") = 1º do grupo E | ("R", "C") = 2º do grupo C
#        ("T", "ABCDF") = melhor 3º oriundo de um dos grupos listados
R32_ESTRUTURA = {
    73: (("R", "A"), ("R", "B")),
    74: (("W", "E"), ("T", "ABCDF")),
    75: (("W", "F"), ("R", "C")),
    76: (("W", "C"), ("R", "F")),
    77: (("W", "I"), ("T", "CDFGH")),
    78: (("R", "E"), ("R", "I")),
    79: (("W", "A"), ("T", "CEFHI")),
    80: (("W", "L"), ("T", "EHIJK")),
    81: (("W", "D"), ("T", "BEFIJ")),
    82: (("W", "G"), ("T", "AEHIJ")),
    83: (("R", "K"), ("R", "L")),
    84: (("W", "H"), ("R", "J")),
    85: (("W", "B"), ("T", "EFGIJ")),
    86: (("W", "J"), ("R", "H")),
    87: (("W", "K"), ("T", "DEIJL")),
    88: (("R", "D"), ("R", "G")),
}
R16_ESTRUTURA = {89: (74, 77), 90: (73, 75), 91: (76, 78), 92: (79, 80),
                 93: (83, 84), 94: (81, 82), 95: (86, 88), 96: (85, 87)}
QF_ESTRUTURA = {97: (89, 90), 98: (93, 94), 99: (91, 92), 100: (95, 96)}
SF_ESTRUTURA = {101: (97, 98), 102: (99, 100)}
SLOTS_TERCEIROS = [(mid, ref) for mid, (sa, sb) in R32_ESTRUTURA.items()
                   for tipo, ref in (sa, sb) if tipo == "T"]

# Níveis de avanço: 0=grupos, 1=fase de 32, 2=oitavas, 3=quartas,
# 4=semifinal, 5=final, 6=campeão
NIVEIS_TORNEIO = ["Grupos", "Fase de 32", "Oitavas", "Quartas",
                  "Semifinal", "Final", "Campeão"]


def _precomputar_lambdas(forcas: pd.DataFrame) -> dict:
    """Pré-calcula λ(a contra b) para todos os pares — acelera o Monte Carlo."""
    fa = forcas.set_index("selecao")
    defesa_media = forcas["defesa"].mean()
    lams = {}
    for a in fa.index:
        base = fa.loc[a, "ataque"] * (0.85 + 0.30 * fa.loc[a, "forma_recente"] / 100)
        for b in fa.index:
            if a != b:
                lams[(a, b)] = max(0.15, float(base * fa.loc[b, "defesa"] / defesa_media))
    return lams


def _simular_grupo(rng: np.random.Generator, lams: dict, times: list,
                   fixos: dict | None = None) -> tuple:
    """Round-robin de 4 times; jogos já disputados usam o placar real."""
    stats = {t: {"P": 0, "J": 0, "V": 0, "E": 0, "D": 0, "GP": 0, "GC": 0} for t in times}
    for i in range(4):
        for j in range(i + 1, 4):
            a, b = times[i], times[j]
            real = None
            if fixos:
                real = fixos.get((a, b))
                if real is None and (b, a) in fixos:
                    gb_r, ga_r = fixos[(b, a)]
                    real = (ga_r, gb_r)
            if real is not None:
                ga, gb = real
            else:
                ga = int(rng.poisson(lams[(a, b)]))
                gb = int(rng.poisson(lams[(b, a)]))
            stats[a]["J"] += 1; stats[b]["J"] += 1
            stats[a]["GP"] += ga; stats[a]["GC"] += gb
            stats[b]["GP"] += gb; stats[b]["GC"] += ga
            if ga > gb:
                stats[a]["P"] += 3; stats[a]["V"] += 1; stats[b]["D"] += 1
            elif gb > ga:
                stats[b]["P"] += 3; stats[b]["V"] += 1; stats[a]["D"] += 1
            else:
                stats[a]["P"] += 1; stats[b]["P"] += 1
                stats[a]["E"] += 1; stats[b]["E"] += 1
    ordem = sorted(
        times,
        key=lambda t: (stats[t]["P"], stats[t]["GP"] - stats[t]["GC"],
                       stats[t]["GP"], rng.random()),
        reverse=True,
    )
    return ordem, stats


def _alocar_terceiros(grupos_qualificados: set) -> dict:
    """Atribui os 8 melhores terceiros aos slots oficiais via backtracking.

    A FIFA define 495 combinações possíveis; aqui resolvemos a restrição
    'cada slot aceita terceiros de grupos específicos' por busca exata.
    """
    alocacao, usados = {}, set()

    def bt(i: int) -> bool:
        if i == len(SLOTS_TERCEIROS):
            return True
        mid, permitidos = SLOTS_TERCEIROS[i]
        for g in permitidos:
            if g in grupos_qualificados and g not in usados:
                alocacao[mid] = g
                usados.add(g)
                if bt(i + 1):
                    return True
                usados.discard(g)
                del alocacao[mid]
        return False

    if not bt(0):  # fallback raríssimo: ignora as listas e distribui na ordem
        restantes = sorted(grupos_qualificados)
        alocacao.update({mid: restantes.pop() for mid, _ in SLOTS_TERCEIROS})
    return alocacao


def _jogo_mata_mata(rng: np.random.Generator, lams: dict, a: str, b: str) -> tuple:
    """Simula jogo eliminatório; empate vai a 'pênaltis' ponderados pelos λ."""
    ga = int(rng.poisson(lams[(a, b)]))
    gb = int(rng.poisson(lams[(b, a)]))
    penaltis = ga == gb
    if penaltis:
        p_a = lams[(a, b)] / (lams[(a, b)] + lams[(b, a)])
        vencedor = a if rng.random() < p_a else b
    else:
        vencedor = a if ga > gb else b
    return ga, gb, vencedor, penaltis


def simular_copa(rng: np.random.Generator, lams: dict, grupos: dict,
                 detalhado: bool = False, fixos: dict | None = None) -> dict:
    """Simula a Copa 2026 completa (72 jogos de grupos + 31 de mata-mata).

    Jogos presentes em `fixos` (já disputados) entram com o placar real;
    o restante é sorteado via Poisson. Retorna níveis de avanço por seleção
    e, se `detalhado`, as tabelas de grupo e os placares do mata-mata.
    """
    niveis = {t: 0 for ts in grupos.values() for t in ts}
    detalhes = {"grupos": {}, "partidas": []}

    primeiro, segundo, terceiros = {}, {}, []
    for g in sorted(grupos):
        ordem, stats = _simular_grupo(rng, lams, grupos[g], fixos)
        primeiro[g], segundo[g] = ordem[0], ordem[1]
        terceiros.append((g, ordem[2], stats[ordem[2]]))
        if detalhado:
            detalhes["grupos"][g] = pd.DataFrame(
                [{"Seleção": t, **stats[t], "SG": stats[t]["GP"] - stats[t]["GC"]}
                 for t in ordem]
            )

    terceiros.sort(key=lambda x: (x[2]["P"], x[2]["GP"] - x[2]["GC"],
                                  x[2]["GP"], rng.random()), reverse=True)
    terceiro_do_grupo = {g: t for g, t, _ in terceiros[:8]}
    alocacao = _alocar_terceiros(set(terceiro_do_grupo))

    for t in (*primeiro.values(), *segundo.values(), *terceiro_do_grupo.values()):
        niveis[t] = 1

    def resolver_slot(slot: tuple, mid: int) -> str:
        tipo, ref = slot
        if tipo == "W":
            return primeiro[ref]
        if tipo == "R":
            return segundo[ref]
        return terceiro_do_grupo[alocacao[mid]]

    vencedores = {}
    rodadas = [("Fase de 32", R32_ESTRUTURA, 2), ("Oitavas", R16_ESTRUTURA, 3),
               ("Quartas", QF_ESTRUTURA, 4), ("Semifinal", SF_ESTRUTURA, 5)]
    for nome_fase, estrutura, nivel_vencedor in rodadas:
        for mid, (sa, sb) in estrutura.items():
            if nome_fase == "Fase de 32":
                a, b = resolver_slot(sa, mid), resolver_slot(sb, mid)
            else:
                a, b = vencedores[sa], vencedores[sb]
            ga, gb, venc, pen = _jogo_mata_mata(rng, lams, a, b)
            vencedores[mid] = venc
            niveis[venc] = nivel_vencedor
            if detalhado:
                detalhes["partidas"].append(
                    {"fase": nome_fase, "jogo": mid, "a": a, "ga": ga,
                     "gb": gb, "b": b, "vencedor": venc, "penaltis": pen})

    a, b = vencedores[101], vencedores[102]
    ga, gb, campeao, pen = _jogo_mata_mata(rng, lams, a, b)
    niveis[campeao] = 6
    if detalhado:
        detalhes["partidas"].append(
            {"fase": "FINAL", "jogo": 104, "a": a, "ga": ga, "gb": gb,
             "b": b, "vencedor": campeao, "penaltis": pen})

    vice = b if campeao == a else a
    return {"campeao": campeao, "vice": vice, "niveis": niveis,
            "detalhes": detalhes if detalhado else None}


@st.cache_data(show_spinner=False)
def rodar_monte_carlo(n_sims: int, seed: int, forcas: pd.DataFrame,
                      calendario: pd.DataFrame | None = None) -> tuple:
    """Roda `n_sims` Copas (resultados reais travados) e agrega probabilidades."""
    rng = np.random.default_rng(seed)
    lams = _precomputar_lambdas(forcas)
    grupos = forcas.groupby("grupo")["selecao"].apply(list).to_dict()
    fixos = extrair_resultados_fixos(calendario) if calendario is not None else None

    times = forcas["selecao"].tolist()
    contagem_nivel = {t: np.zeros(7, dtype=int) for t in times}
    finais, campeoes = {}, {}

    for _ in range(n_sims):
        r = simular_copa(rng, lams, grupos, fixos=fixos)
        for t, nv in r["niveis"].items():
            contagem_nivel[t][nv] += 1
        par_final = tuple(sorted((r["campeao"], r["vice"])))
        finais[par_final] = finais.get(par_final, 0) + 1
        campeoes[r["campeao"]] = campeoes.get(r["campeao"], 0) + 1

    linhas = []
    for t in times:
        acum = np.cumsum(contagem_nivel[t][::-1])[::-1]  # P(nível >= k)
        linhas.append({
            "selecao": t,
            "grupo": forcas.loc[forcas["selecao"] == t, "grupo"].iloc[0],
            "fase_32": acum[1] / n_sims * 100,
            "oitavas": acum[2] / n_sims * 100,
            "quartas": acum[3] / n_sims * 100,
            "semifinal": acum[4] / n_sims * 100,
            "final": acum[5] / n_sims * 100,
            "titulo": acum[6] / n_sims * 100,
        })
    df = (pd.DataFrame(linhas).round(1)
          .sort_values("titulo", ascending=False).reset_index(drop=True))
    top_finais = sorted(finais.items(), key=lambda kv: kv[1], reverse=True)[:5]
    return df, top_finais


# ============================================================================
# COMPONENTES DE INTERFACE — UMA FUNÇÃO POR ABA
# ============================================================================

def render_sidebar(historico: pd.DataFrame) -> dict:
    """Filtros globais na sidebar; retorna as escolhas do usuário."""
    st.sidebar.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Soccerball.svg/240px-Soccerball.svg.png",
        width=70,
    )
    st.sidebar.title("⚙️ Filtros de Análise")
    st.sidebar.caption("Os filtros afetam o Panorama Histórico e o Desempenho de Atletas.")

    selecoes_disponiveis = sorted(historico["selecao"].unique())
    selecoes = st.sidebar.multiselect(
        "Seleções em foco",
        options=selecoes_disponiveis,
        default=["Brasil", "Argentina", "França", "Espanha", "Inglaterra", "Alemanha"],
    )
    edicoes = st.sidebar.slider("Período (edições da Copa)", 2006, 2022, (2006, 2022), step=4)

    st.sidebar.divider()
    st.sidebar.markdown(
        "**🆕 Fator Copa 2026**\n\n"
        "Primeira edição com **48 seleções**: 12 grupos de 4, classificam-se os "
        "2 primeiros + os 8 melhores terceiros para uma inédita fase de 32. "
        "Campeão jogará **8 partidas** (uma a mais que o padrão histórico) — "
        "elenco profundo e rodízio físico pesam mais do que nunca.\n\n"
        "A aba **🏆 Simulação do Torneio** usa os grupos e o chaveamento "
        "**oficiais** do sorteio da FIFA."
    )
    st.sidebar.divider()
    with st.sidebar.expander("🧮 Parâmetros do modelo", expanded=False):
        rho = st.slider(
            "Correção Dixon-Coles (ρ)", -0.10, 0.20, 0.08, 0.01,
            help="O Poisson puro exagera 0x0 e 1x1. Com ρ > 0, esses placares "
                 "perdem probabilidade para 1x0/0x1. ρ = 0 desliga a correção.")
        bonus_mando = st.slider(
            "Vantagem dos anfitriões (%)", 0, 20, 8,
            help="Bônus de ataque para EUA, México e Canadá (jogam em casa). "
                 "Histórico: anfitriões rendem ~10% acima do esperado.")
        impacto_craque = st.slider(
            "Impacto do craque (%)", 0, 12, 5,
            help="Bônus máximo de ataque pelo melhor Índice de Eficiência da "
                 "seleção (aba Desempenho de Atletas).")
    st.sidebar.caption("Dados fictícios para demonstração, calibrados em padrões reais. v1.1")

    if not selecoes:
        selecoes = selecoes_disponiveis
        st.sidebar.warning("Nenhuma seleção marcada — exibindo todas.")
    return {"selecoes": selecoes, "edicoes": edicoes, "rho": rho,
            "bonus_mando": bonus_mando, "impacto_craque": impacto_craque}


def render_tab_historico(historico: pd.DataFrame, filtros: dict) -> None:
    """Tab 1 — Panorama Histórico: evolução de aproveitamento e gols."""
    st.subheader("📊 Panorama Histórico — Últimas 5 Copas (2006–2022)")

    ini, fim = filtros["edicoes"]
    df = historico[
        historico["selecao"].isin(filtros["selecoes"])
        & historico["edicao"].between(ini, fim)
        & (historico["jogos"] > 0)
    ]
    if df.empty:
        st.info("Ajuste os filtros na sidebar para visualizar os dados.")
        return

    # --- métricas destacadas ---
    melhor = df.loc[df["aproveitamento"].idxmax()]
    artilheira = df.groupby("selecao")["gols_pro"].sum().idxmax()
    gols_artilheira = int(df.groupby("selecao")["gols_pro"].sum().max())
    media_gols_jogo = (df["gols_pro"].sum() / df["jogos"].sum()).round(2)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏆 Melhor campanha", f"{melhor['selecao']} {int(melhor['edicao'])}",
              f"{melhor['aproveitamento']}% de aproveitamento")
    c2.metric("⚽ Ataque mais produtivo", artilheira, f"{gols_artilheira} gols no período")
    c3.metric("📈 Média de gols/jogo", f"{media_gols_jogo}", "no recorte filtrado")
    c4.metric("🎯 Campanhas analisadas", f"{len(df)}", f"{df['selecao'].nunique()} seleções")

    st.divider()

    # --- evolução do aproveitamento ---
    col_esq, col_dir = st.columns([3, 2])
    with col_esq:
        fig = px.line(
            df, x="edicao", y="aproveitamento", color="selecao",
            markers=True, color_discrete_map=PALETA_SELECOES,
            labels={"edicao": "Edição", "aproveitamento": "Aproveitamento (%)", "selecao": "Seleção"},
            title="Evolução do aproveitamento por edição",
        )
        fig.update_layout(hovermode="x unified", legend_title=None, height=420,
                          xaxis={"tickvals": sorted(df["edicao"].unique())})
        st.plotly_chart(fig, use_container_width=True)

    with col_dir:
        agg = (df.groupby("selecao", as_index=False)
                 .agg(gols_pro=("gols_pro", "sum"), gols_contra=("gols_contra", "sum")))
        fig2 = go.Figure()
        fig2.add_bar(x=agg["selecao"], y=agg["gols_pro"], name="Gols marcados",
                     marker_color=CORES["vitoria"])
        fig2.add_bar(x=agg["selecao"], y=agg["gols_contra"], name="Gols sofridos",
                     marker_color=CORES["derrota"])
        fig2.update_layout(barmode="group", title="Gols marcados x sofridos (acumulado)",
                           height=420, legend={"orientation": "h", "y": 1.12})
        st.plotly_chart(fig2, use_container_width=True)

    # --- trajetória fase a fase ---
    ordem_fases = ["Não classif.", "Grupos", "Oitavas", "Quartas",
                   "4º lugar", "3º lugar", "Vice", "Campeã"]
    df_fases = historico[historico["selecao"].isin(filtros["selecoes"])].copy()
    df_fases["nivel_fase"] = df_fases["fase"].map({f: i for i, f in enumerate(ordem_fases)})
    fig3 = px.scatter(
        df_fases, x="edicao", y="fase", color="selecao", size="gols_pro",
        size_max=22, color_discrete_map=PALETA_SELECOES,
        category_orders={"fase": ordem_fases},
        labels={"edicao": "Edição", "fase": "Fase alcançada", "gols_pro": "Gols marcados"},
        title="Até onde cada seleção chegou (tamanho da bolha = gols marcados)",
    )
    fig3.update_layout(height=430, xaxis={"tickvals": sorted(historico["edicao"].unique())})
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("📋 Dados completos do recorte"):
        st.dataframe(
            df.sort_values(["selecao", "edicao"]),
            use_container_width=True, hide_index=True,
        )


def render_tab_atletas(jogadores: pd.DataFrame, filtros: dict) -> None:
    """Tab 2 — Desempenho de Atletas: ranking de eficiência e heatmap."""
    st.subheader("🏃‍♂️ Desempenho de Atletas — Últimos 12 meses (clube + seleção)")

    top3 = jogadores.head(3)
    c1, c2, c3 = st.columns(3)
    for col, (_, j) in zip((c1, c2, c3), top3.iterrows()):
        col.metric(
            f"⭐ {j['jogador']} ({j['selecao']})",
            f"Índice {j['indice_eficiencia']}",
            f"{j['participacoes_90']} participações em gol / 90 min",
        )

    st.divider()
    col_tab, col_heat = st.columns([3, 2])

    with col_tab:
        st.markdown("**Ranking de eficiência** — ordene clicando nos cabeçalhos:")
        st.dataframe(
            jogadores[["jogador", "selecao", "posicao", "jogos", "minutos", "gols",
                       "assistencias", "participacoes_90", "aproveitamento_selecao",
                       "nota_media", "indice_eficiencia"]],
            use_container_width=True, hide_index=True, height=560,
            column_config={
                "jogador": "Jogador",
                "selecao": "Seleção",
                "posicao": "Pos.",
                "jogos": st.column_config.NumberColumn("J"),
                "minutos": st.column_config.NumberColumn("Min"),
                "gols": st.column_config.NumberColumn("⚽ Gols"),
                "assistencias": st.column_config.NumberColumn("🎯 Assist."),
                "participacoes_90": st.column_config.NumberColumn(
                    "G+A/90", help="Gols + assistências a cada 90 minutos"),
                "aproveitamento_selecao": st.column_config.ProgressColumn(
                    "Aprov. seleção", format="%d%%", min_value=0, max_value=100,
                    help="Aproveitamento de pontos da seleção com o atleta em campo"),
                "nota_media": st.column_config.NumberColumn("Nota", format="%.1f"),
                "indice_eficiencia": st.column_config.ProgressColumn(
                    "Índice de Eficiência", format="%.1f", min_value=0, max_value=100),
            },
        )

    with col_heat:
        st.markdown("**Heatmap normalizado** — Top 12 por eficiência:")
        metricas = ["participacoes_90", "aproveitamento_selecao", "nota_media", "indice_eficiencia"]
        rotulos = ["G+A / 90", "Aprov. seleção", "Nota média", "Índice"]
        top12 = jogadores.head(12).set_index("jogador")
        normalizado = (top12[metricas] - top12[metricas].min()) / (
            top12[metricas].max() - top12[metricas].min()
        )
        fig = px.imshow(
            normalizado.values,
            x=rotulos, y=top12.index.tolist(),
            color_continuous_scale=["#FFF8E1", "#FFC107", "#1B5E20"],
            aspect="auto",
            labels={"color": "Score (0–1)"},
        )
        fig.update_layout(height=560, coloraxis_showscale=False)
        fig.update_traces(
            text=np.round(normalizado.values, 2), texttemplate="%{text}",
            hovertemplate="<b>%{y}</b><br>%{x}: %{z:.2f}<extra></extra>",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Índice de Eficiência = 45% produção ofensiva (G+A/90, normalizado) "
        "+ 30% nota média + 25% aproveitamento da seleção com o atleta em campo."
    )


def prever_jogo(forcas: pd.DataFrame, time_a: str, time_b: str,
                rho: float = 0.0) -> dict:
    """Previsão compacta: probabilidades + placar típico DO desfecho apontado."""
    lambda_a, lambda_b = gols_esperados(forcas, time_a, time_b)
    matriz = matriz_poisson(lambda_a, lambda_b, rho)
    probs = probabilidades_resultado(matriz)
    if probs["vitoria_a"] >= max(probs["empate"], probs["vitoria_b"]):
        chave, palpite = "vitoria_a", f"Vitória {time_a}"
    elif probs["vitoria_b"] >= probs["empate"]:
        chave, palpite = "vitoria_b", f"Vitória {time_b}"
    else:
        chave, palpite = "empate", "Empate"
    placar, p_placar = placar_condicional(matriz, chave)
    return {"vitoria_a": probs["vitoria_a"] * 100, "empate": probs["empate"] * 100,
            "vitoria_b": probs["vitoria_b"] * 100, "placar": placar,
            "p_placar": p_placar * 100, "palpite": palpite}


def render_palpites_calendario(forcas: pd.DataFrame, calendario: pd.DataFrame,
                               rho: float = 0.0) -> None:
    """Palpites do modelo para os jogos reais da fase de grupos, por data."""
    st.markdown("#### 📅 Palpites do calendário real (fase de grupos)")

    datas = list(calendario["data"].unique())
    hoje = date.today().strftime("%d/%m")
    indice_padrao = datas.index(hoje) if hoje in datas else 0
    col_d, col_info = st.columns([2, 3])
    data_sel = col_d.selectbox("Escolha o dia", datas, index=indice_padrao,
                               format_func=lambda d: f"{d} {'(hoje)' if d == hoje else ''}")
    jogos_dia = calendario[calendario["data"] == data_sel]
    col_info.markdown(
        f"<br>**{len(jogos_dia)} jogo(s)** em {data_sel} — rodada "
        f"{jogos_dia['rodada'].iloc[0]} da fase de grupos.",
        unsafe_allow_html=True,
    )

    linhas = []
    for _, jogo in jogos_dia.iterrows():
        prev = prever_jogo(forcas, jogo["time_a"], jogo["time_b"], rho)
        resultado_str = "—"
        if pd.notna(jogo["resultado"]):
            ga, gb = _parse_placar(jogo["resultado"])
            real = (f"Vitória {jogo['time_a']}" if ga > gb
                    else f"Vitória {jogo['time_b']}" if gb > ga else "Empate")
            acerto = "✅" if real == prev["palpite"] else "❌"
            resultado_str = f"{jogo['resultado']} {acerto}"
        linhas.append({
            "Grupo": jogo["grupo"],
            "Jogo": f"{jogo['time_a']} x {jogo['time_b']}",
            f"Vit. mandante (%)": round(prev["vitoria_a"], 1),
            "Empate (%)": round(prev["empate"], 1),
            f"Vit. visitante (%)": round(prev["vitoria_b"], 1),
            "Placar típico do palpite": f"{prev['placar']} ({prev['p_placar']:.0f}%)",
            "Palpite do modelo": prev["palpite"],
            "Resultado real": resultado_str,
        })
    df_palpites = pd.DataFrame(linhas)
    st.dataframe(
        df_palpites, use_container_width=True, hide_index=True,
        column_config={
            "Vit. mandante (%)": st.column_config.ProgressColumn(
                "Vit. 1º time", format="%.1f%%", min_value=0, max_value=100),
            "Empate (%)": st.column_config.ProgressColumn(
                "Empate", format="%.1f%%", min_value=0, max_value=100),
            "Vit. visitante (%)": st.column_config.ProgressColumn(
                "Vit. 2º time", format="%.1f%%", min_value=0, max_value=100),
        },
    )
    st.caption(
        "Selecione qualquer confronto no simulador abaixo para ver a análise "
        "completa (matriz de placares, head-to-head e xG)."
    )


def render_recalibragem(ajustes: pd.DataFrame) -> None:
    """Painel com o efeito dos resultados reais sobre o modelo."""
    if ajustes.empty:
        return
    with st.expander(f"🔄 Modelo recalibrado com {len(ajustes)} resultado(s) real(is)"):
        st.markdown(
            "Cada placar real atualiza **rating** (Elo, K=40), **forma recente** "
            "(média móvel 85/15) e **ataque/defesa** (ajuste β=0.15 normalizado "
            "pela força do adversário). Jogos disputados também entram travados "
            "na Simulação do Torneio."
        )
        st.dataframe(
            ajustes.rename(columns={"data": "Data", "jogo": "Jogo",
                                    "delta_rating": "Δ rating",
                                    "beneficiado": "Quem subiu"}),
            hide_index=True, use_container_width=True,
        )


def render_fatores_extras(fatores: pd.DataFrame) -> None:
    """Painel de transparência: quais seleções recebem bônus contextuais."""
    if fatores.empty:
        return
    with st.expander(f"🧮 Fatores extras ativos em {len(fatores)} seleção(ões)"):
        st.markdown(
            "Ajuste os pesos na sidebar (**Parâmetros do modelo**). Bônus de "
            "anfitrião e de craque entram nos gols esperados de todas as "
            "previsões e simulações; a correção Dixon-Coles (ρ) redistribui "
            "a probabilidade entre os placares baixos."
        )
        st.dataframe(
            fatores.rename(columns={"selecao": "Seleção", "fatores": "Bônus aplicados"}),
            hide_index=True, use_container_width=True,
        )


def render_tab_simulador(forcas: pd.DataFrame, historico: pd.DataFrame,
                         h2h: pd.DataFrame, calendario: pd.DataFrame,
                         ajustes: pd.DataFrame, fatores: pd.DataFrame,
                         rho: float) -> None:
    """Tab 3 — Palpites do calendário + simulador de confrontos (Poisson)."""
    st.subheader("🔮 Simulador de Confrontos & Probabilidades de Título")
    st.caption(
        "Modelo: Poisson com correção Dixon-Coles (ρ ajustável na sidebar), gols "
        "esperados por ataque x defesa, forma recente (±15%), bônus de anfitrião "
        "e impacto do craque da seleção."
    )

    render_palpites_calendario(forcas, calendario, rho)
    render_recalibragem(ajustes)
    render_fatores_extras(fatores)
    st.divider()
    st.markdown("#### ⚔️ Monte seu confronto")

    selecoes = forcas["selecao"].tolist()
    col_a, col_x, col_b = st.columns([5, 1, 5])
    with col_a:
        time_a = st.selectbox("🏠 Seleção A", selecoes, index=selecoes.index("Brasil"))
    with col_x:
        st.markdown("<h3 style='text-align:center; margin-top:28px;'>VS</h3>",
                    unsafe_allow_html=True)
    with col_b:
        time_b = st.selectbox("✈️ Seleção B", selecoes, index=selecoes.index("Argentina"))

    if time_a == time_b:
        st.warning("Escolha duas seleções diferentes para simular o confronto.")
    else:
        lambda_a, lambda_b = gols_esperados(forcas, time_a, time_b)
        matriz = matriz_poisson(lambda_a, lambda_b, rho)
        probs = probabilidades_resultado(matriz)

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric(f"Vitória {time_a}", f"{probs['vitoria_a']*100:.1f}%")
        m2.metric("Empate", f"{probs['empate']*100:.1f}%")
        m3.metric(f"Vitória {time_b}", f"{probs['vitoria_b']*100:.1f}%")
        m4.metric(f"xG {time_a}", f"{lambda_a:.2f}")
        m5.metric(f"xG {time_b}", f"{lambda_b:.2f}")

        fig_prob = go.Figure(go.Bar(
            x=[probs["vitoria_a"] * 100, probs["empate"] * 100, probs["vitoria_b"] * 100],
            y=[f"Vitória {time_a}", "Empate", f"Vitória {time_b}"],
            orientation="h",
            marker_color=[CORES["vitoria"], CORES["empate"], CORES["derrota"]],
            text=[f"{probs['vitoria_a']*100:.1f}%", f"{probs['empate']*100:.1f}%",
                  f"{probs['vitoria_b']*100:.1f}%"],
            textposition="auto",
        ))
        fig_prob.update_layout(title="Distribuição de probabilidades do confronto",
                               height=260, xaxis_title="Probabilidade (%)",
                               margin={"t": 50, "b": 30})
        st.plotly_chart(fig_prob, use_container_width=True)

        col_placar, col_h2h = st.columns(2)
        with col_placar:
            st.markdown("**Placares mais prováveis:**")
            for placar, p in placares_mais_provaveis(matriz):
                gols_a, gols_b = placar.split(" x ")
                st.markdown(
                    f"- **{time_a} {gols_a} x {gols_b} {time_b}** — "
                    f"`{p*100:.1f}%` de probabilidade"
                )

        with col_h2h:
            st.markdown("**Histórico do confronto direto:**")
            registro = h2h[
                ((h2h["time_a"] == time_a) & (h2h["time_b"] == time_b))
                | ((h2h["time_a"] == time_b) & (h2h["time_b"] == time_a))
            ]
            if registro.empty:
                st.info("Sem histórico relevante de confrontos diretos na base.")
            else:
                r = registro.iloc[0]
                invertido = r["time_a"] != time_a
                v_a = int(r["vitorias_b"] if invertido else r["vitorias_a"])
                v_b = int(r["vitorias_a"] if invertido else r["vitorias_b"])
                fig_h2h = go.Figure(go.Pie(
                    labels=[f"{time_a} ({v_a})", f"Empates ({int(r['empates'])})",
                            f"{time_b} ({v_b})"],
                    values=[v_a, int(r["empates"]), v_b],
                    marker={"colors": [CORES["vitoria"], CORES["empate"], CORES["derrota"]]},
                    hole=0.45,
                ))
                fig_h2h.update_layout(
                    height=260, margin={"t": 30, "b": 10},
                    title=f"{int(r['jogos'])} jogos oficiais disputados",
                )
                st.plotly_chart(fig_h2h, use_container_width=True)

        with st.expander("🔬 Matriz completa de placares (Poisson)"):
            fig_m = px.imshow(
                matriz[:6, :6] * 100,
                x=[f"{g} gol(s) {time_b}" for g in range(6)],
                y=[f"{g} gol(s) {time_a}" for g in range(6)],
                color_continuous_scale="Greens", text_auto=".1f",
                labels={"color": "Prob. (%)"},
            )
            fig_m.update_layout(height=420)
            st.plotly_chart(fig_m, use_container_width=True)

    st.divider()

    # --- Power Ranking ---
    st.subheader("🏆 Power Ranking — Quem levanta a taça em 2026?")
    ranking = power_ranking(forcas, historico)
    top5 = ranking.head(5)

    cols = st.columns(5)
    medalhas = ["🥇", "🥈", "🥉", "4º", "5º"]
    for col, medalha, (_, linha) in zip(cols, medalhas, top5.iterrows()):
        col.metric(f"{medalha} {linha['selecao']}", f"{linha['prob_titulo']}%",
                   f"Rating {int(linha['rating'])}")

    fig_rank = px.bar(
        ranking.head(10), x="prob_titulo", y="selecao", orientation="h",
        color="prob_titulo", color_continuous_scale=["#E8F5E9", "#1B5E20"],
        text="prob_titulo",
        labels={"prob_titulo": "Probabilidade de título (%)", "selecao": ""},
        title="Top 10 — probabilidade de título (rating 60% + forma 25% + pedigree 15%)",
    )
    fig_rank.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_rank.update_layout(height=430, coloraxis_showscale=False,
                           yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_rank, use_container_width=True)


def render_tab_torneio(forcas: pd.DataFrame, calendario: pd.DataFrame) -> None:
    """Tab 4 — Simulação Monte Carlo da Copa 2026 com a tabela oficial."""
    st.subheader("🏆 Simulação do Torneio — Tabela Oficial da Copa 2026")
    n_jogados = calendario["resultado"].notna().sum()
    st.caption(
        "Grupos do sorteio oficial da FIFA e chaveamento real (jogos 73–104, da fase "
        "de 32 à final no MetLife Stadium). Cada Copa simulada joga os 72 jogos de "
        "grupos + 31 de mata-mata com o modelo de Poisson; os 8 melhores terceiros "
        "são alocados aos slots oficiais por busca exata. "
        f"**{n_jogados} jogo(s) já disputado(s) entram com o placar real** — as "
        "probabilidades refletem o torneio daqui em diante."
    )

    grupos = forcas.groupby("grupo")["selecao"].apply(list).to_dict()
    with st.expander("🗂️ Grupos oficiais (sorteio FIFA)"):
        colunas = st.columns(4)
        for i, g in enumerate(sorted(grupos)):
            with colunas[i % 4]:
                st.markdown(f"**Grupo {g}**")
                for t in grupos[g]:
                    st.markdown(f"- {t}")

    c1, c2 = st.columns(2)
    n_sims = c1.slider("⚙️ Número de Copas simuladas", 200, 5000, 1000, step=200,
                       help="Mais simulações = probabilidades mais estáveis (e mais lentas).")
    seed = c2.number_input("🎲 Semente aleatória", 1, 99999, 2026,
                           help="Mesma semente = mesmos resultados (reprodutibilidade).")

    with st.spinner(f"Simulando {n_sims} Copas do Mundo..."):
        probs, top_finais = rodar_monte_carlo(n_sims, int(seed), forcas, calendario)

    lider = probs.iloc[0]
    brasil = probs[probs["selecao"] == "Brasil"].iloc[0]
    (fa, fb), n_final = top_finais[0]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🥇 Campeão mais provável", lider["selecao"], f"{lider['titulo']}% dos títulos")
    m2.metric("🎬 Final mais comum", f"{fa} x {fb}", f"{n_final / n_sims * 100:.1f}% das simulações")
    m3.metric("🇧🇷 Brasil campeão", f"{brasil['titulo']}%", f"{brasil['final']}% chega à final")
    azarao = probs.iloc[8:].iloc[0] if len(probs) > 8 else lider
    m4.metric("🐎 Melhor azarão", azarao["selecao"], f"{azarao['titulo']}% de título")

    st.divider()
    col_graf, col_tab = st.columns([2, 3])

    with col_graf:
        top12 = probs.head(12)
        fig = px.bar(
            top12, x="titulo", y="selecao", orientation="h", text="titulo",
            color="titulo", color_continuous_scale=["#E8F5E9", "#1B5E20"],
            labels={"titulo": "Probabilidade de título (%)", "selecao": ""},
            title=f"Chances de título — {n_sims} Copas simuladas",
        )
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(height=520, coloraxis_showscale=False,
                          yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Finais mais frequentes:**")
        for (ta, tb), n in top_finais:
            st.markdown(f"- {ta} x {tb} — `{n / n_sims * 100:.1f}%`")

    with col_tab:
        st.markdown("**Probabilidade de alcançar cada fase (%):**")
        config_fase = {
            campo: st.column_config.ProgressColumn(
                rotulo, format="%.1f%%", min_value=0, max_value=100)
            for campo, rotulo in [("fase_32", "Fase de 32"), ("oitavas", "Oitavas"),
                                  ("quartas", "Quartas"), ("semifinal", "Semis"),
                                  ("final", "Final"), ("titulo", "🏆 Título")]
        }
        st.dataframe(
            probs, use_container_width=True, hide_index=True, height=560,
            column_config={"selecao": "Seleção", "grupo": "Grupo", **config_fase},
        )

    st.divider()
    st.markdown("### 🎲 Uma Copa simulada, lance a lance")
    st.caption("Um único universo possível — mude a semente acima para sortear outro destino.")
    if st.toggle("Mostrar simulação detalhada de uma Copa"):
        rng = np.random.default_rng(int(seed) * 7 + 1)
        lams = _precomputar_lambdas(forcas)
        copa = simular_copa(rng, lams, grupos, detalhado=True,
                            fixos=extrair_resultados_fixos(calendario))

        st.success(
            f"🏆 **Campeão: {copa['campeao']}** — venceu {copa['vice']} na decisão."
        )
        with st.expander("Classificação final dos 12 grupos"):
            colunas = st.columns(3)
            for i, g in enumerate(sorted(copa["detalhes"]["grupos"])):
                with colunas[i % 3]:
                    st.markdown(f"**Grupo {g}**")
                    st.dataframe(copa["detalhes"]["grupos"][g],
                                 hide_index=True, use_container_width=True)

        partidas = pd.DataFrame(copa["detalhes"]["partidas"])
        for fase in ["Fase de 32", "Oitavas", "Quartas", "Semifinal", "FINAL"]:
            jogos_fase = partidas[partidas["fase"] == fase]
            if jogos_fase.empty:
                continue
            st.markdown(f"**{fase}**")
            linhas = []
            for _, p in jogos_fase.iterrows():
                pen = " (pên.)" if p["penaltis"] else ""
                linhas.append(
                    f"`J{p['jogo']}` {p['a']} **{p['ga']} x {p['gb']}** {p['b']}"
                    f"{pen} → ✅ {p['vencedor']}"
                )
            st.markdown("  \n".join(linhas))


def render_tab_cronica(forcas: pd.DataFrame, historico: pd.DataFrame,
                       jogadores: pd.DataFrame) -> None:
    """Tab 4 — Crônica do Especialista: a narrativa por trás dos números."""
    st.subheader("✍️ Crônica do Especialista")
    ranking = power_ranking(forcas, historico)
    lider = ranking.iloc[0]
    craque = jogadores.iloc[0]

    st.markdown(
        f"""
<div class="cronica-box">

<h4>🖋️ A Copa dos 48: onde a matemática encontra o caos</h4>

<p><em>Por um cientista de dados apaixonado por futebol — junho de 2026</em></p>

<p>Os números raramente mentem, mas adoram pregar peças. O nosso modelo coloca a
<b>{lider['selecao']}</b> no topo do Power Ranking, com <b>{lider['prob_titulo']}%</b> de
probabilidade de título — fruto da combinação rara entre rating de elite, forma recente de
<b>{lider['forma_recente']:.0f}%</b> de aproveitamento e um pedigree de Copa que os dados das
últimas cinco edições confirmam. Mas quem acompanha Mundiais sabe: probabilidade não é destino.
A Espanha de 2010 chegou derrotada na estreia; a Alemanha de 2018 chegou campeã e caiu na fase
de grupos com aproveitamento pífio de 33%. O futebol cobra pedágio de quem confia demais no passado.</p>

<h5>📐 O que os dados gritam</h5>

<p><b>1. A era dos ataques 2.0.</b> A média de gols esperados dos cinco primeiros do ranking
ultrapassa 1.9 por jogo — número que em 2006 era privilégio de uma ou duas seleções. O futebol
de seleções importou a verticalidade dos clubes, e a régua defensiva subiu junto: Argentina e
Espanha sofrem, no modelo, menos de 0.75 gol por partida. Quem não tiver as duas pontas da
equação não passa das quartas.</p>

<p><b>2. O efeito {craque['jogador']}.</b> O líder do nosso Índice de Eficiência
({craque['indice_eficiencia']:.1f} pontos) registra {craque['participacoes_90']} participações
em gol a cada 90 minutos. Mais revelador: o aproveitamento de sua seleção com ele em campo é de
{craque['aproveitamento_selecao']}%. Em mata-mata de jogo único, um atleta dessa magnitude vale
de 8 a 12 pontos percentuais de probabilidade — é a diferença entre cara ou coroa e moeda viciada.</p>

<p><b>3. O imposto das 8 partidas.</b> Pela primeira vez, o campeão precisará vencer uma
maratona de oito jogos em ~35 dias. Nosso histórico mostra que seleções dependentes de uma
espinha dorsal curta (Croácia 2018, Marrocos 2022) chegam às fases finais com queda mensurável
de rendimento. Em 2026, profundidade de elenco deixa de ser luxo estatístico e vira variável
de sobrevivência. Vantagem para quem roda 16, 17 jogadores sem perder padrão.</p>

<h5>🐎 Dark horses: onde mora a surpresa</h5>

<p><b>Marrocos</b> não foi acidente. O 4º lugar de 2022 veio com a melhor defesa relativa do
torneio, e o modelo segue premiando essa solidez: 0.80 gol sofrido esperado por jogo, atrás
apenas do trio de elite. Com Hakimi no auge, repetir um quartas é piso, não teto.
<b>Japão</b> é o dark horse metodológico: duas oitavas seguidas, vitórias sobre Alemanha e
Espanha em 2022, e a geração mais europeizada de sua história. E fique de olho na
<b>Colômbia</b> — o aproveitamento recente de 69% não aparece nas manchetes, mas aparece
no nosso softmax.</p>

<h5>🎯 Veredito</h5>

<p>O formato de 48 dilui o risco dos favoritos na fase de grupos — com 32 classificados,
zebra grande agora precisa sobreviver a uma rodada extra de mata-mata para fazer história.
Tradução estatística: <b>a variância migrou da fase de grupos para o pente-fino das oitavas e
quartas</b>. Espere menos eliminações precoces de gigantes e mais batalhas épicas a partir
da fase de 16. O modelo aponta o favorito; a bola, como sempre, terá a palavra final.
É por isso que rodamos os números — e é por isso que assistimos aos jogos.</p>

</div>
""",
        unsafe_allow_html=True,
    )

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("🎲 Prob. do favorito", f"{lider['prob_titulo']}%",
              "vs ~6% se todas fossem iguais", delta_color="normal")
    pico_zebras = ranking[ranking["selecao"].isin(["Marrocos", "Japão", "Colômbia"])]["prob_titulo"].sum()
    c2.metric("🐎 Soma dos dark horses", f"{pico_zebras:.1f}%", "Marrocos + Japão + Colômbia")
    c3.metric("📅 Jogos até o título", "8 partidas", "+1 vs formato anterior")


# ============================================================================
# APLICAÇÃO PRINCIPAL
# ============================================================================

def main() -> None:
    st.markdown(CSS_CUSTOM, unsafe_allow_html=True)
    st.markdown('<p class="main-title">⚽ Copa 2026 Analytics</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Análise histórica, métricas de atletas e previsões preditivas '
        "para a primeira Copa do Mundo com 48 seleções</p>",
        unsafe_allow_html=True,
    )

    historico = carregar_historico_copas()
    jogadores = carregar_jogadores()
    h2h = carregar_head_to_head()
    calendario = carregar_calendario()

    filtros = render_sidebar(historico)
    # Recalibra com resultados reais e aplica fatores contextuais (sidebar)
    forcas, ajustes = aplicar_resultados(carregar_forcas_2026(), calendario)
    forcas, fatores = aplicar_fatores_extras(
        forcas, jogadores, filtros["bonus_mando"], filtros["impacto_craque"])
    if not ajustes.empty:
        st.sidebar.success(
            f"🔄 Modelo recalibrado com {len(ajustes)} resultado(s) real(is) "
            "da fase de grupos."
        )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Panorama Histórico",
        "🏃‍♂️ Desempenho de Atletas",
        "🔮 Simulador e Previsões",
        "🏆 Simulação do Torneio",
        "✍️ Crônica do Especialista",
    ])
    with tab1:
        render_tab_historico(historico, filtros)
    with tab2:
        render_tab_atletas(jogadores, filtros)
    with tab3:
        render_tab_simulador(forcas, historico, h2h, calendario, ajustes,
                             fatores, filtros["rho"])
    with tab4:
        render_tab_torneio(forcas, calendario)
    with tab5:
        render_tab_cronica(forcas, historico, jogadores)


if __name__ == "__main__":
    main()
