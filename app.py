"""
Projex — Sistema de Controle de Projetos
Conversão completa para Streamlit com todas as funcionalidades do HTML original.
"""

import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime, timedelta
import base64
import io

# ─────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────
GAS_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbwVlPv_dhreFVkbSSTePo7dqAxVbVD_ep8bFeLCsR_Spioko7xACyfURsZRAguWCYNe/exec"
)

st.set_page_config(
    page_title="Projex",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CSS — Design refinado, profissional
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display:ital@0;1&display=swap');

:root {
  --bg:       #F4F6FB;
  --surface:  #FFFFFF;
  --surf2:    #EFF2F8;
  --border:   #DDE2EF;
  --primary:  #1B3A5C;
  --plight:   #2657A0;
  --accent:   #E8A020;
  --text:     #1A2233;
  --text2:    #566070;
  --text3:    #8E98A8;
  --danger:   #D94545;
  --dangbg:   #FDF0F0;
  --success:  #1E8A5A;
  --succbg:   #EBF8F2;
  --warning:  #C07A10;
  --warnbg:   #FEF5E7;
  --infobg:   #EBF1FB;
  --r-sm: 8px; --r-md: 12px; --r-lg: 18px;
  --sh-sm: 0 1px 3px rgba(27,58,92,.07),0 1px 2px rgba(27,58,92,.04);
  --sh-md: 0 4px 16px rgba(27,58,92,.10),0 1px 4px rgba(27,58,92,.06);
  --sh-lg: 0 8px 32px rgba(27,58,92,.13),0 2px 8px rgba(27,58,92,.07);
  --tr: .18s cubic-bezier(.4,0,.2,1);
}

html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--text);}

/* ── RESET Streamlit ── */
.block-container{padding:0!important;max-width:100%!important;}
#MainMenu,footer,header{visibility:hidden;}
section[data-testid="stSidebar"]{display:none;}
.stApp{background:var(--bg);}
div[data-testid="stToolbar"]{display:none;}

/* ── TOPBAR ── */
.topbar{
  background:linear-gradient(90deg,#0f2240 0%,#1B3A5C 50%,#2657A0 100%);
  color:#fff;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 28px;height:58px;
  box-shadow:0 2px 16px rgba(15,34,64,.25);
  position:sticky;top:0;z-index:200;
}
.topbar-brand{display:flex;align-items:center;gap:12px;}
.topbar-icon{font-size:22px;line-height:1;}
.topbar-name{font-family:'DM Serif Display',serif;font-size:20px;letter-spacing:-.3px;color:#fff;opacity:.96;}
.topbar-right{display:flex;align-items:center;gap:16px;}
.topbar-user{font-size:12.5px;color:rgba(255,255,255,.72);font-weight:500;
  background:rgba(255,255,255,.1);border-radius:99px;padding:5px 14px;border:1px solid rgba(255,255,255,.15);}

/* ── NAVBAR ── */
.navbar{
  background:var(--surface);
  border-bottom:1.5px solid var(--border);
  display:flex;align-items:center;gap:2px;
  padding:0 20px;
  position:sticky;top:58px;z-index:150;
  box-shadow:var(--sh-sm);
  overflow-x:auto;
}
.nav-tab{
  padding:15px 18px;
  background:none;border:none;border-bottom:2.5px solid transparent;
  color:var(--text2);font-family:'DM Sans',sans-serif;font-size:13px;font-weight:500;
  cursor:pointer;white-space:nowrap;transition:color var(--tr),border-color var(--tr);
  text-decoration:none;display:inline-block;
}
.nav-tab:hover{color:var(--primary);}
.nav-tab.active{color:var(--primary);border-bottom-color:var(--accent);font-weight:600;}
.nav-tab.highlight{color:var(--plight);font-weight:600;}

/* ── CONTEÚDO ── */
.main-pad{padding:28px 32px;max-width:1440px;margin:0 auto;}
.page-title{font-family:'DM Serif Display',serif;font-size:26px;color:var(--primary);
  margin-bottom:22px;letter-spacing:-.4px;display:flex;align-items:center;gap:10px;}

/* ── CARDS DE PROJETO ── */
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px;margin-top:4px;}
.proj-card{
  background:var(--surface);border:1.5px solid var(--border);border-radius:var(--r-md);
  padding:20px 22px;cursor:pointer;transition:box-shadow var(--tr),transform var(--tr),border-color var(--tr);
  position:relative;overflow:hidden;
}
.proj-card::before{
  content:'';position:absolute;left:0;top:0;bottom:0;width:4px;
  background:linear-gradient(180deg,var(--plight),var(--accent));
  opacity:0;transition:opacity var(--tr);border-radius:4px 0 0 4px;
}
.proj-card:hover{box-shadow:var(--sh-md);transform:translateY(-2px);border-color:#c0cce0;}
.proj-card:hover::before{opacity:1;}
.proj-card h3{font-size:15px;font-weight:600;color:var(--primary);margin-bottom:8px;line-height:1.35;}
.proj-card .meta{font-size:12.5px;color:var(--text2);margin:2px 0;}
.proj-card .meta strong{color:var(--text);font-weight:600;}
.proj-card .durante{font-size:12px;color:var(--text3);margin:7px 0 3px;}
.prog-wrap{background:var(--surf2);border-radius:99px;height:6px;margin:10px 0 4px;overflow:hidden;}
.prog-fill{height:6px;border-radius:99px;transition:width .6s cubic-bezier(.4,0,.2,1);background:var(--success);}
.prog-fill.warn{background:var(--accent);}
.prog-fill.danger{background:var(--danger);}
.card-footer{display:flex;align-items:center;justify-content:space-between;margin-top:4px;}
.card-perc{font-size:11.5px;color:var(--text3);font-weight:500;}

/* ── BADGES ── */
.badge{display:inline-flex;align-items:center;gap:4px;padding:2px 10px;border-radius:99px;
  font-size:11px;font-weight:600;letter-spacing:.2px;}
.badge-atraso{background:var(--dangbg);color:var(--danger);}
.badge-prazo{background:var(--infobg);color:var(--plight);}
.badge-conc{background:var(--succbg);color:var(--success);}
.badge-nao{background:var(--surf2);color:var(--text2);}
.badge-and{background:var(--infobg);color:var(--plight);}

/* ── FILTROS ── */
.filter-bar{
  background:var(--surface);border:1.5px solid var(--border);border-radius:var(--r-md);
  padding:16px 20px;margin-bottom:20px;box-shadow:var(--sh-sm);
  display:flex;gap:14px;flex-wrap:wrap;align-items:flex-end;
}
.filter-bar label{font-size:11px;font-weight:700;color:var(--text2);
  text-transform:uppercase;letter-spacing:.5px;display:flex;flex-direction:column;gap:5px;}
.filter-bar select,.filter-bar input{
  padding:8px 12px;border:1.5px solid var(--border);border-radius:var(--r-sm);
  font-family:'DM Sans',sans-serif;font-size:13px;color:var(--text);
  background:var(--bg);outline:none;transition:border-color var(--tr);min-width:140px;
}
.filter-bar select:focus,.filter-bar input:focus{border-color:var(--plight);}

/* ── TABELA ── */
.tbl-wrap{background:var(--surface);border:1.5px solid var(--border);border-radius:var(--r-md);
  overflow:hidden;box-shadow:var(--sh-sm);overflow-x:auto;}
table{width:100%;border-collapse:collapse;font-size:13px;}
thead th{background:var(--primary);color:#fff;padding:11px 14px;text-align:left;
  font-size:12px;font-weight:600;letter-spacing:.3px;white-space:nowrap;cursor:pointer;}
thead th:hover{background:var(--plight);}
tbody tr{border-bottom:1px solid var(--border);transition:background var(--tr);}
tbody tr:last-child{border-bottom:none;}
tbody tr:hover{background:var(--surf2);}
tbody td{padding:10px 14px;color:var(--text);vertical-align:middle;}
.sort-icon{margin-left:4px;font-size:9px;opacity:.7;}

/* ── KANBAN ── */
.kanban-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:4px;}
.kanban-col{background:var(--surf2);border-radius:var(--r-md);padding:14px;
  border:1.5px solid var(--border);min-height:200px;}
.kanban-header{font-size:11.5px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;
  padding:6px 12px;border-radius:var(--r-sm);margin-bottom:12px;
  display:flex;align-items:center;justify-content:space-between;}
.kh-nao{background:#EEF0F7;color:var(--text2);}
.kh-and{background:var(--infobg);color:var(--plight);}
.kh-conc{background:var(--succbg);color:var(--success);}
.k-count{background:rgba(255,255,255,.75);border-radius:99px;padding:1px 8px;font-size:11px;}
.kanban-card{background:var(--surface);border-radius:var(--r-sm);padding:12px 14px;
  margin-bottom:8px;border:1.5px solid var(--border);border-left:3.5px solid var(--border);
  box-shadow:var(--sh-sm);transition:box-shadow var(--tr),transform var(--tr);}
.kanban-card:hover{box-shadow:var(--sh-md);transform:translateY(-1px);}
.kanban-card.atrasada{border-left-color:var(--danger);}
.kanban-card.no-prazo{border-left-color:var(--success);}
.kanban-card strong{font-size:13px;color:var(--text);line-height:1.4;display:block;margin-bottom:6px;}
.kanban-card .kc-meta{font-size:11.5px;color:var(--text3);margin-bottom:4px;}

/* ── FORMULÁRIOS ── */
.form-surface{background:var(--surface);border:1.5px solid var(--border);border-radius:var(--r-md);
  padding:24px 28px;max-width:640px;box-shadow:var(--sh-sm);margin-bottom:24px;}
.form-title{font-family:'DM Serif Display',serif;font-size:19px;color:var(--primary);margin-bottom:20px;}

/* ── DASHBOARD CARDS ── */
.dash-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:16px;margin-bottom:28px;}
.dash-card{border-radius:var(--r-md);padding:22px 20px;position:relative;overflow:hidden;}
.dash-card::after{content:'';position:absolute;right:-16px;bottom:-16px;
  width:72px;height:72px;border-radius:50%;background:rgba(255,255,255,.12);}
.dash-card .dc-num{font-size:40px;font-weight:700;color:#fff;line-height:1;margin-bottom:5px;}
.dash-card .dc-lbl{font-size:11.5px;font-weight:600;color:rgba(255,255,255,.78);
  text-transform:uppercase;letter-spacing:.5px;}
.dc-nao{background:linear-gradient(135deg,#5A6478,#7A8498);}
.dc-atr{background:linear-gradient(135deg,#C03535,#E05050);}
.dc-and{background:linear-gradient(135deg,#1A4F8A,#2657A0);}
.dc-conc{background:linear-gradient(135deg,#166A45,#1E8A5A);}

/* ── IMPORT BOX ── */
.import-box{background:#EBF4FD;border:2px dashed #90BAE0;border-radius:var(--r-md);padding:22px;}
.import-box h4{font-size:14px;font-weight:600;color:var(--primary);margin-bottom:8px;}

/* ── BOTÕES ── */
.btn{display:inline-flex;align-items:center;gap:6px;padding:9px 18px;border-radius:var(--r-sm);
  font-size:13px;font-weight:600;border:none;cursor:pointer;font-family:'DM Sans',sans-serif;
  transition:all var(--tr);}
.btn-primary{background:var(--primary);color:#fff;box-shadow:0 2px 8px rgba(27,58,92,.2);}
.btn-primary:hover{background:var(--plight);transform:translateY(-1px);}
.btn-ghost{background:var(--surface);color:var(--text2);border:1.5px solid var(--border);}
.btn-ghost:hover{border-color:var(--plight);color:var(--primary);}
.btn-danger{background:var(--danger);color:#fff;}
.btn-success{background:var(--success);color:#fff;}
.btn-warning{background:var(--accent);color:#fff;}
.acoes-bar{display:flex;gap:10px;margin-bottom:18px;flex-wrap:wrap;}

/* ── PROJ HEADER ── */
.proj-header{display:flex;align-items:center;gap:12px;flex-wrap:wrap;
  margin-bottom:18px;padding-bottom:14px;border-bottom:1.5px solid var(--border);}
.proj-header h2{font-family:'DM Serif Display',serif;font-size:20px;color:var(--primary);}

/* ── LOADING ── */
.loading-state{text-align:center;padding:60px 20px;color:var(--text3);}

/* ── ACESSOS ── */
.secao-acessos{margin-top:16px;padding-top:16px;border-top:1.5px solid var(--border);}
.secao-acessos h4{font-size:12px;font-weight:700;text-transform:uppercase;
  letter-spacing:.5px;color:var(--text2);margin-bottom:12px;}
.checkbox-group{display:flex;flex-wrap:wrap;gap:10px;}
.checkbox-item{display:flex;align-items:center;gap:7px;font-size:13px;color:var(--text);
  min-width:160px;cursor:pointer;}
.checkbox-item input{width:15px;height:15px;accent-color:var(--primary);}

/* ── GANTT LEGENDA ── */
.gantt-leg{display:flex;gap:18px;margin-bottom:12px;flex-wrap:wrap;}
.gantt-leg span{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text2);font-weight:500;}
.gantt-leg i{display:inline-block;width:16px;height:10px;border-radius:3px;}

/* ── SECTION DIVIDER ── */
.divider{height:1px;background:var(--border);margin:24px 0;}

/* ── LOGIN PAGE ── */
.login-outer{
  min-height:100vh;display:flex;align-items:center;justify-content:center;
  background:linear-gradient(135deg,#0a1628 0%,#1B3A5C 55%,#2657A0 100%);
  padding:20px;position:relative;overflow:hidden;
}
.login-outer::before{
  content:'';position:absolute;width:600px;height:600px;border-radius:50%;
  background:radial-gradient(circle,rgba(232,160,32,.12) 0%,transparent 70%);
  top:-150px;right:-100px;pointer-events:none;
}
.login-outer::after{
  content:'';position:absolute;width:400px;height:400px;border-radius:50%;
  background:radial-gradient(circle,rgba(38,87,160,.3) 0%,transparent 70%);
  bottom:-100px;left:-80px;pointer-events:none;
}
.login-card{
  background:#fff;border-radius:var(--r-lg);padding:50px 46px 42px;
  width:100%;max-width:420px;
  box-shadow:0 24px 64px rgba(10,22,40,.3),0 0 0 1px rgba(255,255,255,.08);
  position:relative;z-index:1;
  animation:slideUp .45s cubic-bezier(.4,0,.2,1);
}
@keyframes slideUp{from{opacity:0;transform:translateY(24px);}to{opacity:1;transform:translateY(0);}}
.login-title{font-family:'DM Serif Display',serif;font-size:28px;color:var(--primary);
  text-align:center;margin-bottom:4px;letter-spacing:-.3px;}
.login-sub{text-align:center;color:var(--text2);font-size:13px;margin-bottom:30px;}
.login-icon{font-size:40px;display:block;text-align:center;margin-bottom:16px;}

/* ── STREAMLIT OVERRIDES ── */
div[data-testid="stForm"]{background:transparent!important;border:none!important;padding:0!important;}
.stButton>button{
  border-radius:var(--r-sm)!important;
  font-family:'DM Sans',sans-serif!important;
  font-weight:600!important;
  transition:all var(--tr)!important;
}
.stSelectbox>div>div,.stTextInput>div>div>input,.stDateInput>div>div>input{
  border-radius:var(--r-sm)!important;border:1.5px solid var(--border)!important;
  font-family:'DM Sans',sans-serif!important;
}
.stDataFrame{border-radius:var(--r-md)!important;overflow:hidden!important;}
div[data-testid="column"]{padding:0 4px!important;}
.stAlert{border-radius:var(--r-sm)!important;}

/* ── MOBILE ── */
@media(max-width:768px){
  .topbar{padding:0 14px;}
  .main-pad{padding:16px 14px;}
  .kanban-grid{grid-template-columns:1fr;}
  .card-grid{grid-template-columns:1fr;}
  .dash-grid{grid-template-columns:repeat(2,1fr);}
  .navbar{padding:0 10px;}
  .nav-tab{padding:13px 12px;font-size:12px;}
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
DEFAULTS = {
    "token": None, "usuario": None, "tela": "login",
    "projeto_selecionado": None, "proj_modo": "lista",
    "proj_sort_col": "prazo", "proj_sort_dir": 1,
    "tarefa_editando": None, "projeto_editando": None, "usuario_editando": None,
    "msg_ok": None, "msg_err": None,
    "show_form_proj": False, "show_form_tar": False, "show_form_usr": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# API — server-side (sem CORS)
# ─────────────────────────────────────────────
@st.cache_data(ttl=30, show_spinner=False)
def api_cached(path, token):
    return _api_call(path, "GET", {}, token)

def api(path, method="GET", data=None):
    return _api_call(path, method, data or {}, st.session_state.token)

def _api_call(path, method, data, token):
    payload = {"_method": method}
    if token:
        payload["token"] = token
    if data:
        payload.update(data)
    try:
        r = requests.post(GAS_URL, params={"path": path}, json=payload, timeout=30, allow_redirects=True)
        res = r.json()
        if not res.get("success"):
            raise Exception(res.get("error", "Erro desconhecido"))
        return res.get("data")
    except requests.exceptions.Timeout:
        raise Exception("Tempo esgotado. Tente novamente.")
    except Exception as e:
        raise e

def api_get(path):
    return api_cached(path, st.session_state.token)

# ─────────────────────────────────────────────
# UTILITÁRIOS
# ─────────────────────────────────────────────
def iso_br(s):
    if not s or s == "—": return "—"
    try:
        p = str(s).split("-"); return f"{p[2]}/{p[1]}/{p[0]}"
    except: return str(s)

def parse_date(s):
    if not s: return None
    try: return datetime.strptime(str(s), "%Y-%m-%d").date()
    except: return None

def ir(tela, **kw):
    st.session_state.tela = tela
    for k, v in kw.items():
        st.session_state[k] = v
    # Limpa cache ao navegar
    api_cached.clear()
    st.rerun()

def is_admin():
    return st.session_state.usuario and st.session_state.usuario.get("nivel") == "Administrador"

def ok(msg): st.session_state.msg_ok = msg
def err(msg): st.session_state.msg_err = msg

def show_msgs():
    if st.session_state.msg_ok:
        st.success(st.session_state.msg_ok, icon="✅")
        st.session_state.msg_ok = None
    if st.session_state.msg_err:
        st.error(st.session_state.msg_err, icon="🚨")
        st.session_state.msg_err = None

def badge(status, sinalizador=""):
    if sinalizador == "Atrasada":
        return '<span class="badge badge-atraso">⚠ Atrasada</span>'
    m = {"Não iniciada": ("badge-nao",""), "Em andamento": ("badge-and","🔵"), "Concluída": ("badge-conc","✓")}
    cls, ico = m.get(status, ("badge-nao",""))
    return f'<span class="badge {cls}">{ico} {status}</span>'

def sinalizador_label(sin):
    if sin == "Atrasada": return "🔴 Atrasada"
    if sin == "Concluída": return "✅ Concluída"
    return "🟢 No prazo"

# ─────────────────────────────────────────────
# TOPBAR + NAVBAR
# ─────────────────────────────────────────────
def render_topbar():
    u = st.session_state.usuario or {}
    nome = u.get("nome",""); nivel = u.get("nivel","")
    st.markdown(f"""
    <div class="topbar">
      <div class="topbar-brand">
        <span class="topbar-icon">📋</span>
        <span class="topbar-name">Projex</span>
      </div>
      <div class="topbar-right">
        <span class="topbar-user">👤 {nome} · {nivel}</span>
      </div>
    </div>""", unsafe_allow_html=True)

def render_nav():
    tela = st.session_state.tela
    abas = [("📊 Visão Geral","painel"), ("📈 Painel Geral","dashboard")]
    if is_admin():
        abas.insert(1, ("📁 Projetos","projetos"))
        abas.insert(2, ("✅ Tarefas","tarefas"))
        abas.insert(3, ("👤 Usuários","usuarios"))

    tabs_html = ""
    for lbl, t in abas:
        cls = "active" if (tela == t or (tela=="detalhe_projeto" and t=="painel")) else ""
        if t == "dashboard": cls += " highlight"
        tabs_html += f'<span class="nav-tab {cls}" onclick="void(0)">{lbl}</span>'

    st.markdown(f'<nav class="navbar">{tabs_html}</nav>', unsafe_allow_html=True)

    cols = st.columns([1]*len(abas) + [0.5])
    for i,(lbl,t) in enumerate(abas):
        with cols[i]:
            if st.button(lbl, key=f"nav_{t}", use_container_width=True,
                         type="primary" if tela==t else "secondary"):
                st.session_state.show_form_proj = False
                st.session_state.show_form_tar = False
                st.session_state.show_form_usr = False
                st.session_state.tarefa_editando = None
                st.session_state.projeto_editando = None
                st.session_state.usuario_editando = None
                ir(t)
    with cols[-1]:
        if st.button("🚪 Sair", use_container_width=True):
            for k in DEFAULTS:
                st.session_state[k] = DEFAULTS[k]
            api_cached.clear()
            ir("login")

# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────
def tela_login():
    # Esconde tudo do Streamlit para mostrar login fullscreen
    st.markdown("""
    <style>
    .stApp > div:first-child {background:linear-gradient(135deg,#0a1628 0%,#1B3A5C 55%,#2657A0 100%)!important;}
    </style>""", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("""
        <div style="padding-top:8vh;">
          <div class="login-card">
            <span class="login-icon">📋</span>
            <h1 class="login-title">Bem-vindo ao Projex</h1>
            <p class="login-sub">Gestão inteligente de projetos e tarefas</p>
          </div>
        </div>""", unsafe_allow_html=True)

        with st.container(border=True):
            login_val = st.text_input("Usuário", placeholder="Digite seu login",
                                      label_visibility="collapsed",
                                      key="li_login")
            senha_val = st.text_input("Senha", type="password", placeholder="••••••••",
                                      label_visibility="collapsed",
                                      key="li_senha")
            col1, col2 = st.columns([3,1])
            entrar = col1.button("Entrar →", type="primary", use_container_width=True, key="li_btn")
            if entrar:
                if not login_val or not senha_val:
                    st.error("Preencha usuário e senha.")
                else:
                    with st.spinner("Autenticando..."):
                        try:
                            data = api("login","POST",{"login":login_val,"senha":senha_val})
                            st.session_state.token = data["token"]
                            st.session_state.usuario = data["usuario"]
                            ir("painel")
                        except Exception as e:
                            st.error(f"Credenciais inválidas: {e}")

# ─────────────────────────────────────────────
# PAINEL — VISÃO GERAL DE PROJETOS
# ─────────────────────────────────────────────
def tela_painel():
    show_msgs()
    st.markdown('<div class="page-title">📊 Visão Geral de Projetos</div>', unsafe_allow_html=True)

    with st.spinner("Carregando projetos..."):
        try:
            projetos = api_get("projetos") or []
            tarefas  = api_get("tarefas")  or []
        except Exception as e:
            st.error(f"Erro ao carregar: {e}"); return

    # Calcula stats
    tp = {}
    for t in tarefas: tp.setdefault(t["projeto"],[]).append(t)
    for p in projetos:
        arr = tp.get(p["nome"],[])
        total = len(arr); conc = sum(1 for t in arr if t["status"]=="Concluída")
        atr   = sum(1 for t in arr if t.get("sinalizador")=="Atrasada")
        p["_total"]=total; p["_conc"]=conc; p["_atr"]=atr
        p["_perc"] = round((conc/total)*100) if total else 0
        p["_done"] = total>0 and conc==total

    # Filtros
    with st.expander("🔍 Filtros", expanded=False):
        c1,c2,c3,c4,c5 = st.columns(5)
        nomes = ["Todos"]+[p["nome"] for p in projetos]
        f_nome = c1.selectbox("Projeto", nomes, key="fp_nome")
        tipos  = ["Todos","PG","Rotina","Projeto"]
        f_tipo = c2.selectbox("Tipo", tipos, key="fp_tipo")
        ordem  = c3.selectbox("Ordenar", ["Nome","Data Durante"], key="fp_ord")
        f_atr  = c4.checkbox("Somente com atrasos", key="fp_atr")
        f_conc = c5.checkbox("Ocultar concluídos", key="fp_conc")

    lista = projetos[:]
    if f_nome!="Todos": lista=[p for p in lista if p["nome"]==f_nome]
    if f_tipo!="Todos": lista=[p for p in lista if p.get("tipo")==f_tipo]
    if f_atr:  lista=[p for p in lista if p["_atr"]>0]
    if f_conc: lista=[p for p in lista if not p["_done"]]
    if ordem=="Data Durante":
        lista.sort(key=lambda p: parse_date(p.get("inicioDurante")) or date(9999,1,1))
    else:
        lista.sort(key=lambda p: p["nome"])

    if not lista:
        st.info("Nenhum projeto encontrado."); return

    # Grade de cards — 2 colunas
    for i in range(0, len(lista), 2):
        row = lista[i:i+2]
        cols = st.columns(len(row))
        for j, p in enumerate(row):
            with cols[j]:
                perc = p["_perc"]
                prog_cls = "danger" if p["_atr"]>0 else ("" if perc<50 else "warn" if perc<100 else "")
                durante = (f"📅 Durante: {iso_br(p.get('inicioDurante'))} — {iso_br(p.get('fimDurante'))}"
                           if p.get("inicioDurante") else "📅 Sem data durante")
                atr_badge = f'<span class="badge badge-atraso">⚠ {p["_atr"]} em atraso</span>' if p["_atr"]>0 else ""
                conc_badge = '<span class="badge badge-conc">✓ Concluído</span>' if p["_done"] else ""

                st.markdown(f"""
                <div class="proj-card">
                  <h3>{p['nome']}</h3>
                  <p class="meta"><strong>Cliente:</strong> {p.get('cliente') or '—'} &nbsp;|&nbsp;
                     <strong>Tipo:</strong> {p.get('tipo','—')} &nbsp;|&nbsp;
                     <strong>Unidade:</strong> {p.get('unidade') or '—'}</p>
                  <p class="durante">{durante}</p>
                  <div style="margin:6px 0;">{atr_badge}{conc_badge}</div>
                  <div class="prog-wrap"><div class="prog-fill {prog_cls}" style="width:{perc}%"></div></div>
                  <div class="card-footer">
                    <span class="card-perc">{perc}% concluído</span>
                    <span class="card-perc">{p['_conc']}/{p['_total']} tarefas</span>
                  </div>
                </div>""", unsafe_allow_html=True)

                if st.button("Abrir projeto →", key=f"open_{p['nome']}", use_container_width=True):
                    ir("detalhe_projeto", projeto_selecionado=p["nome"],
                       proj_modo="lista", proj_sort_col="prazo", proj_sort_dir=1)

# ─────────────────────────────────────────────
# DETALHE DO PROJETO — Lista + Kanban + Editar
# ─────────────────────────────────────────────
def tela_detalhe_projeto():
    show_msgs()
    nome = st.session_state.projeto_selecionado

    # Header
    c_back, c_title, c_modo = st.columns([1, 5, 1.5])
    with c_back:
        if st.button("← Voltar", key="back_proj"):
            ir("painel")
    with c_title:
        st.markdown(f'<div style="font-family:\'DM Serif Display\',serif;font-size:20px;color:#1B3A5C;padding:8px 0;">📁 {nome}</div>', unsafe_allow_html=True)
    with c_modo:
        modo_label = "🗂️ Kanban" if st.session_state.proj_modo=="lista" else "📋 Lista"
        if st.button(modo_label, key="toggle_modo", use_container_width=True):
            st.session_state.proj_modo = "kanban" if st.session_state.proj_modo=="lista" else "lista"
            st.rerun()

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    with st.spinner("Carregando tarefas..."):
        try:
            tarefas = api_get("tarefas") or []
            tarefas = [t for t in tarefas if t.get("projeto")==nome]
        except Exception as e:
            st.error(f"Erro: {e}"); return

    # ── MODO EDIÇÃO DE TAREFA ──
    if st.session_state.tarefa_editando:
        _form_editar_tarefa(st.session_state.tarefa_editando, nome)
        return

    if not tarefas:
        st.info("Nenhuma tarefa neste projeto.")
        return

    if st.session_state.proj_modo == "kanban":
        _render_kanban(tarefas, nome)
    else:
        _render_lista(tarefas, nome)

def _render_lista(tarefas, nome):
    # Ordenação
    col_map = {"ID":"id","Tarefa":"tarefa","Prazo":"prazo","Status":"status","Situação":"sinalizador"}
    ordem_opts = list(col_map.keys())
    c1, c2, c3 = st.columns([2,1,1])
    col_sel = c1.selectbox("Ordenar por", ordem_opts, key="ls_col",
                            index=ordem_opts.index({v:k for k,v in col_map.items()}.get(st.session_state.proj_sort_col,"Prazo")))
    direcao = c2.radio("Direção", ["↑ Asc","↓ Desc"], horizontal=True, key="ls_dir")
    f_status = c3.selectbox("Filtrar status", ["Todos","Não iniciada","Em andamento","Concluída"], key="ls_st")

    sort_key = col_map[col_sel]
    sort_dir = 1 if "Asc" in direcao else -1
    lista = tarefas[:]
    if f_status != "Todos": lista = [t for t in lista if t.get("status")==f_status]
    lista.sort(key=lambda t: (t.get(sort_key) or ""), reverse=(sort_dir==-1))

    st.markdown('<div class="tbl-wrap">', unsafe_allow_html=True)
    for t in lista:
        with st.container():
            c1,c2,c3,c4,c5,c6 = st.columns([0.5,3,1.5,1.5,1.5,1])
            c1.markdown(f'`{t["id"]}`')
            c2.markdown(f'**{t["tarefa"]}**')
            c3.markdown(f'📅 {iso_br(t.get("prazo"))}')
            c4.markdown(badge(t.get("status",""), t.get("sinalizador","")), unsafe_allow_html=True)
            anexo_txt = f'[📎]({t["anexo"]})' if t.get("anexo") else "—"
            c5.markdown(anexo_txt)
            if c6.button("✏️", key=f"edt_{t['id']}", help="Editar"):
                st.session_state.tarefa_editando = t
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def _render_kanban(tarefas, nome):
    grupos = {"Não iniciada":[], "Em andamento":[], "Concluída":[]}
    for t in tarefas: grupos.get(t.get("status","Não iniciada"), grupos["Não iniciada"]).append(t)

    colunas = [
        ("Não iniciada","kh-nao","⬜"),
        ("Em andamento","kh-and","🔵"),
        ("Concluída","kh-conc","✅"),
    ]

    cols = st.columns(3)
    for i,(status, cls, ico) in enumerate(colunas):
        with cols[i]:
            count = len(grupos[status])
            st.markdown(f"""
            <div class="kanban-col">
              <div class="kanban-header {cls}">
                <span>{ico} {status}</span>
                <span class="k-count">{count}</span>
              </div>""", unsafe_allow_html=True)

            for t in grupos[status]:
                sin = t.get("sinalizador","")
                card_cls = "atrasada" if sin=="Atrasada" else "no-prazo"
                anexo_html = f'<p class="kc-meta"><a href="{t["anexo"]}" target="_blank">📎 Ver anexo</a></p>' if t.get("anexo") else ""
                st.markdown(f"""
                <div class="kanban-card {card_cls}">
                  <strong>{t['tarefa']}</strong>
                  <p class="kc-meta">📅 {iso_br(t.get('prazo'))}</p>
                  <p class="kc-meta">{badge(t.get('status',''), sin)}</p>
                  {anexo_html}
                </div>""", unsafe_allow_html=True)
                if st.button(f"✏️ Editar #{t['id']}", key=f"k_{t['id']}", use_container_width=True):
                    st.session_state.tarefa_editando = t
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

def _form_editar_tarefa(t, nome):
    st.markdown(f'<div class="form-title">✏️ Editar Tarefa #{t["id"]}</div>', unsafe_allow_html=True)

    if st.button("← Voltar às tarefas", key="back_tar"):
        st.session_state.tarefa_editando = None
        api_cached.clear()
        st.rerun()

    with st.container(border=True):
        st.markdown(f"**{t['tarefa']}** · Projeto: `{t.get('projeto','')}`")
        st.caption(f"Prazo original: {iso_br(t.get('prazo'))}")

        status_opts = ["Não iniciada","Em andamento","Concluída"]
        status = st.selectbox("Novo status", status_opts,
                               index=status_opts.index(t.get("status","Não iniciada")),
                               key="tar_status")
        data_conc = st.date_input("Data de Conclusão",
                                   value=parse_date(t.get("dataConclusao")) or None,
                                   key="tar_data_conc")

        st.markdown("**Anexo**")
        if t.get("anexo"):
            st.markdown(f'📎 Anexo atual: [{t["anexo"][:40]}...]({t["anexo"]})')
        arquivo = st.file_uploader("Novo anexo (PDF/imagem — substitui o atual)",
                                    accept_multiple_files=False,
                                    type=["pdf","png","jpg","jpeg"],
                                    key="tar_file")

        if st.button("💾 Salvar alterações", type="primary", key="tar_save"):
            payload = {
                "id": t["id"], "status": status,
                "dataConclusao": data_conc.isoformat() if data_conc else "",
                "tarefa": t["tarefa"], "projeto": t["projeto"],
                "prazo": t.get("prazo",""),
                "centroCusto": t.get("centroCusto",""),
                "anexoObrigatorio": t.get("anexoObrigatorio","Não"),
            }
            if arquivo:
                b64 = base64.b64encode(arquivo.read()).decode()
                payload["anexoBase64"] = f"data:{arquivo.type};base64,{b64}"
                payload["nomeArquivo"] = arquivo.name

            try:
                api("tarefas","PUT",payload)
                st.session_state.tarefa_editando = None
                api_cached.clear()
                ok("Tarefa atualizada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# ─────────────────────────────────────────────
# ADMIN — PROJETOS (CRUD completo)
# ─────────────────────────────────────────────
def tela_projetos():
    show_msgs()
    st.markdown('<div class="page-title">📁 Gerenciar Projetos</div>', unsafe_allow_html=True)

    with st.spinner():
        try: projetos = api_get("projetos") or []
        except Exception as e: st.error(f"Erro: {e}"); return

    c1,c2 = st.columns([1,5])
    with c1:
        if st.button("＋ Novo Projeto", type="primary", use_container_width=True):
            st.session_state.projeto_editando = {}
            st.session_state.show_form_proj = True
            st.rerun()

    # Formulário novo/editar
    if st.session_state.show_form_proj:
        p = st.session_state.projeto_editando or {}
        is_novo = not p.get("id")
        st.markdown(f'<div class="form-title">{"Novo Projeto" if is_novo else "Editar: "+p.get("nome","")}</div>', unsafe_allow_html=True)

        with st.form("form_proj", border=True):
            nome = st.text_input("Nome *", value=p.get("nome",""))
            c1,c2 = st.columns(2)
            tipo = c1.selectbox("Tipo", ["PG","Rotina","Projeto"],
                                 index=["PG","Rotina","Projeto"].index(p.get("tipo","PG")))
            cliente = c2.text_input("Cliente", value=p.get("cliente",""))
            c3,c4 = st.columns(2)
            unidade = c3.text_input("Unidade", value=p.get("unidade",""))
            centro = c4.text_input("Centro de Custo", value=str(p.get("centroCusto","")))

            st.markdown("**Datas do Projeto**")
            d1,d2,d3,d4 = st.columns(4)
            ini_prep = d1.date_input("Início Prep.", value=parse_date(p.get("inicioPrep")), key="pf_ip")
            ini_dur  = d2.date_input("Início Durante", value=parse_date(p.get("inicioDurante")), key="pf_id")
            fim_dur  = d3.date_input("Fim Durante", value=parse_date(p.get("fimDurante")), key="pf_fd")
            fim_des  = d4.date_input("Fim Desmob.", value=parse_date(p.get("fimDesmob")), key="pf_fm")

            c_s, c_c = st.columns(2)
            salvar   = c_s.form_submit_button("💾 Salvar", type="primary", use_container_width=True)
            cancelar = c_c.form_submit_button("Cancelar", use_container_width=True)

        if salvar:
            if not nome: st.error("Nome é obrigatório.")
            else:
                try:
                    api("projetos","POST",{
                        "id": p.get("id"), "nome":nome, "tipo":tipo, "cliente":cliente,
                        "unidade":unidade, "centroCusto":centro,
                        "inicioPrep":  ini_prep.isoformat() if ini_prep else "",
                        "inicioDurante": ini_dur.isoformat() if ini_dur else "",
                        "fimDurante":  fim_dur.isoformat() if fim_dur else "",
                        "fimDesmob":   fim_des.isoformat() if fim_des else "",
                    })
                    st.session_state.show_form_proj = False
                    st.session_state.projeto_editando = None
                    api_cached.clear()
                    ok("Projeto salvo!"); st.rerun()
                except Exception as e: st.error(f"Erro: {e}")
        if cancelar:
            st.session_state.show_form_proj = False
            st.session_state.projeto_editando = None
            st.rerun()

    # Tabela de projetos
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    if not projetos: st.info("Nenhum projeto cadastrado."); return

    # Cabeçalho
    hc = st.columns([0.5,2.5,1,1.5,1,1,1.2,1.2,1.2,1.2,1.2])
    for col,lbl in zip(hc,["ID","Nome","Tipo","Cliente","Unidade","C.Custo","Iní.Prep","Iní.Dur.","Fim Dur.","Fim Desm.","Ações"]):
        col.markdown(f"**{lbl}**")
    st.divider()

    for p in sorted(projetos, key=lambda x: x.get("nome","")):
        r = st.columns([0.5,2.5,1,1.5,1,1,1.2,1.2,1.2,1.2,1.2])
        r[0].caption(str(p.get("id","")))
        r[1].markdown(f"**{p['nome']}**")
        r[2].caption(p.get("tipo","—"))
        r[3].caption(p.get("cliente","—"))
        r[4].caption(p.get("unidade","—"))
        r[5].caption(str(p.get("centroCusto","—")))
        r[6].caption(iso_br(p.get("inicioPrep")))
        r[7].caption(iso_br(p.get("inicioDurante")))
        r[8].caption(iso_br(p.get("fimDurante")))
        r[9].caption(iso_br(p.get("fimDesmob")))
        with r[10]:
            c_e,c_d = st.columns(2)
            if c_e.button("✏️", key=f"ep_{p['id']}", use_container_width=True):
                st.session_state.projeto_editando = p
                st.session_state.show_form_proj = True
                st.rerun()
            if c_d.button("🗑️", key=f"dp_{p['id']}", use_container_width=True):
                try:
                    api("projetos","DELETE",{"id":p["id"]})
                    api_cached.clear(); ok("Projeto excluído."); st.rerun()
                except Exception as e: err(f"Erro: {e}")
        st.divider()

# ─────────────────────────────────────────────
# ADMIN — TAREFAS (CRUD + importação CSV)
# ─────────────────────────────────────────────
def tela_tarefas():
    show_msgs()
    st.markdown('<div class="page-title">✅ Gerenciar Tarefas</div>', unsafe_allow_html=True)

    with st.spinner():
        try:
            tarefas  = api_get("tarefas")  or []
            projetos = api_get("projetos") or []
        except Exception as e: st.error(f"Erro: {e}"); return

    proj_map   = {p["nome"]:p for p in projetos}
    proj_nomes = [p["nome"] for p in projetos]

    tab_lista, tab_form, tab_import = st.tabs(["📋 Lista de Tarefas","➕ Nova / Editar","📥 Importar CSV"])

    # ── LISTA ──
    with tab_lista:
        c1,c2,c3 = st.columns(3)
        f_proj = c1.selectbox("Projeto",["Todos"]+proj_nomes, key="tl_proj")
        f_stat = c2.selectbox("Status",["Todos","Não iniciada","Em andamento","Concluída"], key="tl_stat")
        f_ord  = c3.selectbox("Ordenar",["Prazo","Tarefa","Projeto","Status"], key="tl_ord")

        lista = tarefas[:]
        if f_proj!="Todos": lista=[t for t in lista if t.get("projeto")==f_proj]
        if f_stat!="Todos": lista=[t for t in lista if t.get("status")==f_stat]
        ord_map={"Prazo":"prazo","Tarefa":"tarefa","Projeto":"projeto","Status":"status"}
        lista.sort(key=lambda t: t.get(ord_map[f_ord],"") or "")

        st.caption(f"{len(lista)} tarefa(s)")
        if not lista: st.info("Nenhuma tarefa.")
        else:
            # Cabeçalho
            hd = st.columns([0.4,3,2,1.5,1.5,1,1])
            for col,lbl in zip(hd,["ID","Tarefa","Projeto","Prazo","Status","Anexo","Ação"]):
                col.markdown(f"**{lbl}**")
            st.divider()
            for t in lista:
                r = st.columns([0.4,3,2,1.5,1.5,1,1])
                r[0].caption(str(t["id"]))
                r[1].markdown(f"**{t['tarefa']}**")
                r[2].caption(t.get("projeto",""))
                r[3].caption(iso_br(t.get("prazo")))
                r[4].markdown(badge(t.get("status",""),t.get("sinalizador","")), unsafe_allow_html=True)
                r[5].markdown(f'[📎]({t["anexo"]})' if t.get("anexo") else "—")
                with r[6]:
                    c_e,c_d = st.columns(2)
                    if c_e.button("✏️", key=f"etal_{t['id']}", use_container_width=True):
                        st.session_state.tarefa_editando = t
                        # Muda para aba form — simulamos via rerun com flag
                        st.session_state._ir_tab_form = True
                        st.rerun()
                    if c_d.button("🗑️", key=f"dtal_{t['id']}", use_container_width=True):
                        try:
                            api("tarefas","DELETE",{"id":t["id"]})
                            api_cached.clear(); ok("Tarefa excluída."); st.rerun()
                        except Exception as e: err(f"Erro: {e}")
                st.divider()

    # ── NOVA / EDITAR ──
    with tab_form:
        t = st.session_state.tarefa_editando or {}
        is_nova = not t.get("id")
        form_title = "Nova Tarefa" if is_nova else ("Editar #" + str(t.get("id","")) + ": " + str(t.get("tarefa",""))[:40])
        st.markdown(f'<div class="form-title">{form_title}</div>', unsafe_allow_html=True)

        if not is_nova and st.button("✕ Limpar / nova tarefa", key="tfl_limpar"):
            st.session_state.tarefa_editando = None; st.rerun()

        with st.form("form_tar", border=True):
            desc = st.text_input("Descrição *", value=t.get("tarefa",""))
            c1,c2 = st.columns(2)
            proj_idx = proj_nomes.index(t["projeto"]) if t.get("projeto") in proj_nomes else 0
            proj_sel = c1.selectbox("Projeto *", proj_nomes, index=proj_idx)
            centro_auto = proj_map.get(proj_sel,{}).get("centroCusto","")
            c2.text_input("Centro de Custo (automático)", value=str(centro_auto), disabled=True)

            c3,c4 = st.columns(2)
            prazo  = c3.date_input("Prazo *", value=parse_date(t.get("prazo")) or date.today())
            status = c4.selectbox("Status",["Não iniciada","Em andamento","Concluída"],
                                   index=["Não iniciada","Em andamento","Concluída"].index(t.get("status","Não iniciada")))
            anexo  = st.selectbox("Anexo Obrigatório?",["Não","Sim"],
                                   index=0 if t.get("anexoObrigatorio","Não")=="Não" else 1)
            salvar = st.form_submit_button("💾 Salvar", type="primary", use_container_width=True)

        if salvar:
            if not desc or not proj_sel: st.error("Descrição e Projeto são obrigatórios.")
            else:
                try:
                    api("tarefas","POST",{
                        "id": t.get("id"), "tarefa":desc, "projeto":proj_sel,
                        "centroCusto":str(centro_auto), "prazo":prazo.isoformat(),
                        "status":status, "anexoObrigatorio":anexo,
                    })
                    st.session_state.tarefa_editando = None
                    api_cached.clear(); ok("Tarefa salva!"); st.rerun()
                except Exception as e: st.error(f"Erro: {e}")

    # ── IMPORTAR ──
    with tab_import:
        st.markdown("""
        <div class="import-box">
          <h4>📥 Importar Tarefas via CSV</h4>
          <p style="font-size:13px;color:#2657A0;">Colunas obrigatórias: <strong>Tarefa, Projeto, Prazo Conclusao, Anexo Obrigatorio</strong></p>
          <p style="font-size:12px;color:#566070;">Centro de Custo é preenchido automaticamente pelo projeto. Use o modelo abaixo.</p>
        </div>""", unsafe_allow_html=True)

        modelo = "Tarefa,Projeto,Prazo Conclusao,Anexo Obrigatorio\nExemplo de tarefa,Nome Exato do Projeto,2025-12-31,Não\n"
        st.download_button("📄 Baixar Modelo CSV", modelo, "modelo_tarefas.csv", "text/csv",
                            use_container_width=True)

        arq = st.file_uploader("Selecione o CSV", type=["csv"], key="import_file")
        if arq:
            try:
                txt = arq.read().decode("utf-8-sig")
                linhas = [l.split(",") for l in txt.strip().split("\n")]
                cab = [c.strip().lower() for c in linhas[0]]
                iT = next(i for i,c in enumerate(cab) if "tarefa" in c)
                iP = next(i for i,c in enumerate(cab) if "projeto" in c)
                iPr= next(i for i,c in enumerate(cab) if "prazo" in c)
                iA = next((i for i,c in enumerate(cab) if "anexo" in c), -1)

                tarefas_ex = api_get("tarefas") or []
                ex_set = {(t["tarefa"].lower(), t["projeto"].lower()) for t in tarefas_ex}

                importar, erros, ignoradas = [], [], []
                for i, l in enumerate(linhas[1:], 2):
                    if not any(c.strip() for c in l): continue
                    desc  = l[iT].strip() if iT<len(l) else ""
                    proj  = l[iP].strip() if iP<len(l) else ""
                    prazo = l[iPr].strip() if iPr<len(l) else ""
                    anexo = l[iA].strip() if iA>=0 and iA<len(l) else "Não"
                    if not desc or not proj or not prazo:
                        erros.append(f"Linha {i}: campos vazios."); continue
                    if proj.lower() not in {k.lower() for k in proj_map}:
                        erros.append(f"Linha {i}: projeto '{proj}' não cadastrado."); continue
                    if (desc.lower(),proj.lower()) in ex_set:
                        ignoradas.append(f"Linha {i}: '{desc}' já existe."); continue
                    nome_proj = next(k for k in proj_map if k.lower()==proj.lower())
                    importar.append({"tarefa":desc,"projeto":nome_proj,
                        "centroCusto":str(proj_map[nome_proj].get("centroCusto","")),
                        "prazo":prazo,"status":"Não iniciada","anexoObrigatorio":anexo or "Não"})

                if erros:
                    for e in erros: st.error(e)
                elif not importar:
                    st.warning("Nenhuma tarefa nova.")
                    for ig in ignoradas: st.caption(ig)
                else:
                    st.success(f"Pronto para importar {len(importar)} tarefa(s). {len(ignoradas)} duplicatas ignoradas.")
                    if st.button(f"✅ Confirmar importação de {len(importar)} tarefa(s)", type="primary"):
                        csv_body = "Tarefa,Projeto,CentroCusto,Prazo,Status,Anexo Obrigatorio\n"
                        csv_body += "\n".join(
                            f"{t['tarefa']},{t['projeto']},{t['centroCusto']},{t['prazo']},{t['status']},{t['anexoObrigatorio']}"
                            for t in importar)
                        try:
                            api("importar-tarefas","POST",{"csv":csv_body})
                            api_cached.clear(); ok(f"{len(importar)} tarefa(s) importada(s)!"); st.rerun()
                        except Exception as e: st.error(f"Erro: {e}")
            except StopIteration:
                st.error("Cabeçalho inválido. Use o modelo fornecido.")
            except Exception as e:
                st.error(f"Erro ao processar arquivo: {e}")

# ─────────────────────────────────────────────
# ADMIN — USUÁRIOS (CRUD + acessos por projeto)
# ─────────────────────────────────────────────
def tela_usuarios():
    show_msgs()
    st.markdown('<div class="page-title">👤 Gerenciar Usuários</div>', unsafe_allow_html=True)

    with st.spinner():
        try:
            usuarios = api_get("usuarios") or []
            acessos  = api_get("acessos")  or []
            projetos = api_get("projetos") or []
        except Exception as e: st.error(f"Erro: {e}"); return

    proj_nomes = [p["nome"] for p in projetos]
    amap = {}
    for a in acessos: amap.setdefault(a["login"],[]).append(a["projeto"])

    if st.button("＋ Novo Usuário", type="primary"):
        st.session_state.usuario_editando = {}
        st.session_state.show_form_usr = True
        st.rerun()

    # Formulário
    if st.session_state.show_form_usr:
        u = st.session_state.usuario_editando or {}
        is_novo = not u.get("login")
        st.markdown(f'<div class="form-title">{"Novo Usuário" if is_novo else "Editar: "+u.get("nome","")}</div>', unsafe_allow_html=True)

        with st.form("form_usr", border=True):
            nome_u  = st.text_input("Nome *", value=u.get("nome",""))
            login_u = st.text_input("Login *", value=u.get("login",""), disabled=not is_novo)
            senha_u = st.text_input(
                "Senha *" if is_novo else "Senha (deixe em branco para manter)",
                type="password")
            nivel_u = st.selectbox("Nível",["Usuario","Administrador"],
                                    index=0 if u.get("nivel","Usuario")=="Usuario" else 1)

            acs_sel = []
            if nivel_u == "Usuario":
                st.markdown("---")
                st.markdown("**🔑 Projetos com Acesso**")
                acs_atuais = amap.get(u.get("login",""),[])
                acs_sel = st.multiselect("Selecione os projetos", proj_nomes, default=acs_atuais)

            c_s,c_c = st.columns(2)
            salvar   = c_s.form_submit_button("💾 Salvar", type="primary", use_container_width=True)
            cancelar = c_c.form_submit_button("Cancelar", use_container_width=True)

        if salvar:
            if not nome_u or not (login_u or u.get("login")): st.error("Nome e Login obrigatórios.")
            elif is_novo and not senha_u: st.error("Senha obrigatória para novo usuário.")
            else:
                try:
                    login_final = login_u or u.get("login")
                    api("usuarios","POST",{"nome":nome_u,"login":login_final,"senha":senha_u,"nivel":nivel_u})
                    api("acessos","POST",{"login":login_final,"projetos":",".join(acs_sel) if nivel_u=="Usuario" else ""})
                    st.session_state.show_form_usr = False
                    st.session_state.usuario_editando = None
                    api_cached.clear(); ok("Usuário salvo!"); st.rerun()
                except Exception as e: st.error(f"Erro: {e}")
        if cancelar:
            st.session_state.show_form_usr = False
            st.session_state.usuario_editando = None
            st.rerun()

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Cabeçalho
    hd = st.columns([2,1.5,1.5,3,1.2])
    for col,lbl in zip(hd,["Nome","Login","Nível","Projetos com Acesso","Ações"]):
        col.markdown(f"**{lbl}**")
    st.divider()

    for u in sorted(usuarios, key=lambda x: x.get("nome","")):
        projs = ("Todos (Admin)" if u.get("nivel")=="Administrador"
                 else (", ".join(amap.get(u["login"],[])) or "Nenhum"))
        r = st.columns([2,1.5,1.5,3,1.2])
        r[0].markdown(f"**{u['nome']}**")
        r[1].caption(u.get("login",""))
        r[2].caption(u.get("nivel",""))
        r[3].caption(projs)
        with r[4]:
            c_e,c_d = st.columns(2)
            if c_e.button("✏️", key=f"eu_{u['login']}", use_container_width=True):
                st.session_state.usuario_editando = u
                st.session_state.show_form_usr = True
                st.rerun()
            if c_d.button("🗑️", key=f"du_{u['login']}", use_container_width=True):
                try:
                    api("usuarios","DELETE",{"login":u["login"]})
                    api_cached.clear(); ok("Usuário excluído."); st.rerun()
                except Exception as e: err(f"Erro: {e}")
        st.divider()

# ─────────────────────────────────────────────
# DASHBOARD — KPIs + Gantt com Plotly
# ─────────────────────────────────────────────
def tela_dashboard():
    show_msgs()
    st.markdown('<div class="page-title">📈 Painel Geral</div>', unsafe_allow_html=True)

    with st.spinner("Carregando dados..."):
        try:
            projetos = api_get("todos-projetos") or []
            tarefas  = api_get("todas-tarefas")  or []
            acessos  = api_get("acessos")         or []
        except Exception as e: st.error(f"Erro: {e}"); return

    ulogin = (st.session_state.usuario or {}).get("login","")
    meus = {a["projeto"] for a in acessos if a["login"]==ulogin}

    tp = {}
    for t in tarefas: tp.setdefault(t["projeto"],[]).append(t)
    for p in projetos:
        arr = tp.get(p["nome"],[])
        p["_total"] = len(arr)
        p["_conc"] = sum(1 for t in arr if t["status"]=="Concluída")
        p["_atr"]  = sum(1 for t in arr if t.get("sinalizador")=="Atrasada")
        p["_done"] = p["_total"]>0 and p["_conc"]==p["_total"]

    # Filtros
    with st.expander("🔍 Filtros", expanded=False):
        c1,c2,c3 = st.columns(3)
        f_proj  = c1.selectbox("Projeto",["Todos"]+[p["nome"] for p in projetos], key="db_proj")
        f_meus  = c2.checkbox("Somente meus projetos", key="db_meus")
        f_oconc = c3.checkbox("Ocultar concluídos", key="db_oconc")

    lista = projetos[:]
    if f_proj!="Todos": lista=[p for p in lista if p["nome"]==f_proj]
    if f_meus:  lista=[p for p in lista if p["nome"] in meus]
    if f_oconc: lista=[p for p in lista if not p["_done"]]

    tar_vis = [t for t in tarefas if any(p["nome"]==t["projeto"] for p in lista)]

    # KPI Cards
    n_nao  = sum(1 for t in tar_vis if t.get("status")=="Não iniciada")
    n_atr  = sum(1 for t in tar_vis if t.get("sinalizador")=="Atrasada")
    n_and  = sum(1 for t in tar_vis if t.get("status")=="Em andamento")
    n_conc = sum(1 for t in tar_vis if t.get("status")=="Concluída")

    cols = st.columns(4)
    for col,(num,lbl,cls) in zip(cols,[
        (n_nao,"Não Iniciadas","dc-nao"),
        (n_atr,"Em Atraso","dc-atr"),
        (n_and,"Em Andamento","dc-and"),
        (n_conc,"Concluídas","dc-conc"),
    ]):
        col.markdown(f"""
        <div class="dash-card {cls}">
          <div class="dc-num">{num}</div>
          <div class="dc-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Gantt
    com_data = [p for p in lista if p.get("inicioDurante") or p.get("inicioPrep")]
    if not com_data:
        st.info("Nenhum projeto com datas para exibir no Gantt.")
        return

    st.markdown("#### 📅 Gantt de Projetos")
    st.markdown("""
    <div class="gantt-leg">
      <span><i style="background:linear-gradient(90deg,#2657A0,#4A7FC0)"></i>Preparativo</span>
      <span><i style="background:linear-gradient(90deg,#166A45,#1E8A5A)"></i>Durante</span>
      <span><i style="background:linear-gradient(90deg,#B06010,#E8A020)"></i>Desmobilização</span>
      <span><i style="background:#e74c3c;width:3px"></i>Hoje</span>
    </div>""", unsafe_allow_html=True)

    try:
        import plotly.graph_objects as go

        fig = go.Figure()
        cores = {"Preparativo":("#2657A0","#4A7FC0"),"Durante":("#166A45","#1E8A5A"),"Desmob.":("#B06010","#E8A020")}

        # Monta barras usando datas absolutas em milliseconds (epoch) — compatível com xaxis type=date
        for p in com_data:
            nm = p["nome"]
            fases = []
            if p.get("inicioPrep") and p.get("inicioDurante"):
                fases.append(("Preparativo", p["inicioPrep"], p["inicioDurante"], "#2657A0"))
            if p.get("inicioDurante") and p.get("fimDurante"):
                fases.append(("Durante", p["inicioDurante"], p["fimDurante"], "#1E8A5A"))
            if p.get("fimDurante") and p.get("fimDesmob"):
                fases.append(("Desmob.", p["fimDurante"], p["fimDesmob"], "#E8A020"))

            for fase, ini, fim, cor in fases:
                try:
                    d_ini = datetime.strptime(ini, "%Y-%m-%d")
                    d_fim = datetime.strptime(fim, "%Y-%m-%d")
                    # Converte para ms epoch — única forma confiável com barmode+date axis
                    ms_ini = int(d_ini.timestamp() * 1000)
                    ms_fim = int(d_fim.timestamp() * 1000)
                    dur_ms = ms_fim - ms_ini
                    if dur_ms <= 0:
                        continue
                    fig.add_trace(go.Bar(
                        name=fase,
                        y=[nm],
                        x=[dur_ms],
                        base=[ms_ini],
                        orientation="h",
                        marker=dict(color=cor, line=dict(width=0)),
                        hovertemplate=(
                            f"<b>{nm}</b><br>{fase}<br>"
                            f"{iso_br(ini)} → {iso_br(fim)}<extra></extra>"
                        ),
                        showlegend=False,
                    ))
                except Exception:
                    pass

        # Linha de hoje em ms epoch
        hoje_dt  = datetime.combine(date.today(), datetime.min.time())
        hoje_ms  = int(hoje_dt.timestamp() * 1000)
        fig.add_shape(
            type="line", xref="x", yref="paper",
            x0=hoje_ms, x1=hoje_ms, y0=0, y1=1,
            line=dict(color="#e74c3c", width=2, dash="dot"),
        )
        fig.add_annotation(
            xref="x", yref="paper",
            x=hoje_ms, y=1.04,
            text="<b>Hoje</b>", showarrow=False,
            font=dict(color="#e74c3c", size=11),
            xanchor="center",
        )

        # Legenda manual com traces invisíveis
        for lbl, cor in [("Preparativo","#2657A0"),("Durante","#1E8A5A"),("Desmob.","#E8A020")]:
            fig.add_trace(go.Bar(
                name=lbl, x=[None], y=[None], orientation="h",
                marker=dict(color=cor), showlegend=True,
            ))

        fig.update_layout(
            barmode="overlay",
            xaxis=dict(
                type="date", title="", gridcolor="#EFF2F8",
                tickformat="%b %Y", tickfont=dict(size=11),
            ),
            yaxis=dict(
                title="", autorange="reversed",
                tickfont=dict(size=12, color="#1B3A5C"),
                gridcolor="#EFF2F8",
            ),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.06,
                xanchor="left", x=0,
                font=dict(size=12), bgcolor="rgba(0,0,0,0)",
            ),
            height=max(300, len(com_data)*50+100),
            margin=dict(l=0, r=10, t=40, b=20),
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="DM Sans, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True)

    except ImportError:
        st.info("Instale plotly para o Gantt visual.")
        df = pd.DataFrame([{
            "Projeto":p["nome"],
            "Início":iso_br(p.get("inicioDurante")),
            "Fim":iso_br(p.get("fimDurante")),
            "Atrasos":p["_atr"],
            "Concluídas":f'{p["_conc"]}/{p["_total"]}',
        } for p in com_data])
        st.dataframe(df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# ROTEADOR
# ─────────────────────────────────────────────
def main():
    tela = st.session_state.tela

    if tela == "login" or not st.session_state.token:
        tela_login()
        return

    render_topbar()
    render_nav()
    st.markdown('<div style="padding:24px 28px 28px;">', unsafe_allow_html=True)

    if   tela == "painel":          tela_painel()
    elif tela == "detalhe_projeto": tela_detalhe_projeto()
    elif tela == "dashboard":       tela_dashboard()
    elif tela == "projetos"  and is_admin(): tela_projetos()
    elif tela == "tarefas"   and is_admin(): tela_tarefas()
    elif tela == "usuarios"  and is_admin(): tela_usuarios()
    else: ir("painel")

    st.markdown('</div>', unsafe_allow_html=True)

main()
