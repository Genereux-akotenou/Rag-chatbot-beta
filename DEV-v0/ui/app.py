# ---------------------------------------------------------------
# UTILS
# ---------------------------------------------------------------
import streamlit as st

st.set_page_config(
    page_title='RPGChat',
    page_icon='🧊',
    # layout='wide',
    initial_sidebar_state='collapsed',
    # menu_items={
    #     'Get Help': 'https://www.extremelycoolapp.com/help',
    #     'Report a bug': "https://www.extremelycoolapp.com/bug",
    #     'About': "# This is a header. This is an *extremely* cool app!"
    # }
)

import random, os
import time
import torch
from chromadb import Client
from transformers import AutoTokenizer, AutoModel
from langchain.vectorstores import Chroma
import ollama
import streamlit.components.v1 as components
from urllib.parse import quote

# ---------------------------------------------------------------
# CUSTOM
# ---------------------------------------------------------------
file_server_url = "http://localhost:8888/"
custom_css = f"""
<style>
    h1 {{
        font-size: 2rem !important;
    }}
    header.stAppHeader {{
        background-image: url('{file_server_url}/static/file/dna.jpg');
        background-size: cover;
        background-position: center;
        height: 100px;
        color: white;
    }}
    .stAppHeader h1 {{
        text-align: center;
        font-size: 40px;
        font-weight: bold;
    }}
    .stBaseButton-header {{
        background-color: rgba(255, 255, 255, 0.7);
        color: black;
    }}
    .stMainMenu {{
        color: white;
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

#beta
custom_css = """
<style>
    .button-container {
        position: fixed;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        z-index: 999;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .stButton {
        background-color: #775381; /*#f4f4f4;*/
        color: white;
        border: none;
        padding: 15px 15px;
        font-size: 16px;
        text-align: center;
        border-radius: 5px;
        cursor: pointer;
        width: 60px;
        display: flex;
        justify-content: center;
        align-items: center;
        transition: background-color 0.3s ease, color 0.3s ease;
        overflow: hidden;
    }
    .stButton span {
        margin-left: 10px;
    }
    .stButton:hover {
        background-color: #462e4e;
        color: #fff;
    }
    .stButton span {
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .stButton:hover span {
        opacity: 1;
    }
    .collapsed {
        width: 0;
        padding: 0;
        visibility: hidden;
        transition: width 0.3s ease, visibility 0s ease 0.3s;
    }
    .expanded {
        width: 160px;
        padding: 10px;
        visibility: visible;
    }
</style>
"""

# Inject the CSS into the Streamlit app
st.markdown(custom_css, unsafe_allow_html=True)

# Define buttons with native emoji icons
st.markdown("""
    <div class="button-container expanded" id="button-container">
        <a href="http://localhost:8888/ui/file_manager" alt="Logs" class="stButton">
            📤
        </a>
        <a href="http://localhost:8888" alt="Files" class="stButton">
            📝
        </a>
        <button alt="Administration" class="stButton" onclick="window.open('http://localhost:5555', '_blank')">
            ⚙️
        </button>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# MENU options
# ---------------------------------------------------------------
st.sidebar.markdown("### Select Base LLM Model")
if "selected_llm" not in st.session_state:
    st.session_state.selected_llm = "Llama3"

st.session_state.selected_llm = st.sidebar.selectbox(
    "Choose an LLM model:",
    options=["Llama3", "Llama2", "Phi3", "gemma"],
    index=["Llama3", "Llama2", "Phi3", "gemma"].index(st.session_state.selected_llm)
)

if "k" not in st.session_state:
    st.session_state.k = 2
st.sidebar.markdown("### Adjust Number of Sources")
st.session_state.k = st.sidebar.slider(
    "Number of Sources",
    min_value=1,
    max_value=10,
    value=st.session_state.k,
    step=1
)

st.sidebar.markdown("### Other options")
if "activate_memory" not in st.session_state:
    st.session_state.activate_memory = False
st.session_state.activate_memory = st.sidebar.checkbox(
    "Activate memory between prompts",
    value=st.session_state.activate_memory
)
if "include_images" not in st.session_state:
    st.session_state.include_images = False
st.session_state.include_images = st.sidebar.checkbox(
    "Include images in analysis",
    value=st.session_state.include_images
)

# ---------------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------------
def initialize_rag_components():
    """
    Initialize the tokenizer, model, and vector store for RAG.
    """
    model_name = "sentence-transformers/all-mpnet-base-v2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    chroma_client = Client()

    # Embedding function class
    class EmbeddingFunction:
        def __init__(self, model, tokenizer):
            self.model = model
            self.tokenizer = tokenizer

        def embed_documents(self, texts):
            inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
            with torch.no_grad():
                embeddings = self.model(**inputs).last_hidden_state.mean(dim=1)
            return embeddings.numpy()

        def embed_query(self, query):
            inputs = self.tokenizer([query], padding=True, truncation=True, return_tensors="pt")
            with torch.no_grad():
                embedding = self.model(**inputs).last_hidden_state.mean(dim=1)
            return embedding.numpy().squeeze()

    embedding_function = EmbeddingFunction(model=model, tokenizer=tokenizer)
    vector_store = Chroma(
        collection_name="rag_4_researcher_collection",
        embedding_function=embedding_function,
        persist_directory="../database/vector-db/",
    )
    return vector_store

# deprecated
def retrieve_context(vector_store, query, k=2):
    """
    Retrieve relevant context for a query from the vector store.
    """
    try:
        print('---')
        print(query)
        results = vector_store.similarity_search(query, k=k)
        print(results)
        return results[0].page_content if results else "No relevant context found."
    except Exception as e:
        return f"Error during retrieval: {e}"

def retrieve_context(vector_store, query, k=2):
    """
    Retrieve relevant context for a query from the vector store.
    """
    try:
        results = vector_store.similarity_search(query, k=k)
        #print(len(results))
        if results:
            return [{"content": result.page_content, "source": result.metadata} for result in results]
        else:
            return [{"content": "No relevant context found.", "source": None}]
    except Exception as e:
        return [{"content": f"Error during retrieval: {e}", "source": None}]

def format_sources(sources):
    """
    Format sources for display under the response.
    """
    formatted_sources = []
    for source in sources:
        if source["source"]:
            # Extract the file path and page number
            file_path = source["source"].get("file_path", "Unknown file")
            file_name = file_path.split('/')[-1]
            page = source["source"].get("page", "Unknown page")

            # URL-encode the file name to handle spaces and special characters
            encoded_file_name = quote(file_name)
            file_url = f"{file_server_url}{encoded_file_name}"

            # Format the source information
            formatted_sources.append(f"File: [{file_name}]({file_url}), **Page: {page}**")
        else:
            formatted_sources.append("No source available.")
    return formatted_sources

def display_sources(sources):
    """
    Render formatted sources in Streamlit with clickable links.
    """
    st.markdown("#### Sources")
    for formatted_source in format_sources(sources):
        st.markdown(f"- {formatted_source}")

def generate_llm_response(prompt):
    """
    Make a request to the LLM for generating a response.
    """
    try:
        response = ollama.generate(model=st.session_state.selected_llm.lower(), prompt=prompt)
        return response.get("response", "No response received from LLM.")
    except Exception as e:
        return f"Error during LLM response generation: {e}"

def response_generator(response):
    """
    Simulate streaming of a response, word by word.
    """
    #for word in response.split():
    #    yield word + " "
    #    time.sleep(0.09)
    return response

def response_generator_streaming(response):
    """
    Simulate dynamic streaming of a response, typing character by character.
    """
    stream = ""
    for char in response:
        stream += char
        yield stream 
        time.sleep(0.01)


def chat_interface(vector_store):
    """
    Streamlit-based chat interface for interacting with the RAG system.
    """
    st.title("RAG-Powered Genomics-LLM Paper Chat")
    st.markdown(
        """
            <p style="font-size: 14px; color: gray; text-align: justify;">
                This tool helps to ask various questions on documents retrieved from Google Scholar on the topic 
                <strong>"LLMs in genomics"</strong> to understand the state of the art. 
                This is an experimental version and it use sentence-transformers/all-mpnet-base-v2 for embedding and Phi3 for generation. It can respond to you based on the paper and cite the source and page used. Please note: our <strong>RPGChat</strong> can make mistakes.
            </p>
        """, unsafe_allow_html=True
    )
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask your question here:"): # what are open question related to use of llm in genomics for genes predictions ?
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Retrieve context and generate response
        contexts = retrieve_context(vector_store, prompt, k=st.session_state.k)
        print(contexts)
        combined_context = "Ctx: "
        combined_context += " Ctx: ".join([ctx["content"] for ctx in contexts])
        response = generate_llm_response(
            f"Context: {combined_context}\n\nQuestion: {prompt}\n\nNote: Add '\n\n' to separate section if it is hierarchical."
        )

        # Display assistant response
        print('> write ...')
        formatted_sources = "\n".join([f"- {source}" for source in format_sources(contexts)])
        response_with_source =  response + "\n#### Sources\n" + formatted_sources
        with st.chat_message("assistant"):
            response_container = st.empty()
            dynamic_response = response_generator_streaming(response_with_source)
            for partial_text in dynamic_response:
                response_container.markdown(partial_text)
                
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response_with_source})


        #formatted_sources = "\n".join([f"- {source}" for source in format_sources(contexts)])
        #response_with_source =  response + "\n#### Sources\n" + formatted_sources
        #with st.chat_message("assistant"):
        #    response_ = st.write_stream(response_generator(response))
        #    st.markdown(response_generator(response_with_source))
        ## Display sources
        ##display_sources(contexts)
        ## Add assistant response to chat history
        #st.session_state.messages.append({"role": "assistant", "content": response_with_source})

# ---------------------------------------------------------------
# MAIN APP
# ---------------------------------------------------------------
if __name__ == "__main__":
    vector_store = initialize_rag_components()
    chat_interface(vector_store)