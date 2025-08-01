import os
import fitz  # PyMuPDF
import re
import json
import tempfile
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)

# Função de extração dos dados do PDF
def extrair_dados_pdf(pdf_file):
    try:
        # Resetar o cursor do arquivo para o início
        pdf_file.seek(0)
        # Usar BytesIO para trabalhar com o arquivo em memória
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        
        doc.close()

        def buscar(campo, padrao):
            match = re.search(padrao, text, re.IGNORECASE)
            return match.group(1).strip() if match else None

        empregado = buscar("Empregado", r"Empregado\s+([^\n]+)")
        matricula = nome = None
        if empregado:
            partes = empregado.strip().split(" ", 1)
            if len(partes) == 2:
                matricula, nome = partes

        dados = {
            "Competência": buscar("Competência", r"Competência\s+([\w\s]+ \d{4})"),
            "Inscrição CNPJ": buscar("Inscrição", r"CNPJ:\s*([\d./-]+)"),
            "Empregador": buscar("Empregador", r"Empregador\s+([A-Z\s]+)"),
            "Admissão": buscar("Admissão", r"Admissão\s+(\d{2}/\d{2}/\d{4})"),
            "Lotação": buscar("Lotação", r"Lotação\s+([^\n]+)"),
            "Cargo": buscar("Cargo", r"Cargo\s+([^\n]+)"),
            "Empregado": empregado,
            "Matrícula": matricula,
            "Nome": nome,
            "Banco": buscar("Banco", r"Banco\s+([^\n]+)"),
            "Agência": buscar("Agência", r"Agência\s+([^\n]+)"),
            "Conta": buscar("Conta", r"Conta\s+([^\n]+)"),
            "Tipo de Conta": buscar("Tipo de Conta", r"Tipo de Conta\s+([^\d\n]+)"),
            "CPF": buscar("CPF", r"(\d{3}\.\d{3}\.\d{3}-\d{2})"),
            "Salário Contratual": buscar("Salário Contratual", r"Salário Contratual\s+([\d.,]+)"),
            "Total de Proventos": buscar("Total de Proventos", r"Total de Proventos\s+([\d.,]+)"),
            "Total de Descontos": buscar("Total de Descontos", r"Total de Descontos\s+([\d.,]+)"),
            "Líquido a Receber": buscar("Líquido a Receber", r"Líquido a Receber\s+([\d.,]+)"),
            "Base de Cálculo do IRRF(S)": buscar("IRRF", r"Base de Cálculo do IRRF\(S\)\s+([\d.,]+)"),
            "Base de Cálculo do INSS": buscar("INSS", r"Base de Cálculo do INSS\s+([\d.,]+)"),
            "FGTS": buscar("FGTS", r"FGTS\s+([\d.,]+)"),
            "Base de Cálculo do FGTS": buscar("Base de Cálculo do FGTS", r"Base de Cálculo do FGTS\s+([\d.,]+)")
        }

        return dados
    except Exception as e:
        print(f"Erro ao processar PDF: {str(e)}")
        return None

# Rota principal
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            if "pdf_file" not in request.files:
                return "Nenhum arquivo enviado", 400
            
            file = request.files["pdf_file"]
            if file.filename == "":
                return "Nome de arquivo vazio", 400
            
            if not file.filename.lower().endswith(".pdf"):
                return "Arquivo deve ser um PDF", 400

            # Extrair dados do PDF
            dados = extrair_dados_pdf(file)
            
            if dados is None:
                return "Erro ao processar o PDF. Verifique se o arquivo é válido.", 500

            # Gerar JSON em memória
            json_text = json.dumps(dados, indent=2, ensure_ascii=False)
            
            return render_template("success.html", json_data=json_text, filename=file.filename)

        except Exception as e:
            print(f"Erro na rota principal: {str(e)}")
            return f"Erro interno do servidor: {str(e)}", 500
    
    return render_template("index.html")

# Rota para download do JSON (removida pois não funciona no Vercel)
# @app.route("/download/<filename>")
# def download_json(filename):
#     return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

# Rodar a aplicação
if __name__ == "__main__":
    app.run(debug=True)
