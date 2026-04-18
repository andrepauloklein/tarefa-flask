print("🔥🔥🔥 NOVO APP CARREGADO 🔥🔥🔥")
import os
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)

# ---------------------------------------------------------
# Configuração do MongoDB
# ---------------------------------------------------------
# Busca a URI e o Nome do Banco das variáveis de ambiente da GCP
mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

db_name = os.environ.get("DB_NAME", "tarefa_db").strip()

client = MongoClient(mongo_uri)
db = client[db_name]
collection = db["tarefa"]

print(f"DEBUG:variável de ambiente MONGO_URI = {mongo_uri}")
print(f"DEBUG: Conectado ao banco: {db_name}")

# ---------------------------------------------------------
# Listar tarefas
# ---------------------------------------------------------


@app.route('/')
def index():
    ordem = request.args.get('ordem', 'prioridade')

    if ordem == 'alfabetica':
        tarefas = list(collection.find().sort("descricao", 1))
    elif ordem == 'insercao':
        tarefas = list(collection.find().sort("_id", 1))
    else:
        tarefas = list(collection.find().sort("prioridade", -1))

    return render_template('index.html', tarefas=tarefas, ordem=ordem)

# ---------------------------------------------------------
# Adicionar tarefa
# ---------------------------------------------------------
@app.route("/adicionar", methods=["POST"])
def adicionar():
    descricao = request.form.get("descricao", "")
    try:
        urgencia = int(request.form.get("urgencia", 0))
        importancia = int(request.form.get("importancia", 0))
    except ValueError:
        urgencia = 0
        importancia = 0

    prioridade = urgencia * importancia

    collection.insert_one({
        "descricao": descricao,
        "urgencia": urgencia,
        "importancia": importancia,
        "prioridade": prioridade,
        "data_criacao": datetime.now().strftime("%d/%m/%Y %H:%M")
    })

    return redirect(url_for("index"))

# ---------------------------------------------------------
# Editar tarefa (Carregar formulário)
# ---------------------------------------------------------
@app.route("/editar/<id>")
def editar(id):
    tarefa = collection.find_one({"_id": ObjectId(id)})
    return render_template("editar.html", tarefa=tarefa)

# ---------------------------------------------------------
# Atualizar tarefa (Salvar mudanças)
# ---------------------------------------------------------
@app.route("/atualizar/<id>", methods=["POST"])
def atualizar(id):
    descricao = request.form.get("descricao", "")
    try:
        urgencia = int(request.form.get("urgencia", 0))
        importancia = int(request.form.get("importancia", 0))
    except ValueError:
        urgencia = 0
        importancia = 0

    prioridade = urgencia * importancia

    collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "descricao": descricao,
            "urgencia": urgencia,
            "importancia": importancia,
            "prioridade": prioridade
        }}
    )

    return redirect(url_for("index"))

# ---------------------------------------------------------
# Excluir tarefa
# ---------------------------------------------------------
@app.route("/excluir/<id>")
def excluir(id):
    collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("index"))

# ---------------------------------------------------------
# Migração Inicial (Garante que o banco novo tenha as prioridades)
# ---------------------------------------------------------
try:
    # Busca apenas quem não tem o campo prioridade
    tarefas_sem_prioridade = list(collection.find({"prioridade": {"$exists": False}}))

    for t in tarefas_sem_prioridade:
        u = t.get("urgencia", 0)
        i = t.get("importancia", 0)
        prio_calculada = u * i

        # CORREÇÃO: O update_one deve estar DENTRO do loop 'for'
        collection.update_one(
            {"_id": t["_id"]},
            {"$set": {"prioridade": prio_calculada}}
        )
except Exception as e:
    print(f"Aviso: Erro na migração inicial: {e}")

# ---------------------------------------------------------
# Iniciar Servidor (Configuração para Cloud Run)
# ---------------------------------------------------------
if __name__ == "__main__":
    # O Cloud Run exige que o app ouça na porta definida pela variável PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)