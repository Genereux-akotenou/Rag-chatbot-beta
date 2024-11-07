from flask import Flask, request, render_template, jsonify
from llama_index.core import QueryBundle
from llama_index.core.retrievers import BaseRetriever
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core.schema import NodeWithScore
from typing import Any, List
from typing import Optional
import requests
import psycopg2
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


# -----------------------------------------------------------------------
# APP
# -----------------------------------------------------------------------
app = Flask(__name__)


# -----------------------------------------------------------------------
# UTILS
# -----------------------------------------------------------------------
# DB Parameters
db_name = "rag_vector_db"
host = "localhost"
password = "rag_password"
port = "5433"
user = "rag_user"
vector_store = PGVectorStore.from_params(
    database=db_name,
    host=host,
    password=password,
    port=port,
    user=user,
    table_name="rag_paper_fr",
    embed_dim=1024,
)
embed_model = HuggingFaceEmbedding(model_name="manu/bge-m3-custom-fr")

# -----------------------------------------------------------------------
# ROUTES
# -----------------------------------------------------------------------
# Route for the main chat page
@app.route("/")
def home():
    return render_template("index.html")

# API route to handle chat requests
@app.route("/chat", methods=["POST"])
def chat():
    user_prompt = request.json.get("prompt", "")
    if not user_prompt:
        return jsonify({"response": "Please enter a prompt.", "sources": []})

    query_embedding = embed_model.get_query_embedding(user_prompt)
    query_mode = "default"
    vector_store_query = VectorStoreQuery(
        query_embedding=query_embedding, similarity_top_k=2, mode=query_mode
    )
    query_result = vector_store.query(vector_store_query)
    context = query_result.nodes[0].text + query_result.nodes[1].text
    print(context)
    
    url = 'http://localhost:11434/api/generate'
    base_file= "file:///Users/genereux/Documents/UM6P/COURS-S3/TEXT-MINING/Project/"
    prompt_params = {
        "model": "llama3",
        "prompt": f"Genere une reponse a cette question: '${user_prompt}' en utilisant comme context uniquement les informations disponibles ici: context: '${context}'. La reponse doit etre dans la langue du prompt. Si la reponse n'est pas dans le context veuillez le notifier.",
        "stream": False
    }
    response = requests.post(url, json=prompt_params)
    if response.status_code == 200:
        response_data = response.json()
        return jsonify({
            "response": response_data.get("response", "No response received."),
            "sources": [base_file+query_result.nodes[0].metadata['file_path'], base_file+query_result.nodes[1].metadata['file_path']]
        })
    else:
        return jsonify({"response": f"Error: An error occur !", "sources": []})
        
if __name__ == "__main__":
    app.run(debug=True)
