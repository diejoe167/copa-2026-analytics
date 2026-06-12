# -*- coding: utf-8 -*-
"""
🏛️ MUSEU DAS COPAS — Base histórica completa (1930–2022)
=========================================================
Todas as 22 edições da Copa do Mundo, com dados consistentes e verificados.

IMPORTANTE: este módulo é PROPOSITALMENTE isolado do modelo preditivo.
A Copa de 1930 não diz nada sobre 2026 — o simulador usa apenas as forças
atuais, o pedigree recente (2006–2022) e a recalibração com jogos reais.
Aqui é acervo: para explorar, comparar eras e contar histórias.
"""

import pandas as pd
import streamlit as st


@st.cache_data
def carregar_museu() -> pd.DataFrame:
    """Todas as Copas do Mundo: finais, sedes, artilheiros e métricas de era."""
    copas = [
        # (edição, sede, campeão, placar_final, vice, terceiro,
        #  nº seleções, jogos, gols, artilheiro, gols do artilheiro)
        (1930, "Uruguai", "Uruguai", "4x2", "Argentina", "Estados Unidos",
         13, 18, 70, "Guillermo Stábile (ARG)", 8),
        (1934, "Itália", "Itália", "2x1 (pror.)", "Tchecoslováquia", "Alemanha",
         16, 17, 70, "Oldřich Nejedlý (TCH)", 5),
        (1938, "França", "Itália", "4x2", "Hungria", "Brasil",
         15, 18, 84, "Leônidas da Silva (BRA)", 7),
        (1950, "Brasil", "Uruguai", "2x1 (Maracanazo)", "Brasil", "Suécia",
         13, 22, 88, "Ademir (BRA)", 8),
        (1954, "Suíça", "Alemanha", "3x2", "Hungria", "Áustria",
         16, 26, 140, "Sándor Kocsis (HUN)", 11),
        (1958, "Suécia", "Brasil", "5x2", "Suécia", "França",
         16, 35, 126, "Just Fontaine (FRA)", 13),
        (1962, "Chile", "Brasil", "3x1", "Tchecoslováquia", "Chile",
         16, 32, 89, "Seis jogadores empatados", 4),
        (1966, "Inglaterra", "Inglaterra", "4x2 (pror.)", "Alemanha", "Portugal",
         16, 32, 89, "Eusébio (POR)", 9),
        (1970, "México", "Brasil", "4x1", "Itália", "Alemanha",
         16, 32, 95, "Gerd Müller (ALE)", 10),
        (1974, "Alemanha", "Alemanha", "2x1", "Países Baixos", "Polônia",
         16, 38, 97, "Grzegorz Lato (POL)", 7),
        (1978, "Argentina", "Argentina", "3x1 (pror.)", "Países Baixos", "Brasil",
         16, 38, 102, "Mario Kempes (ARG)", 6),
        (1982, "Espanha", "Itália", "3x1", "Alemanha", "Polônia",
         24, 52, 146, "Paolo Rossi (ITA)", 6),
        (1986, "México", "Argentina", "3x2", "Alemanha", "França",
         24, 52, 132, "Gary Lineker (ING)", 6),
        (1990, "Itália", "Alemanha", "1x0", "Argentina", "Itália",
         24, 52, 115, "Salvatore Schillaci (ITA)", 6),
        (1994, "Estados Unidos", "Brasil", "0x0 (3x2 pên.)", "Itália", "Suécia",
         24, 52, 141, "Salenko (RUS) e Stoichkov (BUL)", 6),
        (1998, "França", "França", "3x0", "Brasil", "Croácia",
         32, 64, 171, "Davor Šuker (CRO)", 6),
        (2002, "Coreia do Sul/Japão", "Brasil", "2x0", "Alemanha", "Turquia",
         32, 64, 161, "Ronaldo (BRA)", 8),
        (2006, "Alemanha", "Itália", "1x1 (5x3 pên.)", "França", "Alemanha",
         32, 64, 147, "Miroslav Klose (ALE)", 5),
        (2010, "África do Sul", "Espanha", "1x0 (pror.)", "Países Baixos", "Alemanha",
         32, 64, 145, "Thomas Müller (ALE)", 5),
        (2014, "Brasil", "Alemanha", "1x0 (pror.)", "Argentina", "Países Baixos",
         32, 64, 171, "James Rodríguez (COL)", 6),
        (2018, "Rússia", "França", "4x2", "Croácia", "Bélgica",
         32, 64, 169, "Harry Kane (ING)", 6),
        (2022, "Catar", "Argentina", "3x3 (4x2 pên.)", "França", "Croácia",
         32, 64, 172, "Kylian Mbappé (FRA)", 8),
    ]
    df = pd.DataFrame(copas, columns=[
        "edicao", "sede", "campeao", "placar_final", "vice", "terceiro",
        "selecoes", "jogos", "gols", "artilheiro", "gols_artilheiro",
    ])
    df["gols_por_jogo"] = (df["gols"] / df["jogos"]).round(2)
    return df


@st.cache_data
def titulos_por_selecao(museu: pd.DataFrame) -> pd.DataFrame:
    """Ranking de títulos mundiais (Alemanha inclui Alemanha Ocidental)."""
    contagem = museu["campeao"].value_counts().reset_index()
    contagem.columns = ["selecao", "titulos"]
    return contagem
