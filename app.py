"""
Projex — Sistema de Controle de Projetos
Conversão completa para Streamlit (backend: Google Apps Script)
"""

import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime, timedelta
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
# CSS GLOBAL
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Remove padding padrão */
.block-container { padding-top: 0 !important; padding-bottom: 1rem !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }

/* Topbar */
.topbar {
    background: linear-gradient(90deg, #1B3A5C 0%, #2657a0 100%);
    color: white;
    padding: 12px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -1rem -1rem 1.5rem -1rem;
    box-shadow: 0 2px 12px rgba(27,58,92,0.2);
}
.topbar-title { font-family: 'DM Serif Display', serif; font-size: 22px; letter-spacing: -0.3px; }
.topbar-user { font-size: 13px; opacity: 0.8; }

/* Cards de projeto */
.proj-card {
    background: white;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 12px;
    border: 1px solid #E2E6F0;
    box-shadow: 0 1px 4px rgba(27,58,92,0.07);
    cursor: pointer;
    transition: box-shadow 0.15s;
}
.proj-card:hover { box-shadow: 0 4px 16px rgba(27,58,92,0.13); }
.proj-card h4 { color: #1B3A5C; margin: 0 0 6px 0; font-size: 15px; }
.proj-card p { color: #5A6478; font-size: 13px; margin: 2px 0; }

/* Badge atraso */
.badge-atraso {
    display: inline-block;
    background: #FDF0F0;
    color: #D94545;
    border: 1px solid #f5c6c6;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 10px;
    margin-top: 6px;
}

/* Progress bar */
.prog-wrap { background: #E2E6F0; border-radius: 99px; height: 6px; margin: 8px 0 4px; }
.prog-fill { height: 6px; border-radius: 99px; background: #1E8A5A; transition: width 0.3s; }
.prog-fill.red { background: #D94545; }
.prog-fill.yellow { background: #E8A020; }

/* Status badges */
.st-badge {
    display: inline-block;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 10px;
}
.st-nao { background:#F0F2F8; color:#5A6478; }
.st-and { background:#EBF1FB; color:#2657a0; }
.st-conc { background:#EBF8F2; color:#1E8A5A; }
.st-atr { background:#FDF0F0; color:#D94545; }

/* Dashboard cards */
.dash-card {
    background: white;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    border: 1px solid #E2E6F0;
    box-shadow: 0 1px 4px rgba(27,58,92,0.07);
}
.dash-card .num { font-size: 36px; font-weight: 700; margin: 0; }
.dash-card .lbl { font-size: 13px; color: #5A6478; margin: 0; }

/* Formulários */
div[data-testid="stForm"] { background: white; padding: 20px; border-radius: 12px; border: 1px solid #E2E6F0; }

/* Tabelas */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* Botões */
.stButton > button {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
}

/* Mobile */
@media (max-width: 768px) {
    .block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    .topbar { padding: 10px 14px; }
    .topbar-title { font-size: 18px; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
for k, v in {
    "token": None,
    "usuario": None,
    "tela": "login",
    "projeto_selecionado": None,
    "tarefa_editando": None,
    "projeto_editando": None,
    "usuario_editando": None,
    "msg_sucesso": None,
    "msg_erro": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# API — todas as chamadas passam pelo Python
# (sem CORS pois é server-side)
# ─────────────────────────────────────────────
def api(path, method="GET", data=None):
    params = {"path": path, "_method": method}
    if st.session_state.token:
        params["token"] = st.session_state.token
    if method == "GET" and data:
        params.update(data)

    payload = {"_method": method}
    if st.session_state.token:
        payload["token"] = st.session_state.token
    if data:
        payload.update(data)

    try:
        resp = requests.post(
            GAS_URL,
            params={"path": path},
            json=payload,
            timeout=30,
            allow_redirects=True,
        )
        result = resp.json()
        if not result.get("success"):
            raise Exception(result.get("error", "Erro desconhecido"))
        return result.get("data")
    except requests.exceptions.Timeout:
        raise Exception("Tempo de conexão esgotado. Tente novamente.")
    except Exception as e:
        raise e

# ─────────────────────────────────────────────
# UTILITÁRIOS
# ─────────────────────────────────────────────
def iso_br(iso):
    if not iso or iso == "—":
        return "—"
    try:
        p = iso.split("-")
        return f"{p[2]}/{p[1]}/{p[0]}"
    except:
        return iso

def br_iso(br):
    if not br:
        return ""
    p = br.split("/")
    if len(p) == 3:
        return f"{p[2]}-{p[1]}-{p[0]}"
    return br

def parse_iso(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except:
        return None

def hoje():
    return date.today()

def badge_status(s, sin=""):
    cls = {"Não iniciada": "st-nao", "Em andamento": "st-and", "Concluída": "st-conc"}.get(s, "st-nao")
    if sin == "Atrasada":
        return f'<span class="st-badge st-atr">⚠ Atrasada</span>'
    return f'<span class="st-badge {cls}">{s}</span>'

def sucesso(msg):
    st.session_state.msg_sucesso = msg

def erro(msg):
    st.session_state.msg_erro = msg

def mostrar_msgs():
    if st.session_state.msg_sucesso:
        st.success(st.session_state.msg_sucesso)
        st.session_state.msg_sucesso = None
    if st.session_state.msg_erro:
        st.error(st.session_state.msg_erro)
        st.session_state.msg_erro = None

def ir(tela, **kwargs):
    st.session_state.tela = tela
    for k, v in kwargs.items():
        st.session_state[k] = v
    st.rerun()

def is_admin():
    return st.session_state.usuario and st.session_state.usuario.get("nivel") == "Administrador"

# ─────────────────────────────────────────────
# TOPBAR
# ─────────────────────────────────────────────
def render_topbar():
    u = st.session_state.usuario
    nome = u.get("nome", "") if u else ""
    nivel = u.get("nivel", "") if u else ""
    st.markdown(f"""
    <div class="topbar">
        <span class="topbar-title">📋 Projex</span>
        <span class="topbar-user">👤 {nome} &nbsp;·&nbsp; {nivel}</span>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# NAVEGAÇÃO
# ─────────────────────────────────────────────
def render_nav():
    cols = st.columns([2, 2, 2, 2, 2, 1] if is_admin() else [3, 3, 3, 1])
    telas = [("📊 Painel", "painel"), ("📁 Projetos", "projetos"), ("📈 Dashboard", "dashboard")]
    if is_admin():
        telas.insert(2, ("✅ Tarefas", "tarefas"))
        telas.insert(4, ("👤 Usuários", "usuarios"))

    for i, (label, tela) in enumerate(telas):
        with cols[i]:
            if st.button(label, use_container_width=True,
                         type="primary" if st.session_state.tela == tela else "secondary"):
                ir(tela)
    with cols[-1]:
        if st.button("Sair", use_container_width=True):
            for k in ["token", "usuario", "projeto_selecionado"]:
                st.session_state[k] = None
            ir("login")

# ─────────────────────────────────────────────
# TELA: LOGIN
# ─────────────────────────────────────────────
def tela_login():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("""
        <div style='text-align:center; padding: 40px 0 20px;'>
            <div style='font-family:"DM Serif Display",serif; font-size:36px; color:#1B3A5C; margin-bottom:4px;'>📋 Projex</div>
            <div style='color:#5A6478; font-size:14px;'>Controle de Projetos</div>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("#### Entrar")
            login = st.text_input("Usuário", placeholder="seu.login")
            senha = st.text_input("Senha", type="password", placeholder="••••••")

            if st.button("Entrar", type="primary", use_container_width=True):
                if not login or not senha:
                    st.error("Preencha usuário e senha.")
                else:
                    with st.spinner("Autenticando..."):
                        try:
                            data = api("login", "POST", {"login": login, "senha": senha})
                            st.session_state.token = data["token"]
                            st.session_state.usuario = data["usuario"]
                            ir("painel")
                        except Exception as e:
                            st.error(f"Erro: {e}")

# ─────────────────────────────────────────────
# TELA: PAINEL (visão geral de projetos)
# ─────────────────────────────────────────────
def tela_painel():
    mostrar_msgs()
    st.markdown("### 📊 Visão Geral de Projetos")

    with st.spinner("Carregando projetos..."):
        try:
            projetos = api("projetos", "GET") or []
            tarefas = api("tarefas", "GET") or []
        except Exception as e:
            st.error(f"Erro: {e}")
            return

    # Mapa tarefas por projeto
    tp = {}
    for t in tarefas:
        tp.setdefault(t["projeto"], []).append(t)

    hoje_d = hoje()
    for p in projetos:
        arr = tp.get(p["nome"], [])
        total = len(arr)
        conc = sum(1 for t in arr if t["status"] == "Concluída")
        atr = sum(1 for t in arr if t.get("sinalizador") == "Atrasada")
        p["_total"] = total
        p["_conc"] = conc
        p["_atr"] = atr
        p["_perc"] = round((conc / total) * 100) if total > 0 else 0
        p["_concluido"] = total > 0 and conc == total

    # Filtros
    with st.expander("🔍 Filtros", expanded=False):
        c1, c2, c3 = st.columns(3)
        nomes = ["Todos"] + [p["nome"] for p in projetos]
        filtro_nome = c1.selectbox("Projeto", nomes, key="f_nome")
        tipos = ["Todos", "PG", "Rotina", "Projeto"]
        filtro_tipo = c2.selectbox("Tipo", tipos, key="f_tipo")
        ordem = c3.selectbox("Ordenar por", ["Nome", "Data Durante"], key="f_ordem")
        c4, c5 = st.columns(2)
        so_atraso = c4.checkbox("Somente com atrasos", key="f_atr")
        ocultar_conc = c5.checkbox("Ocultar concluídos", key="f_conc")

    lista = projetos[:]
    if filtro_nome != "Todos":
        lista = [p for p in lista if p["nome"] == filtro_nome]
    if filtro_tipo != "Todos":
        lista = [p for p in lista if p.get("tipo") == filtro_tipo]
    if so_atraso:
        lista = [p for p in lista if p["_atr"] > 0]
    if ocultar_conc:
        lista = [p for p in lista if not p["_concluido"]]

    if ordem == "Data Durante":
        lista.sort(key=lambda p: parse_iso(p.get("inicioDurante")) or date(9999, 1, 1))
    else:
        lista.sort(key=lambda p: p["nome"])

    if not lista:
        st.info("Nenhum projeto encontrado.")
        return

    # Grade de cards (2 por linha no desktop, 1 no mobile)
    cols_per_row = 2
    for i in range(0, len(lista), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, p in enumerate(lista[i:i + cols_per_row]):
            with cols[j]:
                perc = p["_perc"]
                cor_cls = "red" if p["_atr"] > 0 else ("" if perc >= 100 else "yellow" if perc >= 50 else "")
                durante = (
                    f"Durante: {iso_br(p.get('inicioDurante'))} — {iso_br(p.get('fimDurante'))}"
                    if p.get("inicioDurante") and p.get("fimDurante") else "—"
                )
                badge = f'<span class="badge-atraso">⚠ {p["_atr"]} em atraso</span>' if p["_atr"] > 0 else ""
                prog_cor = "red" if p["_atr"] > 0 else ("" if perc < 50 else "yellow" if perc < 100 else "")

                st.markdown(f"""
                <div class="proj-card">
                    <h4>{p['nome']}</h4>
                    <p><strong>Cliente:</strong> {p.get('cliente') or '—'} &nbsp;|&nbsp;
                       <strong>Tipo:</strong> {p.get('tipo','—')} &nbsp;|&nbsp;
                       <strong>Unidade:</strong> {p.get('unidade') or '—'}</p>
                    <p>{durante}</p>
                    {badge}
                    <div class="prog-wrap"><div class="prog-fill {prog_cor}" style="width:{perc}%"></div></div>
                    <p style="font-size:12px;color:#888;">{perc}% concluído ({p['_conc']}/{p['_total']} tarefas)</p>
                </div>
                """, unsafe_allow_html=True)

                if st.button("Ver tarefas", key=f"card_{p['nome']}", use_container_width=True):
                    ir("detalhe_projeto", projeto_selecionado=p["nome"])

# ─────────────────────────────────────────────
# TELA: DETALHE PROJETO (tarefas do usuário)
# ─────────────────────────────────────────────
def tela_detalhe_projeto():
    mostrar_msgs()
    nome = st.session_state.projeto_selecionado

    if st.button("← Voltar ao Painel"):
        ir("painel")

    st.markdown(f"### 📁 {nome}")

    with st.spinner("Carregando tarefas..."):
        try:
            tarefas = api("tarefas", "GET", {"projeto": nome}) or []
        except Exception as e:
            st.error(f"Erro: {e}")
            return

    if not tarefas:
        st.info("Nenhuma tarefa neste projeto.")
        return

    # Filtros inline
    c1, c2 = st.columns(2)
    f_status = c1.selectbox("Status", ["Todos", "Não iniciada", "Em andamento", "Concluída"], key="dp_status")
    f_sin = c2.selectbox("Sinalizador", ["Todos", "Atrasada", "No prazo"], key="dp_sin")

    lista = tarefas[:]
    if f_status != "Todos":
        lista = [t for t in lista if t.get("status") == f_status]
    if f_sin != "Todos":
        lista = [t for t in lista if (t.get("sinalizador") == "Atrasada") == (f_sin == "Atrasada")]

    lista.sort(key=lambda t: parse_iso(t.get("prazo")) or date(9999, 1, 1))

    for t in lista:
        sin = t.get("sinalizador", "")
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"**{t.get('tarefa', '')}**")
                st.markdown(
                    f"Prazo: `{iso_br(t.get('prazo'))}` &nbsp;"
                    f"Anexo: `{t.get('anexoObrigatorio','—')}` &nbsp;"
                    f"{'⚠ **Atrasada**' if sin == 'Atrasada' else ''}",
                    unsafe_allow_html=False
                )
                st.markdown(badge_status(t.get("status", ""), sin), unsafe_allow_html=True)
            with c2:
                novo_status = st.selectbox(
                    "Status",
                    ["Não iniciada", "Em andamento", "Concluída"],
                    index=["Não iniciada", "Em andamento", "Concluída"].index(t.get("status", "Não iniciada")),
                    key=f"sel_{t['id']}",
                    label_visibility="collapsed"
                )
                if st.button("💾", key=f"save_{t['id']}", help="Salvar status"):
                    try:
                        api("tarefas", "PUT", {
                            "id": t["id"],
                            "status": novo_status,
                            "tarefa": t["tarefa"],
                            "projeto": t["projeto"],
                            "prazo": t.get("prazo", ""),
                            "centroCusto": t.get("centroCusto", ""),
                            "anexoObrigatorio": t.get("anexoObrigatorio", "Não"),
                        })
                        sucesso("Status atualizado!")
                        st.rerun()
                    except Exception as e:
                        erro(f"Erro: {e}")

# ─────────────────────────────────────────────
# TELA: PROJETOS (admin — CRUD)
# ─────────────────────────────────────────────
def tela_projetos():
    mostrar_msgs()
    st.markdown("### 📁 Gerenciar Projetos")

    with st.spinner("Carregando..."):
        try:
            projetos = api("projetos", "GET") or []
        except Exception as e:
            st.error(f"Erro: {e}")
            return

    # Botão novo projeto
    if st.button("＋ Novo Projeto", type="primary"):
        st.session_state.projeto_editando = {}
        st.rerun()

    # Formulário (novo ou editar)
    if st.session_state.projeto_editando is not None:
        p = st.session_state.projeto_editando
        is_novo = not p.get("id")
        st.markdown(f"#### {'Novo Projeto' if is_novo else 'Editar Projeto'}")

        with st.form("form_projeto"):
            nome = st.text_input("Nome *", value=p.get("nome", ""))
            c1, c2 = st.columns(2)
            tipo = c1.selectbox("Tipo", ["PG", "Rotina", "Projeto"],
                                index=["PG", "Rotina", "Projeto"].index(p.get("tipo", "PG")))
            cliente = c2.text_input("Cliente", value=p.get("cliente", ""))
            c3, c4 = st.columns(2)
            unidade = c3.text_input("Unidade", value=p.get("unidade", ""))
            centro = c4.text_input("Centro de Custo", value=str(p.get("centroCusto", "")))

            st.markdown("**Datas**")
            d1, d2, d3, d4 = st.columns(4)
            ini_prep = d1.date_input("Início Prep.", value=parse_iso(p.get("inicioPrep")) or None)
            ini_dur = d2.date_input("Início Durante", value=parse_iso(p.get("inicioDurante")) or None)
            fim_dur = d3.date_input("Fim Durante", value=parse_iso(p.get("fimDurante")) or None)
            fim_des = d4.date_input("Fim Desmob.", value=parse_iso(p.get("fimDesmob")) or None)

            c_salvar, c_cancelar = st.columns(2)
            salvar = c_salvar.form_submit_button("💾 Salvar", type="primary", use_container_width=True)
            cancelar = c_cancelar.form_submit_button("Cancelar", use_container_width=True)

        if salvar:
            if not nome:
                st.error("Nome obrigatório.")
            else:
                try:
                    api("projetos", "POST", {
                        "id": p.get("id"),
                        "nome": nome, "tipo": tipo, "cliente": cliente,
                        "unidade": unidade, "centroCusto": centro,
                        "inicioPrep": ini_prep.isoformat() if ini_prep else "",
                        "inicioDurante": ini_dur.isoformat() if ini_dur else "",
                        "fimDurante": fim_dur.isoformat() if fim_dur else "",
                        "fimDesmob": fim_des.isoformat() if fim_des else "",
                    })
                    st.session_state.projeto_editando = None
                    sucesso("Projeto salvo!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
        if cancelar:
            st.session_state.projeto_editando = None
            st.rerun()

    # Tabela de projetos
    if projetos:
        st.markdown("---")
        for p in sorted(projetos, key=lambda x: x.get("nome", "")):
            with st.container(border=True):
                c1, c2, c3 = st.columns([5, 1, 1])
                with c1:
                    st.markdown(f"**{p['nome']}** &nbsp; `{p.get('tipo','—')}` &nbsp; {p.get('cliente','—')}")
                    st.caption(
                        f"Unidade: {p.get('unidade','—')} | CC: {p.get('centroCusto','—')} | "
                        f"Durante: {iso_br(p.get('inicioDurante'))} — {iso_br(p.get('fimDurante'))}"
                    )
                with c2:
                    if st.button("✏️", key=f"edp_{p['id']}", help="Editar", use_container_width=True):
                        st.session_state.projeto_editando = p
                        st.rerun()
                with c3:
                    if st.button("🗑️", key=f"delp_{p['id']}", help="Excluir", use_container_width=True):
                        try:
                            api("projetos", "DELETE", {"id": p["id"]})
                            sucesso("Projeto excluído.")
                            st.rerun()
                        except Exception as e:
                            erro(f"Erro: {e}")
    else:
        st.info("Nenhum projeto cadastrado.")

# ─────────────────────────────────────────────
# TELA: TAREFAS (admin — CRUD + importação)
# ─────────────────────────────────────────────
def tela_tarefas():
    mostrar_msgs()
    st.markdown("### ✅ Gerenciar Tarefas")

    with st.spinner("Carregando..."):
        try:
            tarefas = api("tarefas", "GET") or []
            projetos = api("projetos", "GET") or []
        except Exception as e:
            st.error(f"Erro: {e}")
            return

    proj_map = {p["nome"]: p for p in projetos}
    proj_nomes = [p["nome"] for p in projetos]

    tab_lista, tab_nova, tab_import = st.tabs(["📋 Lista", "➕ Nova / Editar", "📥 Importar CSV"])

    # ── LISTA ──
    with tab_lista:
        f1, f2 = st.columns(2)
        f_proj = f1.selectbox("Projeto", ["Todos"] + proj_nomes, key="ft_proj")
        f_stat = f2.selectbox("Status", ["Todos", "Não iniciada", "Em andamento", "Concluída"], key="ft_stat")

        lista = tarefas[:]
        if f_proj != "Todos":
            lista = [t for t in lista if t.get("projeto") == f_proj]
        if f_stat != "Todos":
            lista = [t for t in lista if t.get("status") == f_stat]
        lista.sort(key=lambda t: parse_iso(t.get("prazo")) or date(9999, 1, 1))

        if not lista:
            st.info("Nenhuma tarefa.")
        else:
            for t in lista:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([5, 1, 1])
                    with c1:
                        st.markdown(f"**{t.get('tarefa','')}**  `{t.get('projeto','')}`")
                        st.caption(f"Prazo: {iso_br(t.get('prazo'))} | Status: {t.get('status')} | Anexo: {t.get('anexoObrigatorio','—')}")
                    with c2:
                        if st.button("✏️", key=f"et_{t['id']}", use_container_width=True):
                            st.session_state.tarefa_editando = t
                            st.rerun()
                    with c3:
                        if st.button("🗑️", key=f"dt_{t['id']}", use_container_width=True):
                            try:
                                api("tarefas", "DELETE", {"id": t["id"]})
                                sucesso("Tarefa excluída.")
                                st.rerun()
                            except Exception as e:
                                erro(f"Erro: {e}")

    # ── NOVA / EDITAR ──
    with tab_nova:
        t = st.session_state.tarefa_editando or {}
        is_nova = not t.get("id")
        st.markdown(f"#### {'Nova Tarefa' if is_nova else 'Editar Tarefa'}")

        if not is_nova:
            if st.button("✕ Limpar / Nova tarefa"):
                st.session_state.tarefa_editando = None
                st.rerun()

        with st.form("form_tarefa"):
            desc = st.text_input("Descrição *", value=t.get("tarefa", ""))
            c1, c2 = st.columns(2)
            proj_idx = proj_nomes.index(t["projeto"]) if t.get("projeto") in proj_nomes else 0
            proj_sel = c1.selectbox("Projeto *", proj_nomes, index=proj_idx)
            centro_auto = proj_map.get(proj_sel, {}).get("centroCusto", "")
            c2.text_input("Centro de Custo (auto)", value=str(centro_auto), disabled=True)

            c3, c4 = st.columns(2)
            prazo = c3.date_input("Prazo *", value=parse_iso(t.get("prazo")) or date.today())
            status = c4.selectbox("Status", ["Não iniciada", "Em andamento", "Concluída"],
                                  index=["Não iniciada", "Em andamento", "Concluída"].index(t.get("status", "Não iniciada")))
            anexo = st.selectbox("Anexo Obrigatório?", ["Não", "Sim"],
                                 index=0 if t.get("anexoObrigatorio", "Não") == "Não" else 1)

            salvar = st.form_submit_button("💾 Salvar", type="primary", use_container_width=True)

        if salvar:
            if not desc or not proj_sel:
                st.error("Descrição e Projeto são obrigatórios.")
            else:
                try:
                    api("tarefas", "POST", {
                        "id": t.get("id"),
                        "tarefa": desc, "projeto": proj_sel,
                        "centroCusto": str(centro_auto),
                        "prazo": prazo.isoformat(),
                        "status": status,
                        "anexoObrigatorio": anexo,
                    })
                    st.session_state.tarefa_editando = None
                    sucesso("Tarefa salva!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── IMPORTAR CSV ──
    with tab_import:
        st.markdown("**Colunas esperadas:** `Tarefa, Projeto, Prazo Conclusao, Anexo Obrigatorio`")

        # Baixar modelo
        modelo_csv = "Tarefa,Projeto,Prazo Conclusao,Anexo Obrigatorio\nExemplo de tarefa,Nome Exato do Projeto,2025-12-31,Não\n"
        st.download_button("📄 Baixar Modelo CSV", modelo_csv, "modelo_tarefas.csv", "text/csv")

        arq = st.file_uploader("Selecione o arquivo CSV", type=["csv"])
        if arq and st.button("✅ Importar", type="primary"):
            try:
                txt = arq.read().decode("utf-8-sig")
                linhas = [l.split(",") for l in txt.strip().split("\n")]
                cab = [c.strip().lower() for c in linhas[0]]
                iT = next(i for i, c in enumerate(cab) if "tarefa" in c)
                iP = next(i for i, c in enumerate(cab) if "projeto" in c)
                iPr = next(i for i, c in enumerate(cab) if "prazo" in c)
                iA = next((i for i, c in enumerate(cab) if "anexo" in c), -1)

                tarefas_ex = api("tarefas", "GET") or []
                ex_set = {(t["tarefa"].lower(), t["projeto"].lower()) for t in tarefas_ex}

                importar, erros, ignoradas = [], [], []
                for i, l in enumerate(linhas[1:], 2):
                    if not any(c.strip() for c in l):
                        continue
                    desc = l[iT].strip() if iT < len(l) else ""
                    proj = l[iP].strip() if iP < len(l) else ""
                    prazo = l[iPr].strip() if iPr < len(l) else ""
                    anexo = l[iA].strip() if iA >= 0 and iA < len(l) else "Não"
                    if not desc or not proj or not prazo:
                        erros.append(f"Linha {i}: campos vazios.")
                        continue
                    if proj.lower() not in {k.lower() for k in proj_map}:
                        erros.append(f"Linha {i}: projeto '{proj}' não cadastrado.")
                        continue
                    if (desc.lower(), proj.lower()) in ex_set:
                        ignoradas.append(f"Linha {i}: '{desc}' já existe (ignorada).")
                        continue
                    nome_proj = next(k for k in proj_map if k.lower() == proj.lower())
                    importar.append({
                        "tarefa": desc, "projeto": nome_proj,
                        "centroCusto": str(proj_map[nome_proj].get("centroCusto", "")),
                        "prazo": prazo, "status": "Não iniciada",
                        "anexoObrigatorio": anexo or "Não"
                    })

                if erros:
                    for e in erros:
                        st.error(e)
                elif not importar:
                    st.warning("Nenhuma tarefa nova para importar.")
                    for ig in ignoradas:
                        st.caption(ig)
                else:
                    csv_body = "Tarefa,Projeto,CentroCusto,Prazo,Status,Anexo Obrigatorio\n"
                    csv_body += "\n".join(
                        f"{t['tarefa']},{t['projeto']},{t['centroCusto']},{t['prazo']},{t['status']},{t['anexoObrigatorio']}"
                        for t in importar
                    )
                    api("importar-tarefas", "POST", {"csv": csv_body})
                    st.success(f"✅ {len(importar)} tarefa(s) importada(s)!")
                    for ig in ignoradas:
                        st.caption(ig)
                    st.rerun()
            except StopIteration:
                st.error("Cabeçalho inválido. Use o modelo fornecido.")
            except Exception as e:
                st.error(f"Erro: {e}")

# ─────────────────────────────────────────────
# TELA: USUÁRIOS (admin)
# ─────────────────────────────────────────────
def tela_usuarios():
    mostrar_msgs()
    st.markdown("### 👤 Gerenciar Usuários")

    with st.spinner("Carregando..."):
        try:
            usuarios = api("usuarios", "GET") or []
            acessos = api("acessos", "GET") or []
            projetos = api("projetos", "GET") or []
        except Exception as e:
            st.error(f"Erro: {e}")
            return

    proj_nomes = [p["nome"] for p in projetos]
    amap = {}
    for a in acessos:
        amap.setdefault(a["login"], []).append(a["projeto"])

    if st.button("＋ Novo Usuário", type="primary"):
        st.session_state.usuario_editando = {}
        st.rerun()

    # Formulário
    if st.session_state.usuario_editando is not None:
        u = st.session_state.usuario_editando
        is_novo = not u.get("login")
        st.markdown(f"#### {'Novo Usuário' if is_novo else 'Editar Usuário'}")

        with st.form("form_usuario"):
            nome = st.text_input("Nome *", value=u.get("nome", ""))
            login_val = st.text_input("Login *", value=u.get("login", ""), disabled=not is_novo)
            senha = st.text_input("Senha" + (" *" if is_novo else " (deixe em branco para manter)"), type="password")
            nivel = st.selectbox("Nível", ["Usuario", "Administrador"],
                                 index=0 if u.get("nivel", "Usuario") == "Usuario" else 1)

            acs_sel = []
            if nivel == "Usuario":
                st.markdown("**Projetos com Acesso**")
                acs_atuais = amap.get(u.get("login", ""), [])
                acs_sel = st.multiselect("Selecione os projetos", proj_nomes, default=acs_atuais)

            c1, c2 = st.columns(2)
            salvar = c1.form_submit_button("💾 Salvar", type="primary", use_container_width=True)
            cancelar = c2.form_submit_button("Cancelar", use_container_width=True)

        if salvar:
            if not nome or not (login_val or u.get("login")):
                st.error("Nome e Login são obrigatórios.")
            elif is_novo and not senha:
                st.error("Senha obrigatória para novo usuário.")
            else:
                try:
                    api("usuarios", "POST", {
                        "nome": nome,
                        "login": login_val or u.get("login"),
                        "senha": senha,
                        "nivel": nivel,
                    })
                    api("acessos", "POST", {
                        "login": login_val or u.get("login"),
                        "projetos": ",".join(acs_sel) if nivel == "Usuario" else "",
                    })
                    st.session_state.usuario_editando = None
                    sucesso("Usuário salvo!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
        if cancelar:
            st.session_state.usuario_editando = None
            st.rerun()

    # Lista de usuários
    st.markdown("---")
    for u in usuarios:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 1, 1])
            with c1:
                projs = "Todos (Admin)" if u.get("nivel") == "Administrador" \
                    else (", ".join(amap.get(u["login"], [])) or "Nenhum")
                st.markdown(f"**{u['nome']}** &nbsp; `{u['login']}` &nbsp; `{u.get('nivel','—')}`")
                st.caption(f"Projetos: {projs}")
            with c2:
                if st.button("✏️", key=f"eu_{u['login']}", use_container_width=True):
                    st.session_state.usuario_editando = u
                    st.rerun()
            with c3:
                if st.button("🗑️", key=f"du_{u['login']}", use_container_width=True):
                    try:
                        api("usuarios", "DELETE", {"login": u["login"]})
                        sucesso("Usuário excluído.")
                        st.rerun()
                    except Exception as e:
                        erro(f"Erro: {e}")

# ─────────────────────────────────────────────
# TELA: DASHBOARD + GANTT
# ─────────────────────────────────────────────
def tela_dashboard():
    mostrar_msgs()
    st.markdown("### 📈 Painel Geral")

    with st.spinner("Carregando dados..."):
        try:
            projetos = api("todos-projetos", "GET") or []
            tarefas = api("todas-tarefas", "GET") or []
            acessos = api("acessos", "GET") or []
        except Exception as e:
            st.error(f"Erro: {e}")
            return

    usuario_login = st.session_state.usuario.get("login", "")
    meus_proj = {a["projeto"] for a in acessos if a["login"] == usuario_login}

    tp = {}
    for t in tarefas:
        tp.setdefault(t["projeto"], []).append(t)

    for p in projetos:
        arr = tp.get(p["nome"], [])
        total = len(arr)
        conc = sum(1 for t in arr if t["status"] == "Concluída")
        atr = sum(1 for t in arr if t.get("sinalizador") == "Atrasada")
        p["_total"] = total
        p["_conc"] = conc
        p["_atr"] = atr
        p["_concluido"] = total > 0 and conc == total

    # Filtros
    with st.expander("🔍 Filtros", expanded=False):
        c1, c2, c3 = st.columns(3)
        proj_nomes = ["Todos"] + [p["nome"] for p in projetos]
        f_proj = c1.selectbox("Projeto", proj_nomes, key="db_proj")
        f_meus = c2.checkbox("Somente meus projetos", key="db_meus")
        f_oconc = c3.checkbox("Ocultar concluídos", key="db_oconc")

    lista = projetos[:]
    if f_proj != "Todos":
        lista = [p for p in lista if p["nome"] == f_proj]
    if f_meus:
        lista = [p for p in lista if p["nome"] in meus_proj]
    if f_oconc:
        lista = [p for p in lista if not p["_concluido"]]

    tarefas_vis = [t for t in tarefas if any(p["nome"] == t["projeto"] for p in lista)]

    # Cards de resumo
    n_nao = sum(1 for t in tarefas_vis if t.get("status") == "Não iniciada")
    n_atr = sum(1 for t in tarefas_vis if t.get("sinalizador") == "Atrasada")
    n_and = sum(1 for t in tarefas_vis if t.get("status") == "Em andamento")
    n_conc = sum(1 for t in tarefas_vis if t.get("status") == "Concluída")

    c1, c2, c3, c4 = st.columns(4)
    for col, num, lbl, cor in [
        (c1, n_nao, "Não Iniciadas", "#5A6478"),
        (c2, n_atr, "Em Atraso", "#D94545"),
        (c3, n_and, "Em Andamento", "#2657a0"),
        (c4, n_conc, "Concluídas", "#1E8A5A"),
    ]:
        col.markdown(f"""
        <div class="dash-card">
            <p class="num" style="color:{cor};">{num}</p>
            <p class="lbl">{lbl}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Gantt com Plotly (mobile-friendly)
    projetos_com_data = [p for p in lista if p.get("inicioDurante") or p.get("inicioPrep")]
    if not projetos_com_data:
        st.info("Nenhum projeto com datas para exibir no Gantt.")
        return

    st.markdown("#### 📅 Gantt de Projetos")
    try:
        import plotly.graph_objects as go

        gantt_rows = []
        for p in projetos_com_data:
            nome = p["nome"]
            fases = []
            if p.get("inicioPrep") and p.get("inicioDurante"):
                fases.append(("Preparativo", p["inicioPrep"], p["inicioDurante"], "#3498db"))
            if p.get("inicioDurante") and p.get("fimDurante"):
                fases.append(("Durante", p["inicioDurante"], p["fimDurante"], "#27ae60"))
            if p.get("fimDurante") and p.get("fimDesmob"):
                fases.append(("Desmob.", p["fimDurante"], p["fimDesmob"], "#e67e22"))
            for fase, ini, fim, cor in fases:
                gantt_rows.append(dict(
                    Task=nome, Start=ini, Finish=fim, Fase=fase, Cor=cor
                ))

        if not gantt_rows:
            st.info("Projetos sem datas completas para o Gantt.")
            return

        fig = go.Figure()
        for row in gantt_rows:
            fig.add_trace(go.Bar(
                name=row["Fase"],
                y=[row["Task"]],
                x=[(datetime.strptime(row["Finish"], "%Y-%m-%d") -
                    datetime.strptime(row["Start"], "%Y-%m-%d")).days],
                base=[row["Start"]],
                orientation="h",
                marker_color=row["Cor"],
                hovertemplate=f"<b>{row['Task']}</b><br>{row['Fase']}: {iso_br(row['Start'])} → {iso_br(row['Finish'])}<extra></extra>",
            ))

        # Linha de hoje
        hoje_str = hoje().isoformat()
        fig.add_vline(x=hoje_str, line_color="#e74c3c", line_width=2, annotation_text="Hoje",
                      annotation_font_color="#e74c3c")

        fig.update_layout(
            barmode="overlay",
            xaxis=dict(type="date", title=""),
            yaxis=dict(title="", autorange="reversed"),
            height=max(250, len(projetos_com_data) * 50),
            margin=dict(l=0, r=0, t=20, b=20),
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)

    except ImportError:
        # Fallback sem plotly: tabela simples
        st.info("Instale plotly para ver o Gantt visual.")
        rows = []
        for p in projetos_com_data:
            rows.append({
                "Projeto": p["nome"],
                "Início Prep.": iso_br(p.get("inicioPrep")),
                "Início Durante": iso_br(p.get("inicioDurante")),
                "Fim Durante": iso_br(p.get("fimDurante")),
                "Fim Desmob.": iso_br(p.get("fimDesmob")),
                "Concluído": "✅" if p["_concluido"] else f"{p['_atr']} atraso(s)",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# ROTEADOR PRINCIPAL
# ─────────────────────────────────────────────
def main():
    tela = st.session_state.tela

    if tela == "login" or not st.session_state.token:
        tela_login()
        return

    render_topbar()
    render_nav()
    st.markdown("---")

    if tela == "painel":
        tela_painel()
    elif tela == "detalhe_projeto":
        tela_detalhe_projeto()
    elif tela == "projetos":
        tela_projetos()
    elif tela == "tarefas":
        if is_admin():
            tela_tarefas()
        else:
            ir("painel")
    elif tela == "usuarios":
        if is_admin():
            tela_usuarios()
        else:
            ir("painel")
    elif tela == "dashboard":
        tela_dashboard()

main()
