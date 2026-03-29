import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

html_final = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }}
    </style>
</head>
<body>
    {html_content}
    <script>
        function resize() {{
            window.parent.postMessage({{
                type: 'iframe-resize',
                height: document.body.scrollHeight + 20
            }}, '*');
        }}
        window.addEventListener('load', resize);
        window.addEventListener('resize', resize);
        setTimeout(resize, 500);
    </script>
</body>
</html>
"""

components.html(html_final, height=2000, scrolling=False)
