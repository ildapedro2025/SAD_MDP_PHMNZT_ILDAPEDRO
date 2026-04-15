# app.py
import streamlit as st
import random
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression
from io import BytesIO

# ---------- Configurações máximas ----------
MAX_LEITOS = 100
MAX_RECURSOS = 25
MAX_URGENCIA = 35

#---------- Ações possíveis ----------
acoes = ["admitir", "transferir", "abrir_leito", "reagendar"]

# ---------- Custom CSS Styling ----------
CUSTOM_CSS = """
<style>
    /* General Styling */
    :root {
        --primary-color: #0066cc;
        --success-color: #00aa00;
        --warning-color: #ff9900;
        --danger-color: #cc0000;
        --light-bg: #f8f9fa;
    }
    
    /* Card Styling - Enhanced */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 10px;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.2);
    }
    
    .metric-card h3 {
        margin: 0 0 10px 0;
        font-size: 14px;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-card .value {
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .metric-card .subtitle {
        font-size: 12px;
        opacity: 0.8;
    }
    
    /* Alert Styling */
    .alert-box {
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 4px solid;
    }
    
    .alert-success { border-color: #00aa00; background-color: #e8f5e9; }
    .alert-warning { border-color: #ff9900; background-color: #fff3e0; }
    .alert-error { border-color: #cc0000; background-color: #ffebee; }
    
    /* Button Styling */
    .action-button {
        border-radius: 8px;
        padding: 12px 20px;
        font-weight: 500;
        transition: all 0.3s ease;
        border: 2px solid;
        text-align: center;
        cursor: pointer;
    }
    
    /* Section Headers */
    .section-header {
        border-bottom: 3px solid #0066cc;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    
    /* Spacing */
    .spacer { height: 20px; }
    .spacer-lg { height: 40px; }
    
    /* Data Table */
    .dataframe { border-collapse: collapse; }
    .dataframe th { 
        background-color: #f0f2f5;
        font-weight: 600;
        border-bottom: 2px solid #0066cc;
    }
    
</style>
"""

# ---------- Função de Exportação para Excel ----------
def exportar_para_excel(df: pd.DataFrame) -> bytes:
    """Exporta dataframe para Excel em formato bytes"""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Histórico')
    buffer.seek(0)
    return buffer.getvalue()

# ---------- Funções UI Melhoradas ----------
def renderizar_cartao_metrica(titulo: str, valor: str, subtitulo: str, icone: str, cor: str):
    """Renderiza um card de métrica com estilo melhorado"""
    return f"""
    <div style="
        background: linear-gradient(135deg, {cor}dd 0%, {cor} 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <p style="margin: 0; opacity: 0.9; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">{titulo}</p>
                <p style="margin: 10px 0; font-size: 32px; font-weight: bold;">{valor}</p>
                <p style="margin: 0; opacity: 0.8; font-size: 12px;">{subtitulo}</p>
            </div>
            <div style="font-size: 40px; opacity: 0.7;">{icone}</div>
        </div>
    </div>
    """

def render_status_badge(status: str, value: str, max_val: str):
    """Renderiza um badge de status"""
    return f"<span style='background: #f0f2f5; padding: 2px 8px; border-radius: 12px; font-size: 12px;'>{status}: {value}/{max_val}</span>"

def to_excel(df: pd.DataFrame) -> bytes:
    """Converte DataFrame para bytes Excel"""
    output = pd.io.common.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Histórico')
        writer.save()
    return output.getvalue()

def probabilidades_transicao(estado, acao):
    o, r, u = estado
    outcomes = []
    if acao == "admitir" and o < MAX_LEITOS:
        outcomes.append(((o+1, r, max(0, min(MAX_URGENCIA, u))), 0.5))
        outcomes.append(((o+1, r, max(0, min(MAX_URGENCIA, u+1))), 0.3))
        outcomes.append(((o+1, r, max(0, min(MAX_URGENCIA, u-1))), 0.2))
    elif acao == "transferir" and o > 0:
        outcomes.append(((o-1, r, max(0, min(MAX_URGENCIA, u))), 0.6))
        outcomes.append(((o-1, r, max(0, min(MAX_URGENCIA, u+1))), 0.3))
        outcomes.append(((o-1, r, max(0, min(MAX_URGENCIA, u-1))), 0.1))
    elif acao == "abrir_leito" and r > 0:
        outcomes.append(((min(MAX_LEITOS, o+1), r-1, u), 1.0))
    elif acao == "reagendar":
        outcomes.append(((o, r, max(0, min(MAX_URGENCIA, u))), 0.4))
        outcomes.append(((o, r, max(0, min(MAX_URGENCIA, u+1))), 0.4))
        outcomes.append(((o, r, max(0, min(MAX_URGENCIA, u-1))), 0.2))
    return outcomes
# ---------- Função de Recompensa ----------
def recompensa(estado, acao, proximo_estado):
    o, r, u = proximo_estado
    eficiencia = o / MAX_LEITOS
    satisfacao = (MAX_URGENCIA - u) / MAX_URGENCIA
    custo_acao = 0.5 if acao in ["abrir_leito", "transferir"] else 0
    total = round(eficiencia + satisfacao - custo_acao, 2)
    return total, round(eficiencia,2), round(satisfacao,2), custo_acao

def valor_esperado(estado, acao):
    outcomes = probabilidades_transicao(estado, acao)
    Q = 0
    for s_prime, prob in outcomes:
        r, _, _, _ = recompensa(estado, acao, s_prime)
        Q += prob * r
    return round(Q,2)

# ---------- Configuração ----------
st.set_page_config(
    page_title="MDP Hospital Municipal do Nzeto",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Custom color function with better logic
def obter_cor_status(valor, valor_maximo, reverso=False):
    """
    Retorna cor baseada no valor relative
    reverso=True para métricas onde valores baixos são bons (urgência, custo)
    """
    if valor_maximo == 0:
        return "#00aa00", "✓"  # Verde com checkmark
    
    proporcao = valor / valor_maximo
    
    if not reverso:
        if proporcao >= 0.8:
            return "#cc0000", "●"  # Vermelho - crítico
        elif proporcao >= 0.5:
            return "#ff9900", "◐"  # Laranja - aviso
        else:
            return "#00aa00", "✓"  # Verde - ok
    else:
        if proporcao >= 0.7:
            return "#cc0000", "●"  # Vermelho para valores altos (ruim)
        elif proporcao >= 0.4:
            return "#ff9900", "◐"  # Laranja
        else:
            return "#00aa00", "✓"  # Verde para valores baixos (bom)

# ---------- Sessão ----------
if 'estado' not in st.session_state:
    st.session_state.estado = (0, MAX_RECURSOS, 0)
    st.session_state.historico = []
    st.session_state.configuracao_concluida = False
    st.session_state.dados_ml = []
    st.session_state.modelo_o = LinearRegression()
    st.session_state.modelo_r = LinearRegression()
    st.session_state.modelo_u = LinearRegression()

# ---------- Funções ML ----------
def treinar_modelo_ml():
    if len(st.session_state.dados_ml) > 5:
        df = pd.DataFrame(st.session_state.dados_ml,
                          columns=["o","r","u","acao","o_next","r_next","u_next"])
        X = df[["o","r","u","acao"]]
        st.session_state.modelo_o.fit(X, df["o_next"])
        st.session_state.modelo_r.fit(X, df["r_next"])
        st.session_state.modelo_u.fit(X, df["u_next"])

def prever_proximo_estado(estado, acao):
    if len(st.session_state.dados_ml) < 5:
        return None
    X = np.array([[estado[0], estado[1], estado[2], acoes.index(acao)]])
    o_pred = st.session_state.modelo_o.predict(X)[0]
    r_pred = st.session_state.modelo_r.predict(X)[0]
    u_pred = st.session_state.modelo_u.predict(X)[0]
    return (
        int(round(max(0, min(MAX_LEITOS, o_pred)))),
        int(round(max(0, min(MAX_RECURSOS, r_pred)))),
        int(round(max(0, min(MAX_URGENCIA, u_pred))))
    )

# ---------- Tela Inicial ----------
if not st.session_state.configuracao_concluida:
    # Create a nice header
    col_header = st.columns([1, 2, 1])
    with col_header[1]:
        st.markdown(
            """
            <div style='text-align: center; padding: 40px 0;'>
                <h1 style='color: #0066cc; margin-bottom: 10px;'>🏥 HOSPITAL MUNICIPAL DO NZETO</h1>
                <p style='color: #666; font-size: 16px;'>Simulação de Decisão sob Incerteza</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Configuration form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("⚙️ Informe os parâmetros iniciais")
        
        with st.form("config_form"):
            # Input fields with better labels
            col_a, col_b = st.columns(2)
            with col_a:
                leitos = st.slider(
                    "🛏️ Leitos Ocupados",
                    min_value=0,
                    max_value=MAX_LEITOS,
                    value=10,
                    help="Número atual de leitos ocupados"
                )
            
            with col_b:
                recursos = st.slider(
                    "📦 Recursos Disponíveis",
                    min_value=0,
                    max_value=MAX_RECURSOS,
                    value=MAX_RECURSOS,
                    help="Número de recursos hospitalares disponíveis"
                )
            
            urgencia = st.slider(
                "⚠️ Urgência Média",
                min_value=0,
                max_value=MAX_URGENCIA,
                value=5,
                help="Nível médio de urgência dos pacientes"
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                if st.form_submit_button(
                    "▶️ Iniciar Simulação",
                    use_container_width=True,
                    type="primary"
                ):
                    st.session_state.estado = (leitos, recursos, urgencia)
                    st.session_state.historico = []
                    st.session_state.dados_ml = []
                    st.session_state.configuracao_concluida = True
                    st.rerun()

# ---------- Dashboard ----------
else:
    estado = st.session_state.estado
    historico = st.session_state.historico

    # Header
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1 style='color: #0066cc; margin-bottom: 10px;'>🏥 Hospital MDP Dashboard</h1>
            <p style='color: #666;'>Decisão sob Incerteza e Processos de Decisão de Markov (MDP)</p>
            <p style='color: #999; font-size: 12px;'>Hospital Municipal do Nzeto</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------- Indicadores em Cards Melhorados --------
    ef_total, sat_total, _, custo_total = recompensa(estado, "admitir", estado)
    
    # Get color for each metric
    color_leitos, _ = obter_cor_status(estado[0], MAX_LEITOS)
    color_recursos, _ = obter_cor_status(estado[1], MAX_RECURSOS)
    color_urgencia, _ = obter_cor_status(estado[2], MAX_URGENCIA, reverso=True)
    color_exec, _ = obter_cor_status(ef_total, 1)
    color_sat, _ = obter_cor_status(sat_total, 1, reverso=True)
    color_cost, _ = obter_cor_status(custo_total, 1, reverso=True)

    # Display metrics in improved cards
    cols_metrics = st.columns(3)
    
    with cols_metrics[0]:
        st.markdown(
            renderizar_cartao_metrica(
                "Leitos Ocupados",
                f"{estado[0]}/{MAX_LEITOS}",
                f"{MAX_LEITOS - estado[0]} leitos livres",
                "🛏️",
                color_leitos
            ),
            unsafe_allow_html=True
        )
    
    with cols_metrics[1]:
        st.markdown(
            renderizar_cartao_metrica(
                "Recursos Disponíveis",
                f"{estado[1]}/{MAX_RECURSOS}",
                f"Utilizados: {MAX_RECURSOS - estado[1]}",
                "📦",
                color_recursos
            ),
            unsafe_allow_html=True
        )
    
    with cols_metrics[2]:
        st.markdown(
            renderizar_cartao_metrica(
                "Urgência Média",
                f"{estado[2]}/{MAX_URGENCIA}",
                "Nível de demanda",
                "⚠️",
                color_urgencia
            ),
            unsafe_allow_html=True
        )
    
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    cols_metrics_2 = st.columns(3)
    
    with cols_metrics_2[0]:
        st.markdown(
            renderizar_cartao_metrica(
                "Eficiência",
                f"{round(ef_total*100, 1)}%",
                "Taxa de ocupação",
                "⚡",
                color_exec
            ),
            unsafe_allow_html=True
        )
    
    with cols_metrics_2[1]:
        st.markdown(
            renderizar_cartao_metrica(
                "Satisfação",
                f"{round(sat_total*100, 1)}%",
                "Nível de satisfação",
                "😊",
                color_sat
            ),
            unsafe_allow_html=True
        )
    
    with cols_metrics_2[2]:
        st.markdown(
            renderizar_cartao_metrica(
                "Custo Total",
                f"{custo_total}",
                "Custo da última ação",
                "💰",
                color_cost
            ),
            unsafe_allow_html=True
        )
    
    st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)

    # -------- Sugestão Inteligente --------
    st.markdown("### 🤖 Sugestão Inteligente (Modelo Preditivo)")
    
    if len(st.session_state.dados_ml) > 5:
        predicted_rewards = {}
        for a in acoes:
            pred_state = prever_proximo_estado(estado, a)
            if pred_state:
                r_pred, _, _, _ = recompensa(estado, a, pred_state)
                predicted_rewards[a] = r_pred
        
        if predicted_rewards:
            best_action = max(predicted_rewards, key=predicted_rewards.get)
            
            col_sugest1, col_sugest2 = st.columns([2, 1])
            with col_sugest1:
                st.markdown(
                    f"""
                    <div style='background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                                border-radius: 12px; padding: 20px; color: white;
                                box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                        <h3 style='margin: 0 0 10px 0;'>✅ Ação Recomendada</h3>
                        <p style='margin: 0; font-size: 24px; font-weight: bold;'>{best_action.upper()}</p>
                        <p style='margin: 10px 0 0 0; opacity: 0.9; font-size: 12px;'>Recompensa esperada: {predicted_rewards[best_action]:.2f}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col_sugest2:
                st.markdown("**Projeção de Recompensas:**")
                for action, reward_val in sorted(predicted_rewards.items(), key=lambda x: x[1], reverse=True):
                    st.metric(action.capitalize(), f"{reward_val:.2f}")
    else:
        dias_aprendizado = 5 - len(st.session_state.dados_ml)
        st.info(f"📚 Modelo em aprendizado. Execute {dias_aprendizado} ações para ativá-lo.")
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)

    # -------- Ações Disponíveis --------
    st.markdown("### 🎯 Ações Disponíveis")
    
    action_icons = {
        "admitir": "➕",
        "transferir": "🚑",
        "abrir_leito": "🛏️",
        "reagendar": "📅"
    }
    
    action_descriptions = {
        "admitir": "Admitir novo paciente",
        "transferir": "Transferir paciente",
        "abrir_leito": "Abrir novo leito",
        "reagendar": "Reagendar procedimento"
    }
    
    cols_actions = st.columns(4)
    
    for col, a in zip(cols_actions, acoes):
        with col:
            # Check if action is available
            outcomes = probabilidades_transicao(estado, a)
            is_available = len(outcomes) > 0
            
            button_color = "#0066cc" if is_available else "#cccccc"
            button_text = f"{action_icons.get(a, '')} {a.capitalize()}"
            
            if st.button(
                button_text,
                key=f"btn_{a}",
                use_container_width=True,
                disabled=not is_available,
                type="primary" if is_available else "secondary"
            ):
                if outcomes:
                    states_list, probs_list = zip(*outcomes)
                    next_state = random.choices(states_list, weights=probs_list)[0]
                    prob_next = next(p for s,p in outcomes if s==next_state)
                    r_total, ef, sat, custo = recompensa(estado, a, next_state)
                    Q_val = valor_esperado(estado, a)

                    st.session_state.dados_ml.append([
                        estado[0],estado[1], estado[2],
                        acoes.index(a),
                        next_state[0], next_state[1], next_state[2]
                    ])

                    treinar_modelo_ml()

                    st.session_state.historico.append({
                        "Estado": estado,
                        "Ação": a,
                        "Próximo Estado": next_state,
                        "Recompensa": r_total,
                        "Q(s,a)": Q_val,
                        "Probabilidade": prob_next
                    })

                    st.session_state.estado = next_state
                    st.rerun()
            
            # Add description below button
            st.caption(action_descriptions.get(a, ""))

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Reset button
    col_reset1, col_reset2, col_reset3 = st.columns([3, 1, 1])
    with col_reset3:
        if st.button("🔄 Reiniciar", use_container_width=True):
            st.session_state.configuracao_concluida = False
            st.session_state.estado = (0, MAX_RECURSOS, 0)
            st.session_state.historico = []
            st.session_state.dados_ml = []
            st.rerun()
    
    st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)

    # -------- Histórico e Gráficos --------
    st.markdown("### 📊 Histórico e Análise")
    
    if len(historico) > 0:
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📋 Histórico Completo", "📈 Gráficos", "📑 Resumo"])
        
        with tab1:
            df_history = pd.DataFrame(historico)

            uploaded_file = st.file_uploader(
                "⏫ Importar histórico (CSV)",
                type=['csv'],
                key='upload_history'
            )
            if uploaded_file is not None:
                try:
                    df_uploaded = pd.read_csv(uploaded_file)
                    st.session_state.historico = df_uploaded.to_dict(orient='records')
                    st.success('✅ Histórico importado com sucesso.')
                    df_history = pd.DataFrame(st.session_state.historico)
                except Exception as e:
                    st.error(f'Erro ao importar CSV: {e}')

            # Export controls
            csv_data = df_history.to_csv(index=False, encoding='utf-8')
            json_data = df_history.to_json(orient='records', force_ascii=False)
            excel_data = exportar_para_excel(df_history)

            col_exp1, col_exp2, col_exp3, col_exp4 = st.columns([1,1,1,1])
            with col_exp1:
                st.download_button(
                    label='⬇ Exportar CSV',
                    data=csv_data,
                    file_name='mdp_history.csv',
                    mime='text/csv',
                    key='download_csv'
                )
            with col_exp2:
                st.download_button(
                    label='⬇ Exportar JSON',
                    data=json_data,
                    file_name='mdp_history.json',
                    mime='application/json',
                    key='download_json'
                )
            with col_exp3:
                st.download_button(
                    label='⬇ Exportar Excel',
                    data=excel_data,
                    file_name='mdp_history.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    key='download_excel'
                )
            with col_exp4:
                st.write(f'Total de registros: **{len(df_history)}**')

            # Format the dataframe for better display
            st.dataframe(
                df_history,
                use_container_width=True,
                height=400
            )
        
        with tab2:
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                fig_q = px.line(
                    pd.DataFrame(historico),
                    x=pd.DataFrame(historico).index+1,
                    y="Q(s,a)",
                    color="Ação",
                    markers=True,
                    title="📈 Evolução do Valor Esperado Q(s,a)",
                    labels={"index": "Iteração", "Q(s,a)": "Q(s,a)"}
                )
                fig_q.update_layout(
                    hovermode="x unified",
                    height=400,
                    showlegend=True
                )
                st.plotly_chart(fig_q, use_container_width=True)
            
            with col_g2:
                df_hist = pd.DataFrame(historico)
                action_counts = df_hist['Ação'].value_counts().reset_index()
                action_counts.columns = ['Ação', 'Quantidade']
                fig_actions = px.bar(
                    action_counts,
                    x='Ação',
                    y='Quantidade',
                    color='Ação',
                    title="📊 Ações Realizadas",
                    text='Quantidade'
                )
                fig_actions.update_traces(textposition='auto')
                fig_actions.update_layout(
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig_actions, use_container_width=True)
        
        with tab3:
            col_r1, col_r2, col_r3 = st.columns(3)
            
            with col_r1:
                st.metric(
                    "Total de Ações",
                    len(historico),
                    help="Número total de decisões tomadas"
                )
            
            with col_r2:
                avg_reward = pd.DataFrame(historico)["Recompensa"].mean()
                st.metric(
                    "Recompensa Média",
                    f"{avg_reward:.2f}",
                    help="Recompensa média por ação"
                )
            
            with col_r3:
                max_reward = pd.DataFrame(historico)["Recompensa"].max()
                st.metric(
                    "Melhor Recompensa",
                    f"{max_reward:.2f}",
                    help="Maior recompensa obtida"
                )
            
            st.markdown("---")
            
            # Statistics by action - melhorado em português
            st.subheader("📊 Estatísticas Detalhadas por Ação")
            df_hist = pd.DataFrame(historico)
            
            # Mapeamento de funções para português
            agg_mapping = {
                'count': 'Contagem',      # Número de ocorrências
                'mean': 'Média',          # Valor médio
                'std': 'Desvio Padrão',   # Desvio padrão
                'max': 'Máximo',          # Valor máximo
                'min': 'Mínimo'           # Valor mínimo
            }
            
            # Agrupamento com nomes em português
            stats_by_action = df_hist.groupby('Ação').agg(
                **{agg_mapping[func]: ('Recompensa', func) for func in ['count', 'mean', 'std', 'max', 'min']}
            ).round(3)
            
            stats_by_action.index.name = '🎯 Ação'
            
            # Exibir com melhor destaque
            st.dataframe(
                stats_by_action,
                use_container_width=True,
                height=300
            )
            
            # Adicionar resumo visual por ação
            st.markdown("**📌 Detalhamento por Ação:**")
            for action in df_hist['Ação'].unique():
                df_action = df_hist[df_hist['Ação'] == action]
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        f"🎯 {action.upper()}",
                        f"{len(df_action)}",
                        "vezes executada"
                    )
                
                with col2:
                    avg = df_action['Recompensa'].mean()
                    st.metric(
                        "Recompensa Média",
                        f"{avg:.3f}"
                    )
                
                with col3:
                    max_val = df_action['Recompensa'].max()
                    st.metric(
                        "Melhor",
                        f"{max_val:.3f}"
                    )
                
                with col4:
                    min_val = df_action['Recompensa'].min()
                    st.metric(
                        "Pior",
                        f"{min_val:.3f}"
                    )
    else:
        st.info("📭 Nenhuma ação realizada ainda. Clique em um botão de ação para começar!")