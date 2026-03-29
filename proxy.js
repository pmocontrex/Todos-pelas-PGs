// netlify/functions/proxy.js
// Proxy reverso: recebe chamadas do browser e repassa ao Google Apps Script
// Isso elimina o erro de CORS porque o browser nunca fala diretamente com o Google

const GAS_URL = 'https://script.google.com/macros/s/AKfycbz8X7d-1IiKzJqavRNE8-Yns4qzNnI_UmPiS9oZyDcZMxPmOR_DJaiu5OpBGHMKnC_J/exec';

exports.handler = async (event) => {
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  // Responde ao preflight OPTIONS imediatamente — sem isso o browser bloqueia tudo
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: corsHeaders, body: '' };
  }

  try {
    // Repassa query string para o GAS (ex: ?path=login)
    const qs = event.rawQuery ? '?' + event.rawQuery : '';

    const fetchOptions = {
      method: event.httpMethod,
      headers: { 'Content-Type': 'application/json' },
      redirect: 'follow'
    };

    if (event.httpMethod === 'POST' && event.body) {
      fetchOptions.body = event.body;
    }

    const response = await fetch(GAS_URL + qs, fetchOptions);
    const text = await response.text();

    return {
      statusCode: 200,
      headers: corsHeaders,
      body: text
    };
  } catch (err) {
    return {
      statusCode: 500,
      headers: corsHeaders,
      body: JSON.stringify({ success: false, error: 'Proxy error: ' + err.message })
    };
  }
};
