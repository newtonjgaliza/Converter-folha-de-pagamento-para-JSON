from flask import Flask, request, jsonify

# Cria a aplicação Flask
app = Flask(__name__)

# Rota principal
@app.route('/', methods=['GET', 'POST'])
def main():
    return jsonify({"status": "running", "message": "Flask app working on Vercel"})

# Exportação OBRIGATÓRIA para o Vercel
handler = app
