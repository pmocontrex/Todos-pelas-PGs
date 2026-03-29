"""
app.py — Projex no Streamlit
Sobe um proxy FastAPI em thread separada para resolver o CORS com o Google Apps Script.
O index.html chama /api/proxy?path=... e o proxy repassa ao GAS transparentemente.
"""

import threading
import uvicorn
import httpx
import streamlit as st
import streamlit.components.v1 as components
from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

# ── Configuração ─────────────────────────────────────────────────────────────
GAS_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbwVlPv_dhreFVkbSSTePo7dqAxVbVD_ep8bFeLCsR_Spioko7xACyfURsZRAguWCYNe/exec"
)
PROXY_PORT = 8501  # porta interna do proxy (diferente do Streamlit que usa 8501 externamente)
# Streamlit Cloud expõe apenas a porta 8501 ao exterior, mas internamente podemos usar outra.
# Usamos 8502 para o FastAPI rodar em paralelo sem conflito.
PROXY_PORT = 8502

# ── FastAPI proxy ─────────────────────────────────────────────────────────────
proxy_app = FastAPI()

proxy_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@proxy_app.api_route("/api/proxy", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy(request: Request):
    """Recebe chamadas do browser e repassa ao Google Apps Script."""
    qs = str(request.url.query)
    target = GAS_URL + ("?" + qs if qs else "")

    body = await request.body()
    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        resp = await client.request(
            method=request.method if request.method != "OPTIONS" else "GET",
            url=target,
            content=body or None,
            headers=headers,
        )

    return Response(
        content=resp.content,
        status_code=200,
        media_type="application/json",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        },
    )


def _start_proxy():
    """Inicia o FastAPI em thread daemon (não bloqueia o Streamlit)."""
    uvicorn.run(proxy_app, host="0.0.0.0", port=PROXY_PORT, log_level="error")


# Garante que o proxy sobe apenas uma vez (Streamlit re-executa o script a cada interação)
if "proxy_started" not in st.session_state:
    t = threading.Thread(target=_start_proxy, daemon=True)
    t.start()
    st.session_state["proxy_started"] = True

# ── Streamlit UI ──────────────────────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="Projex")

# Remove padding padrão do Streamlit para o HTML ocupar 100% da largura
st.markdown(
    """
    <style>
        /* Remove margens e padding do Streamlit */
        .block-container { padding: 0 !important; max-width: 100% !important; }
        #MainMenu, footer, header { visibility: hidden; }
        iframe { border: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Injeta o script que aponta API_BASE_URL para o proxy local antes de qualquer outro JS
# Isso sobrescreve a constante declarada no index.html sem precisar editar o arquivo
proxy_override = f"""
<script>
  // Aponta chamadas de API para o proxy FastAPI interno
  // (sobrescreve API_BASE_URL antes do restante do script carregar)
  window.__PROXY_PORT__ = {PROXY_PORT};
</script>
"""

# Insere o override logo após o <head> e reescreve API_BASE_URL via substituição de string
# A linha original no index.html é: const API_BASE_URL = '/api/proxy';
# Precisamos que ela aponte para http://localhost:8502/api/proxy
html_patched = html_content.replace(
    "const API_BASE_URL = '/api/proxy';",
    f"const API_BASE_URL = 'http://localhost:{PROXY_PORT}/api/proxy';",
)

html_final = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{ margin: 0; padding: 0; overflow-x: hidden; }}
  </style>
</head>
<body>
  {html_patched}
  <script>
    // Redimensionamento dinâmico do iframe
    function resize() {{
      const h = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight) + 20;
      window.parent.postMessage({{ type: 'iframe-resize', height: h }}, '*');
    }}
    window.addEventListener('load', resize);
    window.addEventListener('resize', resize);
    new MutationObserver(resize).observe(document.body, {{ subtree: true, childList: true }});
    setTimeout(resize, 500);
    setTimeout(resize, 1500);
  </script>
</body>
</html>"""

components.html(html_final, height=3000, scrolling=True)
