import os
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# ---------------------------------------------------------
# Configuração do MongoDB
# ---------------------------------------------------------
mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

db = client["tarefa_db"]
colecao = db["tarefa"]

print("Conectando em:", mongo_uri)


# ---------------------------------------------------------
# Listar tarefas
# ---------------------------------------------------------

@app.route("/")
def index():
    
    try:
        #tarefas = list(colecao.find())
        tarefas = list(colecao.find().sort("prioridade", -1))


        for t in tarefas:
            if "prioridade" not in t:
                u = t.get("urgencia", 0)
                i = t.get("importancia", 0)
                t["prioridade"] = u * i 

        return render_template("index.html", tarefas=tarefas)
    except Exception as e:
        return f"Erro de conexão com o MongoDB: {e}", 500

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
    urgencia = int(urgencia)
    importancia = int(importancia)
    prioridade = urgencia * importancia


    colecao.insert_one({
        "descricao": descricao,
        "urgencia": urgencia,
        "importancia": importancia,
        "prioridade": prioridade
    })

    return redirect(url_for("index"))

# ---------------------------------------------------------
# Ordenar por prioridade
# ---------------------------------------------------------
@app.route("/ordenar")
def ordenar():
    tarefas = list(colecao.find().sort("prioridade", -1))
    return render_template("index.html", tarefas=tarefas)

# ---------------------------------------------------------
# Editar tarefa
# ---------------------------------------------------------
'''@app.route("/editar/<id>")
def editar(id):
    tarefa = colecao.find_one({"_id": ObjectId(id)})
    return render_template("editar.html", tarefa=tarefa)
    urgencia = int(request.form["urgencia"])
    importancia = int(request.form["importancia"])

    prioridade = urgencia * importancia

colecao.update_one(
    {"_id": ObjectId(id)},
    {"$set": {
        "descricao": request.form["descricao"],
        "urgencia": urgencia,
        "importancia": importancia,
        "prioridade": prioridade
    }}
)'''
@app.route("/editar/<id>")
def editar(id):
    # Aqui o 'id' vem da URL, então funciona corretamente
    tarefa = colecao.find_one({"_id": ObjectId(id)})
    return render_template("editar.html", tarefa=tarefa)




# ---------------------------------------------------------
# Atualizar tarefa
# ---------------------------------------------------------
'''@app.route("/atualizar/<id>", methods=["POST"])
def atualizar(id):
    descricao = request.form.get("descricao", "")
    try:
        urgencia = int(request.form.get("urgencia", 0))
        importancia = int(request.form.get("importancia", 0))
    except ValueError:
        urgencia = 0
        importancia = 0

    prioridade = urgencia * importancia

    colecao.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "descricao": descricao,
            "urgencia": urgencia,
            "importancia": importancia,
            "prioridade": prioridade
        }}
    )

    return redirect(url_for("index"))'''

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

    colecao.update_one(
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
    colecao.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("index"))


tarefas_sem_prioridade = colecao.find({"prioridade": {"$exists": False}})


try:
    tarefas_sem_prioridade = colecao.find({"prioridade": {"$exists": False}})

    for t in tarefas_sem_prioridade:
        u = t.get("urgencia", 0)
        i = t.get("importancia", 0)
        prioridade = u * i

    colecao.update_one(
        {"_id": t["_id"]},
        {"$set": {"prioridade": prioridade}}
    )
except Exception as e:
    print(f"Aviso: Não foi possível realizar a migração inicial: {e}")

# iniciar servidor apos a migracao
if __name__ == "__main__":
    app.run(debug=True)