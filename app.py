import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import datetime

st.set_page_config(page_title="Pool 48 — Qualidade ANEC 73", layout="wide", page_icon="\U0001F6A2")

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
MOTOR_PATH = DATA_DIR / "motor.xlsx"

MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
MESES_EXT = {'Jan': 'Janeiro', 'Fev': 'Fevereiro', 'Mar': 'Março', 'Abr': 'Abril', 'Mai': 'Maio', 'Jun': 'Junho',
             'Jul': 'Julho', 'Ago': 'Agosto', 'Set': 'Setembro', 'Out': 'Outubro', 'Nov': 'Novembro', 'Dez': 'Dezembro'}

NAVY = "#21295C"
BLUE = "#065A82"
TEAL = "#1C7293"
TEAL_LIGHT = "#5DCAA5"
GOLD = "#F2C200"
ORANGE = "#E9870F"
PAGA = "#B3413A"
PAGA_LIGHT = "#F09595"

ASSETS_DIR = Path(__file__).parent / "assets"

def _b64(path):
    import base64
    try:
        return base64.b64encode(path.read_bytes()).decode()
    except Exception:
        return None

LOGO_ANEC_B64 = _b64(ASSETS_DIR / "logo_anec.png")
LOGO_TERMINAL_B64 = _b64(ASSETS_DIR / "logo_terminal.png")
BG_B64 = _b64(ASSETS_DIR / "background_faded.jpg")

def inject_global_style():
    bg_css = f'background-image: url("data:image/jpeg;base64,{BG_B64}");' if BG_B64 else ""
    st.markdown(
        f"""
        <style>
          .stApp {{
            {bg_css}
            background-size: cover;
            background-position: center top;
            background-attachment: fixed;
            border: 7px solid transparent;
            border-image: linear-gradient(135deg, {BLUE} 0%, {BLUE} 45%, {ORANGE} 55%, {ORANGE} 100%) 1;
          }}
          .block-container {{ padding-top: 2rem; }}
          [data-testid="stSidebar"] {{
            background: rgba(247,245,240,0.94);
            border-right: 3px solid {ORANGE};
          }}
          [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
          .tablewrap {{
            overflow-x:auto; background: rgba(255,255,255,0.62); border-radius:6px;
            padding: 6px 10px 2px 10px; margin-bottom: 14px;
          }}
          table.styled-table {{
            width:100%; border-collapse:collapse; font-family:'Source Sans Pro',sans-serif; font-size:13.5px;
          }}
          table.styled-table thead th {{
            text-align:left; font-weight:700; color:{NAVY}; border-bottom:2px solid {NAVY};
            padding:8px 10px; white-space:nowrap;
          }}
          table.styled-table tbody td {{
            padding:7px 10px; border-bottom:1px solid #E7E3D8; font-variant-numeric:tabular-nums;
            font-weight:500; color:#1A2027;
          }}
          table.styled-table thead th.num, table.styled-table tbody td.num {{ text-align:right; }}
          table.styled-table tbody tr:hover td {{ background: rgba(233,135,15,0.10); }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_table(df, right_align=None):
    right_align = set(right_align or [])
    if df is None or len(df) == 0:
        st.caption("Sem dados para exibir.")
        return
    thead = "".join(
        f'<th class="{"num" if c in right_align else ""}">{c}</th>' for c in df.columns
    )
    body_rows = []
    for _, row in df.iterrows():
        cells = "".join(
            f'<td class="{"num" if c in right_align else ""}">{row[c]}</td>' for c in df.columns
        )
        body_rows.append(f"<tr>{cells}</tr>")
    html = (
        '<div class="tablewrap"><table class="styled-table">'
        f'<thead><tr>{thead}</tr></thead><tbody>{"".join(body_rows)}</tbody>'
        '</table></div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def logos_html():
    imgs = []
    if LOGO_TERMINAL_B64:
        imgs.append(f'<img src="data:image/png;base64,{LOGO_TERMINAL_B64}" style="height:42px;background:#F4F1E8;padding:4px 8px;border-radius:4px;">')
    if LOGO_ANEC_B64:
        imgs.append(f'<img src="data:image/png;base64,{LOGO_ANEC_B64}" style="height:42px;background:#F4F1E8;padding:4px 8px;border-radius:4px;">')
    if not imgs:
        return ""
    return f'<div style="display:flex;gap:10px;align-items:center;">{"".join(imgs)}</div>'

inject_global_style()

# ----------------------------------------------------------------------------
# Autenticacao
# ----------------------------------------------------------------------------
def get_secret(key, default):
    try:
        return st.secrets[key]
    except Exception:
        return default

POOL_PASSWORD = get_secret("POOL_PASSWORD", "pool48")
ADMIN_PASSWORD = get_secret("ADMIN_PASSWORD", "admin48")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

def login_screen():
    st.markdown(
        f"""
        <div style="background:linear-gradient(100deg,{NAVY},{BLUE});padding:28px 32px;border-radius:8px;margin-bottom:28px;display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap;">
            <div>
                <p style="color:#C9D6DE;font-size:13px;margin:0;">Terminal XXXIX &middot; Pool 48</p>
                <h1 style="color:#F4F1E8;font-size:26px;font-weight:400;margin:4px 0 0 0;">Controle de Qualidade ANEC 73</h1>
            </div>
            {logos_html()}
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Acesso do pool")
        with st.form("login_form"):
            pwd = st.text_input("Senha de acesso", type="password")
            submitted = st.form_submit_button("Entrar")
            if submitted:
                if pwd == POOL_PASSWORD:
                    st.session_state.authenticated = True
                    st.rerun()
                elif pwd == ADMIN_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
    with col2:
        st.subheader("Sobre este boletim")
        st.caption(
            "Consulta consolidada do pool de qualidade ANEC 73 — proteina, umidade e fibra, "
            "com o desconto e o acerto financeiro entre os clientes. Fale com o controle de "
            "qualidade do terminal se nao tiver a senha de acesso."
        )

if not st.session_state.authenticated:
    login_screen()
    st.stop()

# ----------------------------------------------------------------------------
# Barra lateral: navegacao + area do administrador
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"<p style='color:{NAVY};font-weight:600;font-size:15px;'>Pool 48 — ANEC 73</p>", unsafe_allow_html=True)

    if st.session_state.is_admin:
        with st.expander("Area do administrador", expanded=not MOTOR_PATH.exists()):
            st.caption("Envie o motor.xlsx atualizado (ja recalculado) para publicar um novo periodo.")
            uploaded = st.file_uploader("Motor_Controle_Qualidade_ANEC73_Pool.xlsx", type=["xlsx"])
            if uploaded is not None:
                with open(MOTOR_PATH, "wb") as f:
                    f.write(uploaded.getbuffer())
                st.success("Arquivo atualizado. Recarregando...")
                st.cache_data.clear()
                st.rerun()
            if MOTOR_PATH.exists():
                mtime = datetime.datetime.fromtimestamp(MOTOR_PATH.stat().st_mtime)
                st.caption(f"Ultima atualizacao: {mtime.strftime('%d/%m/%Y %H:%M')}")

    if st.button("Sair"):
        st.session_state.authenticated = False
        st.session_state.is_admin = False
        st.rerun()

if not MOTOR_PATH.exists():
    st.info("Nenhum motor de calculo foi publicado ainda. Peça ao administrador para enviar o arquivo na área lateral.")
    st.stop()

# ----------------------------------------------------------------------------
# Carregamento dos dados (cache por horario de modificacao do arquivo)
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(path_str, mtime):
    resumo = pd.read_excel(path_str, sheet_name="Resumo_Cliente_Mes")
    desconto = pd.read_excel(path_str, sheet_name="Desconto_Cliente_Mes")
    acerto = pd.read_excel(path_str, sheet_name="Acerto_Detalhado")
    clientes = pd.read_excel(path_str, sheet_name="Clientes")["Cliente"].dropna().tolist()
    dados = pd.read_excel(path_str, sheet_name="DADOS")
    parametros = pd.read_excel(path_str, sheet_name="Parametros_ANEC73", header=2, nrows=3)
    precos = pd.read_excel(path_str, sheet_name="Parametros_ANEC73", header=12, nrows=12, usecols="A:B")
    return resumo, desconto, acerto, clientes, dados, parametros, precos

try:
    resumo, desconto, acerto, clientes, dados, parametros, precos = load_data(str(MOTOR_PATH), MOTOR_PATH.stat().st_mtime)
except Exception as e:
    st.error(f"Nao foi possivel ler o motor.xlsx: {e}")
    st.stop()

PADRAO_ANEC = {row["Parametro"]: row["Padrao ANEC73 (%)"] for _, row in parametros.iterrows()}

@st.cache_data
def build_weekly(dados_str_ignore, mtime):
    df = dados.copy()
    df["Data Inicial"] = pd.to_datetime(df["Data Inicial"])
    df["Data Final"] = pd.to_datetime(df["Data Final"])
    df["Semana"] = df["Data Inicial"].dt.strftime("%d/%m") + " a " + df["Data Final"].dt.strftime("%d/%m")
    df["Semana_ord"] = df["Data Inicial"]
    grp = df.groupby(["Semana", "Semana_ord"], as_index=False).apply(
        lambda g: pd.Series({
            "Volume (t)": g["Volume (t)"].sum(),
            "Proteina (%)": (g["Volume (t)"] * g["Proteina (%)"]).sum() / g["Volume (t)"].sum(),
            "Umidade (%)": (g["Volume (t)"] * g["Umidade (%)"]).sum() / g["Volume (t)"].sum(),
            "Fibra (%)": (g["Volume (t)"] * g["Fibra (%)"]).sum() / g["Volume (t)"].sum(),
        }), include_groups=False
    )
    return grp.sort_values("Semana_ord")

@st.cache_data
def build_weekly_by_client(dados_str_ignore, mtime):
    df = dados.copy()
    df["Data Inicial"] = pd.to_datetime(df["Data Inicial"])
    df["Data Final"] = pd.to_datetime(df["Data Final"])
    df["Semana"] = df["Data Inicial"].dt.strftime("%d/%m") + " a " + df["Data Final"].dt.strftime("%d/%m")
    grp = df.groupby(["Cliente", "Mes", "Semana", "Data Inicial"], as_index=False).apply(
        lambda g: pd.Series({
            "Volume (t)": g["Volume (t)"].sum(),
            "Proteina (%)": (g["Volume (t)"] * g["Proteina (%)"]).sum() / g["Volume (t)"].sum(),
            "Umidade (%)": (g["Volume (t)"] * g["Umidade (%)"]).sum() / g["Volume (t)"].sum(),
            "Fibra (%)": (g["Volume (t)"] * g["Fibra (%)"]).sum() / g["Volume (t)"].sum(),
        }), include_groups=False
    )
    return grp.sort_values(["Data Inicial", "Cliente"])

semanal = build_weekly(str(MOTOR_PATH), MOTOR_PATH.stat().st_mtime)
semanal_cli = build_weekly_by_client(str(MOTOR_PATH), MOTOR_PATH.stat().st_mtime)

clientes = sorted(clientes)

def fmt_money(v):
    if v is None or pd.isna(v):
        return "-"
    if abs(v) < 0.5:
        return "US$ 0"
    sign = "-" if v < 0 else ""
    return f"{sign}US$ {abs(v):,.0f}".replace(",", ".")

def fmt_vol(v):
    if v is None or pd.isna(v):
        return "-"
    return f"{v:,.0f} t".replace(",", ".")

def fmt_pct(v):
    if v is None or pd.isna(v):
        return "-"
    return f"{v:.2f}%".replace(".", ",")

def excel_download_button(sheets, filename, label="Baixar em Excel", key=None):
    import io
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    st.download_button(
        label=f"\U0001F4E5 {label}", data=buffer.getvalue(), file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=key,
    )

def bar_saldo_mensal(meses, valores, height=220):
    colors = [TEAL_LIGHT if v >= 0 else PAGA_LIGHT for v in valores]
    fig = go.Figure(go.Bar(x=meses, y=valores, marker_color=colors))
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(showgrid=False, zeroline=True, zerolinecolor="#D8D3C7", visible=False),
        xaxis=dict(showgrid=False),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", color="#1A2027"),
    )
    return fig

def hbar_ranking(labels, valores, height=None):
    colors = [TEAL_LIGHT if v >= 0 else PAGA_LIGHT for v in valores]
    order = sorted(range(len(valores)), key=lambda i: valores[i])
    labels_s = [labels[i] for i in order]
    valores_s = [valores[i] for i in order]
    colors_s = [colors[i] for i in order]
    fig = go.Figure(go.Bar(
        x=valores_s, y=labels_s, orientation="h", marker_color=colors_s,
        text=[fmt_money(v) for v in valores_s], textposition="outside",
        textfont=dict(size=11),
        cliponaxis=False,
    ))
    maxabs = max([abs(v) for v in valores_s], default=1) or 1
    fig.update_layout(
        height=height or (28 * len(labels) + 60),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=True, zerolinecolor="#D8D3C7", visible=False,
                    range=[-maxabs * 2.1, maxabs * 2.1]),
        yaxis=dict(showgrid=False, automargin=True),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", color="#1A2027"),
    )
    return fig

def line_semanal(semanas, valores, padrao, height=240):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=semanas, y=valores, mode="lines+markers",
        line=dict(color=BLUE, width=2), marker=dict(size=6, color=BLUE),
        name="Media do pool",
    ))
    if padrao is not None:
        fig.add_trace(go.Scatter(
            x=semanas, y=[padrao] * len(semanas), mode="lines",
            line=dict(color=PAGA, width=1.3, dash="dash"),
            name="Padrao ANEC 73",
        ))
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(showgrid=True, gridcolor="#E7E3D8", ticksuffix="%"),
        xaxis=dict(showgrid=False),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", color="#1A2027"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    return fig

# ----------------------------------------------------------------------------
# Cabecalho
# ----------------------------------------------------------------------------
gen_date = datetime.datetime.fromtimestamp(MOTOR_PATH.stat().st_mtime).strftime("%d/%m/%Y")
st.markdown(
    f"""
    <div style="background:linear-gradient(100deg,{NAVY},{BLUE});padding:22px 28px;border-radius:8px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap;">
        <div>
            <p style="color:#C9D6DE;font-size:13px;margin:0;">Terminal XXXIX &middot; Pool 48 &middot; Controle de Qualidade ANEC 73</p>
            <h1 style="color:#F4F1E8;font-size:24px;font-weight:400;margin:4px 0 0 0;">Boletim Consolidado do Pool</h1>
            <p style="color:#C9D6DE;font-size:12.5px;margin:8px 0 0 0;">Dados publicados em {gen_date} &middot; {len(clientes)} clientes no pool</p>
        </div>
        {logos_html()}
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Navegacao
# ----------------------------------------------------------------------------
clientes_ativos = sorted(resumo[resumo["Volume (t)"] > 0]["Cliente"].unique().tolist())
n_sem_embarque = len(clientes) - len(clientes_ativos)

paginas = ["Visao geral do pool", "Qualidade semanal do pool", "Preco do farelo por mes"] + clientes_ativos
escolha = st.sidebar.radio("Consultar", paginas, label_visibility="collapsed")
if n_sem_embarque > 0:
    st.sidebar.caption(f"{n_sem_embarque} cliente(s) do pool ainda sem embarque neste periodo (oculto).")

def resumo_cliente(cliente):
    df = resumo[resumo["Cliente"] == cliente]
    df = df[df["Volume (t)"] > 0]
    return df

# ----------------------------------------------------------------------------
# Pagina: visao geral
# ----------------------------------------------------------------------------
if escolha == "Visao geral do pool":
    ativos = resumo[resumo["Volume (t)"] > 0]
    volume_total = ativos["Volume (t)"].sum()
    n_ativos = ativos["Cliente"].nunique()

    saldo_por_cliente = ativos.groupby("Cliente")["Saldo Total (US$)"].sum().sort_values(ascending=False)

    c1, c2, c3 = st.columns(3)
    c1.metric("Volume do pool", fmt_vol(volume_total))
    c2.metric("Clientes ativos", f"{n_ativos} de {len(clientes)}")
    c3.metric("Saldo em transito", fmt_money(saldo_por_cliente.sum()))

    st.markdown("#### Ranking de saldo por cliente")
    st.plotly_chart(hbar_ranking(saldo_por_cliente.index.tolist(), saldo_por_cliente.values.tolist()),
                     width='stretch', config={"displayModeBar": False})

    st.markdown("#### Todos os clientes")
    tabela_raw = pd.DataFrame({
        "Cliente": saldo_por_cliente.index,
        "Volume (t)": [ativos[ativos["Cliente"] == c]["Volume (t)"].sum() if c in ativos["Cliente"].values else 0 for c in saldo_por_cliente.index],
        "Saldo total (US$)": saldo_por_cliente.values,
        "Situacao": ["Recebe" if v > 0 else ("Paga" if v < 0 else "Sem embarque") for v in saldo_por_cliente.values],
    }).sort_values("Saldo total (US$)", ascending=False)
    tabela = tabela_raw.copy()
    tabela["Volume (t)"] = tabela["Volume (t)"].apply(fmt_vol)
    tabela["Saldo total (US$)"] = tabela["Saldo total (US$)"].apply(fmt_money)
    tabela = tabela.rename(columns={"Volume (t)": "Volume", "Saldo total (US$)": "Saldo total"})
    render_table(tabela, right_align=["Volume", "Saldo total"])
    excel_download_button({"Visao geral do pool": tabela_raw}, "visao_geral_pool.xlsx", key="dl_overview")

# ----------------------------------------------------------------------------
# Pagina: qualidade semanal do pool
# ----------------------------------------------------------------------------
elif escolha == "Qualidade semanal do pool":
    st.markdown("#### Qualidade apurada semana a semana (media ponderada do pool)")
    st.caption(
        "Cada semana corresponde a uma janela de coleta (Data Inicial a Data Final) registrada na aba DADOS, "
        "igual a planilha original. Media ponderada pelo volume de todos os clientes do pool naquela semana."
    )

    for par, col, padrao in [("Proteina", "Proteina (%)", PADRAO_ANEC.get("Proteina")),
                              ("Umidade", "Umidade (%)", PADRAO_ANEC.get("Umidade")),
                              ("Fibra", "Fibra (%)", PADRAO_ANEC.get("Fibra"))]:
        st.markdown(f"##### {par}")
        st.plotly_chart(
            line_semanal(semanal["Semana"].tolist(), semanal[col].tolist(), padrao),
            width='stretch', config={"displayModeBar": False},
        )

    st.markdown("#### Tabela semanal (pool)")
    tab_sem_raw = semanal[["Semana", "Volume (t)", "Proteina (%)", "Umidade (%)", "Fibra (%)"]].copy()
    tab_sem = tab_sem_raw.copy()
    tab_sem["Volume (t)"] = tab_sem["Volume (t)"].apply(fmt_vol)
    for c in ["Proteina (%)", "Umidade (%)", "Fibra (%)"]:
        tab_sem[c] = tab_sem[c].apply(fmt_pct)
    render_table(tab_sem, right_align=["Volume (t)", "Proteina (%)", "Umidade (%)", "Fibra (%)"])
    excel_download_button({"Semanal Pool": tab_sem_raw}, "qualidade_semanal_pool.xlsx", key="dl_semanal_pool")

    st.markdown("#### Qualidade entregue por cliente")
    st.caption("Filtre por cliente, mes e/ou semana para ver o que cada um entregou naquele periodo.")

    clientes_opts = sorted(semanal_cli["Cliente"].unique().tolist())
    meses_opts = [m for m in MESES if m in semanal_cli["Mes"].unique()]
    semanas_opts = semanal_cli.sort_values("Data Inicial")["Semana"].unique().tolist()

    fc1, fc2, fc3 = st.columns(3)
    sel_clientes = fc1.multiselect("Cliente", clientes_opts, default=clientes_opts)
    sel_meses_ext = fc2.multiselect("Mes", [MESES_EXT[m] for m in meses_opts], default=[MESES_EXT[m] for m in meses_opts])
    sel_semanas = fc3.multiselect("Semana", semanas_opts, default=semanas_opts)

    mes_rev = {v: k for k, v in MESES_EXT.items()}
    sel_meses = [mes_rev[m] for m in sel_meses_ext]

    filtrado = semanal_cli[
        semanal_cli["Cliente"].isin(sel_clientes)
        & semanal_cli["Mes"].isin(sel_meses)
        & semanal_cli["Semana"].isin(sel_semanas)
    ].copy()

    if len(filtrado):
        filtrado["Mes"] = filtrado["Mes"].map(MESES_EXT)
        show_raw = filtrado[["Cliente", "Mes", "Semana", "Volume (t)", "Proteina (%)", "Umidade (%)", "Fibra (%)"]].copy()
        show = show_raw.copy()
        show["Volume (t)"] = show["Volume (t)"].apply(fmt_vol)
        for c in ["Proteina (%)", "Umidade (%)", "Fibra (%)"]:
            show[c] = show[c].apply(fmt_pct)
        render_table(show, right_align=["Volume (t)", "Proteina (%)", "Umidade (%)", "Fibra (%)"])
        excel_download_button({"Qualidade por cliente": show_raw}, "qualidade_semanal_por_cliente.xlsx", key="dl_semanal_cliente")
    else:
        st.caption("Nenhum resultado para os filtros selecionados.")

# ----------------------------------------------------------------------------
# Pagina: preco do farelo
# ----------------------------------------------------------------------------
elif escolha == "Preco do farelo por mes":
    st.markdown("#### Preco USD/t do farelo por mes")
    st.caption("Preco de referencia usado no calculo do valor do desconto (aba Parametros_ANEC73 do motor).")

    precos_show = precos.copy()
    precos_show = precos_show[precos_show["Mes"].isin(MESES)]
    precos_show["MesExt"] = precos_show["Mes"].map(MESES_EXT)

    fig = go.Figure(go.Bar(
        x=precos_show["MesExt"], y=precos_show["Preco USD"],
        marker_color=BLUE, text=[f"${v:,.0f}" for v in precos_show["Preco USD"]], textposition="outside",
    ))
    fig.update_layout(
        height=280, margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(showgrid=True, gridcolor="#E7E3D8", tickprefix="$"),
        xaxis=dict(showgrid=False),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", color="#1A2027"),
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

    tab_preco = precos_show[["MesExt", "Preco USD"]].rename(columns={"MesExt": "Mes"})
    tab_preco_raw = tab_preco.copy()
    tab_preco["Preco USD"] = tab_preco["Preco USD"].apply(lambda v: f"US$ {v:,.0f}".replace(",", "."))
    render_table(tab_preco, right_align=["Preco USD"])
    excel_download_button({"Preco Farelo": tab_preco_raw}, "preco_farelo_mensal.xlsx", key="dl_preco")

# ----------------------------------------------------------------------------
# Pagina: cliente
# ----------------------------------------------------------------------------
else:
    cliente = escolha
    df_cli = resumo_cliente(cliente)
    total_saldo = df_cli["Saldo Total (US$)"].sum()
    total_vol = df_cli["Volume (t)"].sum()
    situacao = "a receber" if total_saldo > 0 else ("a pagar" if total_saldo < 0 else "neutro")

    c1, c2 = st.columns([1, 2])
    c1.metric(f"Saldo do periodo ({situacao})", fmt_money(total_saldo))
    c2.metric("Volume acumulado", fmt_vol(total_vol))

    tab_cons, tab_prot, tab_umi, tab_fib = st.tabs(["Consolidado", "Proteina", "Umidade", "Fibra"])

    with tab_cons:
        st.markdown("##### Evolucao mensal do saldo")
        meses_ord = [m for m in MESES if m in df_cli["Mes"].values]
        valores = [df_cli[df_cli["Mes"] == m]["Saldo Total (US$)"].sum() for m in meses_ord]
        st.plotly_chart(bar_saldo_mensal(meses_ord, valores), width='stretch', config={"displayModeBar": False})

        st.markdown("##### Resultado de qualidade por parametro")
        desc_cli = desconto[(desconto["Cliente"] == cliente) & (desconto["Volume (t)"] > 0)]
        pivot_rows = []
        for m in meses_ord:
            row = {"Mes": MESES_EXT[m]}
            for par in ["Proteina", "Umidade", "Fibra"]:
                sub = desc_cli[(desc_cli["Mes"] == m) & (desc_cli["Parametro"] == par)]
                if len(sub):
                    row[f"{par} - Resultado"] = fmt_pct(sub["Resultado (%)"].iloc[0])
                    row[f"{par} - Padrao"] = fmt_pct(sub["Padrao ANEC73 (%)"].iloc[0])
                    row[f"{par} - Pool"] = fmt_pct(sub["Media Pool (%)"].iloc[0])
                else:
                    row[f"{par} - Resultado"] = row[f"{par} - Padrao"] = row[f"{par} - Pool"] = "-"
            pivot_rows.append(row)
        render_table(pd.DataFrame(pivot_rows), right_align=[c for c in pd.DataFrame(pivot_rows).columns if c != "Mes"])

        st.markdown("##### Detalhamento do acerto financeiro")
        det_raw = df_cli[["Mes", "Volume (t)", "Saldo Proteina (US$)", "Saldo Umidade (US$)", "Saldo Fibra (US$)",
                           "Saldo Total (US$)", "Situacao"]].copy()
        det_raw["Mes"] = det_raw["Mes"].map(MESES_EXT)
        det = det_raw.copy()
        det["Volume (t)"] = det["Volume (t)"].apply(fmt_vol)
        for c in ["Saldo Proteina (US$)", "Saldo Umidade (US$)", "Saldo Fibra (US$)", "Saldo Total (US$)"]:
            det[c] = det[c].apply(fmt_money)
        render_table(det, right_align=["Volume (t)", "Saldo Proteina (US$)", "Saldo Umidade (US$)", "Saldo Fibra (US$)", "Saldo Total (US$)"])

    def aba_parametro(par, saldo_col):
        st.markdown(f"##### Saldo de {par.lower()} no periodo")
        meses_ord = [m for m in MESES if m in df_cli["Mes"].values]
        valores = [df_cli[df_cli["Mes"] == m][saldo_col].sum() for m in meses_ord]
        st.metric("Total no periodo", fmt_money(sum(valores)))
        st.plotly_chart(bar_saldo_mensal(meses_ord, valores), width='stretch', config={"displayModeBar": False})

        desc_cli = desconto[(desconto["Cliente"] == cliente) & (desconto["Volume (t)"] > 0) & (desconto["Parametro"] == par)]
        rows = []
        for m in meses_ord:
            sub = desc_cli[desc_cli["Mes"] == m]
            saldo_m = df_cli[df_cli["Mes"] == m][saldo_col].sum()
            if len(sub):
                rows.append({
                    "Mes": MESES_EXT[m],
                    "Volume": fmt_vol(sub["Volume (t)"].iloc[0]),
                    "Resultado": fmt_pct(sub["Resultado (%)"].iloc[0]),
                    "Padrao": fmt_pct(sub["Padrao ANEC73 (%)"].iloc[0]),
                    "Pool": fmt_pct(sub["Media Pool (%)"].iloc[0]),
                    "Saldo": fmt_money(saldo_m),
                })
        render_table(pd.DataFrame(rows), right_align=["Volume", "Resultado", "Padrao", "Pool", "Saldo"])

    with tab_prot:
        aba_parametro("Proteina", "Saldo Proteina (US$)")
    with tab_umi:
        aba_parametro("Umidade", "Saldo Umidade (US$)")
    with tab_fib:
        aba_parametro("Fibra", "Saldo Fibra (US$)")

    st.markdown("##### Acerto com outros clientes")
    ac_cli = acerto[(acerto["Cliente"] == cliente) & (acerto["Volume (t)"] > 0)]
    ac_raw = None
    if len(ac_cli):
        ac_raw = ac_cli[["Mes", "Parametro", "Volume (t)", "Valor Desconto (US$)", "Credito (US$)", "Saldo do cliente (US$)"]].copy()
        ac_raw["Mes"] = ac_raw["Mes"].map(MESES_EXT)
        ac_show = ac_raw.copy()
        ac_show["Volume (t)"] = ac_show["Volume (t)"].apply(fmt_vol)
        for c in ["Valor Desconto (US$)", "Credito (US$)", "Saldo do cliente (US$)"]:
            ac_show[c] = ac_show[c].apply(fmt_money)
        render_table(ac_show, right_align=["Volume (t)", "Valor Desconto (US$)", "Credito (US$)", "Saldo do cliente (US$)"])
    else:
        st.caption("Sem embarques no periodo.")

    qualidade_raw = desconto[(desconto["Cliente"] == cliente) & (desconto["Volume (t)"] > 0)][
        ["Mes", "Parametro", "Volume (t)", "Resultado (%)", "Padrao ANEC73 (%)", "Media Pool (%)"]
    ].copy()
    qualidade_raw["Mes"] = qualidade_raw["Mes"].map(MESES_EXT)

    export_sheets = {"Detalhamento": det_raw, "Qualidade por parametro": qualidade_raw}
    if ac_raw is not None:
        export_sheets["Acerto com outros"] = ac_raw
    excel_download_button(export_sheets, f"boletim_{cliente}.xlsx", key="dl_cliente")

st.caption(
    "Boletim informativo, calculado a partir dos embarques registrados no Terminal XXXIX. "
    "Valores sujeitos a conciliacao final do fechamento mensal do pool. Padrao de referencia: ANEC 73."
)
