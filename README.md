# ⚽ Copa 2026 Analytics

Dashboard Streamlit que une ciência de dados de futebol e jornalismo esportivo
para a Copa do Mundo de 2026 — a primeira com 48 seleções.

## Funcionalidades

| Aba | Conteúdo |
|---|---|
| 🔴 Ao Vivo | Placar em tempo real dos jogos em andamento (scoreboard com cronômetro), encerrados do dia com acerto do modelo e próximos com palpite. Auto-refresh a cada 15s via `st.fragment` |
| 📊 Panorama Histórico | Evolução do aproveitamento (2006–2022), gols marcados x sofridos e fase alcançada por edição (Plotly interativo) |
| 🏃‍♂️ Desempenho de Atletas | Ranking de eficiência com barras de progresso e heatmap normalizado dos top 12 |
| 🔮 Simulador e Previsões | Confronto A x B via **Distribuição de Poisson** (probabilidades, xG, placares prováveis, matriz de placares, head-to-head) + Power Ranking de título |
| 🏆 Simulação do Torneio | **Monte Carlo da Copa 2026 com a tabela oficial**: 12 grupos reais do sorteio FIFA, melhores terceiros alocados por busca exata e chaveamento oficial (jogos 73–104) até a final no MetLife. Probabilidade de cada seleção alcançar cada fase + replay detalhado de uma Copa simulada |
| 🏛️ Museu das Copas | Acervo completo das 22 edições (1930–2022) em `dados_copas.py`: finais, sedes, artilheiros, eras do futebol (gols/jogo) e galeria de campeões. **Isolado do modelo preditivo** — história não contamina previsão |
| ✍️ Crônica do Especialista | Análise textual gerada a partir dos próprios dados do modelo, com dark horses e leitura tática |

## Modelo preditivo (resumo)

- **Gols esperados (λ):** `ataque_A × (defesa_B / defesa_média) × fator_forma` (forma recente escala ±15%).
- **Resultado:** matriz de Poisson com correção Dixon-Coles (ρ ajustável), agregada em vitória/empate/derrota; placar exibido é condicionado ao desfecho apontado.
- **Power Ranking:** softmax calibrado sobre `60% rating + 25% forma recente + 15% pedigree histórico em Copas`.

### Fatores contextuais por jogo

- **🏔️ Altitude:** sedes acima de 1.400m (Cidade do México, Guadalajara) penalizam em 6% o ataque de seleções não adaptadas (todas exceto México, Equador e Colômbia);
- **🥵 Calor:** sedes quentes sem teto/ar-condicionado penalizam seleções UEFA em 4% (Houston/Dallas/Atlanta têm teto — sem penalidade);
- **😴 Descanso:** ±2% por dia de diferença de descanso entre as equipes (máx. ±6%);
- **💤 Jogo morto:** na 3ª rodada, time já garantido (6 pts) joga com ataque x0.85 e concede x1.10 — tanto nos palpites quanto dentro do Monte Carlo;
- **🟨 Radar de cartões:** critério FIFA (2 amarelos = suspensão; zerados após as quartas). Suspensões cortam o ataque em até 20%, ponderado pela importância do jogador — editável direto no app;
- **🏟️ Anfitrião, ⭐ craque e 🌎 continental:** bônus ajustáveis na sidebar (em 11 Copas nas Américas, só uma teve campeão europeu — CONMEBOL ganha bônus cheio, CONCACAF metade);
- **⚔️ Matchup de estilos:** pedra-papel-tesoura tático — contra-ataque pune posse (+8%), bloco baixo neutraliza posse (-8%) e surpreende na transição (+5%);
- **🦓 Variância de zebra:** acima de 300 pontos de gap de rating, o favorito perde 3% de λ e o azarão ganha 6% (o "dia mágico" existe);
- **💥 Dia de gala (goleadas):** nos mesmos confrontos desiguais, em 12% dos jogos o favorito engrena (λ x1.4, azarão x0.85) — a mistura de distribuições cria a cauda gorda de goleadas que o Poisson puro subestima. A coluna "💥 Goleada" nos palpites mostra P(vitória por 3+);
- **📈 Elo com K crescente:** recalibração com K=32/40/48 por rodada — vitória com tudo em jogo informa mais que na estreia.

### Fatores exclusivos de mata-mata

- **🥅 Pedigree de pênaltis (0–100):** empates no jogo único são decididos 50% pela razão dos λ e 50% pelo histórico de shootouts (Argentina 90, Croácia 88, Alemanha 85 vs Japão 52...);
- **🎭 Síndrome de mata-mata:** fator de rendimento no jogo único (México 0.93 e a maldição das oitavas; Croácia 1.07);
- **⏳ Imposto das 8 partidas:** elencos com idade média > 29 anos perdem 4% de λ das quartas em diante.

## Como executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

O app abre em `http://localhost:8501`.

## Acompanhando a Copa em tempo real

### Placar ao vivo automático (API)

O app integra a **football-data.org** (plano gratuito) para placares ao vivo,
resultados finalizados e artilharia reais. É **opcional** — sem chave, o app
funciona no modo manual (abaixo).

1. Crie uma conta grátis em https://www.football-data.org/client/register
2. Copie seu token.
3. **No Streamlit Cloud:** App → Settings → **Secrets**, adicione:
   ```toml
   FOOTBALL_DATA_TOKEN = "seu_token_aqui"
   ```
   **Localmente:** crie `.streamlit/secrets.toml` com a mesma linha (esse
   arquivo é ignorado pelo git — nunca suba seu token).

Com a chave ativa, a aba **🔴 Ao Vivo** mostra "🟢 API conectada": jogos em
andamento, resultados encerrados e a artilharia da Copa entram sozinhos, e o
modelo recalibra automaticamente.

### Placar ao vivo manual (sem chave)

Durante uma partida, adicione o jogo ao dict `JOGOS_AO_VIVO` no `app.py`:

```python
JOGOS_AO_VIVO = {
    ("Brasil", "Marrocos"): {"placar": "1x0", "minuto": "52'", "evento": "Gol de Vinícius Jr"},
}
```

Ele aparece como scoreboard na aba **🔴 Ao Vivo** (atualiza a cada 15s). Quando
o jogo acabar, mova o placar final para `resultado` no calendário e remova a
entrada — o modelo recalibra sozinho. Para placar 100% automático, basta plugar
uma API (football-data.org, api-football) na função `buscar_placares_ao_vivo()`.

### Recalibração com resultados

O calendário real da fase de grupos (72 jogos) está em `carregar_calendario()`
no `app.py`. Conforme os jogos acontecem, preencha a coluna `resultado`
(ex.: troque `None` por `"2x0"`). Com isso, automaticamente:

1. **O modelo recalibra** — rating (Elo, K=40), forma recente (média móvel 85/15)
   e ataque/defesa (β=0.15, normalizado pela força do adversário) de cada seleção;
2. **A Simulação do Torneio trava os placares reais** — as probabilidades passam
   a refletir o torneio "daqui em diante", não mais o pré-Copa;
3. **Os palpites mostram ✅/❌** comparando a previsão do modelo com o resultado.

> **Nota:** os dados de histórico/jogadores são fictícios (mock), porém calibrados
> em padrões reais; os grupos, o calendário e o chaveamento são os oficiais da FIFA.
> Para produção, substitua as funções `carregar_*()` em `app.py` por conexões
> a APIs/bases reais — toda a camada de dados é isolada nessas funções.
