# -*- coding: utf-8 -*-
"""
🌐 INTEGRAÇÃO COM API DE FUTEBOL (football-data.org)
====================================================
Puxa placares ao vivo, resultados finalizados e artilharia REAIS da Copa.

Tudo aqui é OPCIONAL e tolerante a falha: sem chave de API ou sem rede, as
funções devolvem vazio e o app cai no modo manual (calendário + JOGOS_AO_VIVO).

Como ativar (grátis):
1. Crie uma conta em https://www.football-data.org/client/register
2. Copie seu token (X-Auth-Token).
3. No Streamlit Cloud: App → Settings → Secrets, adicione:
       FOOTBALL_DATA_TOKEN = "seu_token_aqui"
   Localmente: crie .streamlit/secrets.toml com a mesma linha
   (ou defina a variável de ambiente FOOTBALL_DATA_TOKEN).
"""

import os

import pandas as pd
import streamlit as st

try:
    import requests
except ImportError:  # requests é dependência padrão do Streamlit, mas guardamos
    requests = None

API_BASE = "https://api.football-data.org/v4"
COMPETICAO = "WC"  # código da Copa do Mundo na football-data.org

# Mapa nome da API (inglês) -> nosso nome (português). Ajuste se algum
# confronto não casar quando os dados reais chegarem.
MAPA_NOMES = {
    "Brazil": "Brasil", "Argentina": "Argentina", "France": "França",
    "Germany": "Alemanha", "Spain": "Espanha", "England": "Inglaterra",
    "Portugal": "Portugal", "Netherlands": "Países Baixos", "Croatia": "Croácia",
    "Uruguay": "Uruguai", "Belgium": "Bélgica", "Morocco": "Marrocos",
    "Japan": "Japão", "Mexico": "México", "United States": "Estados Unidos",
    "USA": "Estados Unidos", "Colombia": "Colômbia", "Switzerland": "Suíça",
    "Canada": "Canadá", "Qatar": "Catar", "Ecuador": "Equador",
    "Senegal": "Senegal", "Norway": "Noruega", "South Korea": "Coreia do Sul",
    "Korea Republic": "Coreia do Sul", "Czech Republic": "Rep. Checa",
    "Czechia": "Rep. Checa", "South Africa": "África do Sul",
    "Bosnia and Herzegovina": "Bósnia e Herzegovina", "Paraguay": "Paraguai",
    "Australia": "Austrália", "Turkey": "Turquia", "Türkiye": "Turquia",
    "Curaçao": "Curaçao", "Ivory Coast": "Costa do Marfim",
    "Côte d'Ivoire": "Costa do Marfim", "Sweden": "Suécia", "Tunisia": "Tunísia",
    "Egypt": "Egito", "Iran": "Irã", "IR Iran": "Irã",
    "New Zealand": "Nova Zelândia", "Cape Verde": "Cabo Verde",
    "Cabo Verde": "Cabo Verde", "Saudi Arabia": "Arábia Saudita",
    "Iraq": "Iraque", "Algeria": "Argélia", "Austria": "Áustria",
    "Jordan": "Jordânia", "DR Congo": "RD Congo", "Congo DR": "RD Congo",
    "Uzbekistan": "Uzbequistão", "Ghana": "Gana", "Panama": "Panamá",
    "Haiti": "Haiti", "Scotland": "Escócia",
}


def _token() -> str | None:
    """Lê o token dos secrets do Streamlit ou da variável de ambiente."""
    try:
        if "FOOTBALL_DATA_TOKEN" in st.secrets:
            return st.secrets["FOOTBALL_DATA_TOKEN"]
    except Exception:
        pass
    return os.environ.get("FOOTBALL_DATA_TOKEN")


def api_disponivel() -> bool:
    """True se há token e a lib requests está instalada."""
    return bool(_token()) and requests is not None


def _nome(api_name: str) -> str:
    """Traduz o nome da seleção da API para o nosso padrão."""
    return MAPA_NOMES.get(api_name, api_name)


@st.cache_data(ttl=30, show_spinner=False)
def _get(endpoint: str):
    """GET na API com cache de 30s (respeita o limite do plano grátis)."""
    token = _token()
    if not token or requests is None:
        return None
    try:
        resp = requests.get(f"{API_BASE}/{endpoint}",
                            headers={"X-Auth-Token": token}, timeout=8)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def _gols(match: dict) -> tuple:
    """Extrai (gols_casa, gols_fora) do placar de tempo integral."""
    ft = match.get("score", {}).get("fullTime", {})
    return ft.get("home"), ft.get("away")


def placares_ao_vivo_api() -> dict:
    """Jogos em andamento: {(time_a, time_b): {placar, minuto}}."""
    data = _get(f"competitions/{COMPETICAO}/matches?status=LIVE,IN_PLAY,PAUSED")
    if not data:
        return {}
    out = {}
    for m in data.get("matches", []):
        a, b = _nome(m["homeTeam"]["name"]), _nome(m["awayTeam"]["name"])
        ga, gb = _gols(m)
        ga, gb = ga or 0, gb or 0
        minuto = f"{m['minute']}'" if m.get("minute") else "AO VIVO"
        out[(a, b)] = {"placar": f"{ga}x{gb}", "minuto": minuto}
    return out


def resultados_finalizados_api() -> dict:
    """Jogos encerrados: {(time_a, time_b): "GAxGB"} (placar de tempo normal)."""
    data = _get(f"competitions/{COMPETICAO}/matches?status=FINISHED")
    if not data:
        return {}
    out = {}
    for m in data.get("matches", []):
        ga, gb = _gols(m)
        if ga is None or gb is None:
            continue
        a, b = _nome(m["homeTeam"]["name"]), _nome(m["awayTeam"]["name"])
        out[(a, b)] = f"{ga}x{gb}"
    return out


@st.cache_data(ttl=300, show_spinner=False)
def artilheiros_api(limite: int = 20) -> pd.DataFrame:
    """Artilharia real do torneio (gols, assistências, jogos por jogador)."""
    data = _get(f"competitions/{COMPETICAO}/scorers?limit={limite}")
    if not data:
        return pd.DataFrame()
    linhas = []
    for s in data.get("scorers", []):
        linhas.append({
            "jogador": s["player"]["name"],
            "selecao": _nome(s["team"]["name"]),
            "gols": s.get("goals") or 0,
            "assistencias": s.get("assists") or 0,
            "jogos": s.get("playedMatches") or 0,
        })
    return pd.DataFrame(linhas)
