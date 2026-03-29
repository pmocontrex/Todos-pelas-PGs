"""
app.py — Projex no Streamlit Cloud
Chama o Google Apps Script diretamente (sem proxy).
Corrige o 'Invalid base URL' que ocorre dentro do iframe sandboxed do Streamlit:
  - API_BASE_URL vira a URL absoluta do GAS
  - new URL(base, origin) é substituído por new URL(base) — funciona com URL absoluta
"""

import streamlit as st
import streamlit.components.v1 as components

GAS_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbwVlPv_dhreFVkbSSTePo7dqAxVbVD_ep8bFeLCsR_Spioko7xACyfURsZRAguWCYNe/exec"
)

st.set_page_config(layout="wide", page_title="Projex")

st.markdown(
    """
    <style>
        .block-container { padding: 0 !important; max-width: 100% !important; }
        #MainMenu, footer, header { visibility: hidden; }
        iframe { border: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Fix 1: aponta API_BASE_URL para o GAS diretamente
html_patched = html_content.replace(
    "const API_BASE_URL = '/api/proxy';",
    f"const API_BASE_URL = '{GAS_URL}';",
)

# Fix 2: dentro do iframe do Streamlit, window.location.origin é "null"
# então new URL(base, "null") lança "Invalid base URL".
# Como API_BASE_URL agora é absoluta, basta usar new URL(base) sem o segundo argumento.
html_patched = html_patched.replace(
    "const url = new URL(API_BASE_URL, window.location.origin);",
    "const url = new URL(API_BASE_URL);",
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
    function resize() {{
      const h = Math.max(
        document.body.scrollHeight,
        document.documentElement.scrollHeight
      ) + 20;
      window.parent.postMessage({{ type: 'iframe-resize', height: h }}, '*');
    }}
    window.addEventListener('load', resize);
    window.addEventListener('resize', resize);
    new MutationObserver(resize).observe(document.body, {{
      subtree: true, childList: true, attributes: true
    }});
    setTimeout(resize, 500);
    setTimeout(resize, 1500);
  </script>
</body>
</html>"""

components.html(html_final, height=3000, scrolling=True)
