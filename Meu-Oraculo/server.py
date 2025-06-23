from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

# Pegando a chave da API do ambiente
API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-pro:generateContent?key={API_KEY}"

@app.route("/api/intel", methods=["POST"])
def obter_inteligencia():
    data = request.get_json()
    produto = data.get("produto", "").strip()

    if not produto:
        return jsonify({"erro": "Produto não informado"}), 400

    # Prompt estruturado em JSON entre tags para facilitar o parse
    prompt = f'''
<json>
{{
  "nome": "{produto}",
  "categoria": "Desconhecido",
  "ingrediente_ativo": "Desconhecido",
  "info": "Desconhecido",
  "culturas": [],
  "alvos": []
}}
</json>

Agora substitua os valores por informações reais sobre o produto agrícola "{produto}".
Responda SOMENTE com o JSON entre as tags <json></json>.
'''

    payload = {
        "contents": [{
            "role": "user",
            "parts": [{ "text": prompt }]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    try:
        resp = requests.post(API_URL, json=payload)
        resp.raise_for_status()
        result = resp.json()

        # Pega o conteúdo retornado
        text = result['candidates'][0]['content']['parts'][0]['text']
        print("Resposta da IA:", text)  # log útil para debug

        if "<json>" in text:
            raw_json = text.split("<json>")[1].split("</json>")[0].strip()
            return jsonify(json.loads(raw_json))

        return jsonify({"erro": "Resposta fora do padrão", "resposta": text}), 422

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
