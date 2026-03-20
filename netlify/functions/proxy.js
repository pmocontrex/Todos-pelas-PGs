[build]
  functions = "netlify/functions"

# /api/* → função proxy (mantém query string e body)
[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/proxy"
  status = 200
  force = true
