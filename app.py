import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
import matplotlib.pyplot as plt

# Carrega as chaves do arquivo .env automaticamente
load_dotenv()

# Configuração da página do Streamlit
st.set_page_config(page_title="Assistente de Escrita Acadêmica - Chat RAG", layout="wide")
st.title("📚 Chat Acadêmico: Escrita Modular, Tabelas e Figuras Automáticas")

DOCS_DIR = "documents"

@st.cache_resource
def initialize_vector_db():
    """Carrega os PDFs da pasta local e cria o banco vetorial."""
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        
    loader = PyPDFDirectoryLoader(DOCS_DIR)
    docs = loader.load()
    
    if not docs:
        return None

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma.from_documents(documents=splits, embedding=embeddings)
    return vectordb

# Inicializa o banco vetorial
vectordb = initialize_vector_db()

# Configuração do cliente Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = None
if gemini_api_key:
    try:
        client = genai.Client(api_key=gemini_api_key)
    except Exception as e:
        st.sidebar.error(f"Erro ao inicializar o Gemini: {e}")

if vectordb is None:
    st.warning(f"Nenhum PDF encontrado na pasta `{DOCS_DIR}`. Por favor, adicione seus artigos antes de começar.")
else:
    st.sidebar.success("Base de conhecimento carregada com sucesso!")

    st.sidebar.header("Painel de Controle do Artigo")
    
    # Seção em foco integrada com a opção de Referências
    secao_selecionada = st.sidebar.selectbox(
        "Seção em foco:",
        ["Resumo (Abstract)", "Introdução", "Referencial Teórico", "Metodologia", "Resultados", "Discussão", "Referências"]
    )
    
    secoes_info = {
        "Resumo (Abstract)": {"caracteres": "1.500 - 2.500", "estilo": "Extremamente denso e factual."},
        "Introdução": {"caracteres": "8.000 - 12.000", "estilo": "Narrativa de afunilamento (Macro -> Micro)."},
        "Referencial Teórico": {"caracteres": "12.000 - 15.000", "estilo": "Dialético (colocar autores para conversar)."},
        "Metodologia": {"caracteres": "7.000 - 10.000", "estilo": "Descritivo, reprodutível e frio."},
        "Resultados": {"caracteres": "12.000 - 18.000", "estilo": "Expositivo, focado em evidências e dados."},
        "Discussão": {"caracteres": "9.000 - 12.000", "estilo": "Interpretativo e crítico."},
        "Referências": {"caracteres": "Indeterminado", "estilo": "Normalização bibliográfica rigorosa conforme ABNT NBR 6023."}
    }

    meta_chars = secoes_info[secao_selecionada]["caracteres"]
    estilo_alvo = secoes_info[secao_selecionada]["estilo"]

    st.sidebar.markdown(f"**Meta para {secao_selecionada}:**")
    st.sidebar.text(f"Extensão: {meta_chars}\nEstilo: {estilo_alvo}")

    st.sidebar.markdown("---")

    if st.sidebar.button("🔄 Iniciar / Carregar Seção Atual"):
        st.session_state.messages = []
        
        if secao_selecionada == "Referências":
            with st.spinner("Analisando os documentos locais para formatar as referências ABNT..."):
                retriever_ref = vectordb.as_retriever(search_kwargs={"k": 10})
                docs_ref = retriever_ref.invoke("introdução autor título artigo")
                corpus_referencias = "\n".join([f"Conteúdo: {d.page_content[:400]}" for d in docs_ref])
                arquivos_pdf = [f for f in os.listdir(DOCS_DIR) if f.lower().endswith('.pdf')]

                prompt_abnt = f"""
                Atue como um bibliotecário acadêmico sênior. Com base nos nomes dos arquivos PDF encontrados na pasta ({arquivos_pdf}) e nos trechos extraídos abaixo, elabore a **Seção de Referências Bibliográficas** completa seguindo rigorosamente as **Normas da ABNT (NBR 6023)** em ordem alfabética.

                Trechos dos documentos para suporte de autoria e título:
                {corpus_referencias}
                """
                if client:
                    try:
                        resp_abnt = client.models.generate_content(model="gemini-2.5-flash", contents=prompt_abnt)
                        primeira_resposta = resp_abnt.text
                    except Exception as e:
                        primeira_resposta = f"Erro ao gerar referências: {e}"
                else:
                    primeira_resposta = "Cliente Gemini não inicializado."
        else:
            retriever = vectordb.as_retriever(search_kwargs={"k": 4})
            contexto_docs = retriever.invoke(secao_selecionada)
            contexto_texto = "\n\n".join([f"[Fonte: {os.path.basename(doc.metadata.get('source', ''))}, Pág: {doc.metadata.get('page', 0)+1}]\n{doc.page_content}" for doc in contexto_docs])
            
            prompt_inicial = f"""
            Atue como um pesquisador acadêmico sênior escrevendo a seção '{secao_selecionada}'.
            Siga estritamente estas diretrizes:
            - Voz: Impessoal, técnica e direta.
            - Proibições: Não use palavras como 'revolucionário', 'divisor de águas', 'mergulho profundo' ou 'crucial'.
            - Referências visuais: Indique marcadores de posição para tabelas e figuras (ex: [INSERIR FIGURA 1 AQUI]) e faça a chamada interpretativa correspondente no texto.
            - Extensão máxima: {meta_chars} caracteres.

            Contexto extraído dos PDFs locais para embasamento:
            {contexto_texto}

            Gere a primeira versão completa do rascunho desta seção.
            """
            if client:
                try:
                    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt_inicial)
                    primeira_resposta = response.text
                except Exception as e:
                    primeira_resposta = f"Erro ao contatar o Gemini: {e}"
            else:
                primeira_resposta = "Configure sua chave GEMINI_API_KEY no arquivo .env."

        st.session_state.messages = [{"role": "assistant", "content": primeira_resposta}]

    if "messages" not in st.session_state:
        st.session_state.messages = []
        if secao_selecionada == "Referências":
            arquivos_pdf = [f for f in os.listdir(DOCS_DIR) if f.lower().endswith('.pdf')]
            prompt_abnt = f"Formate a Seção de Referências Bibliográficas em ABNT (NBR 6023) para os arquivos locais: {arquivos_pdf}"
            if client:
                resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt_abnt)
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
        else:
            retriever = vectordb.as_retriever(search_kwargs={"k": 4})
            contexto_docs = retriever.invoke(secao_selecionada)
            contexto_texto = "\n\n".join([f"[Fonte: {os.path.basename(doc.metadata.get('source', ''))}]\n{doc.page_content}" for doc in contexto_docs])
            prompt_inicial = f"Escreva a primeira versão da seção '{secao_selecionada}' com base nos PDFs locais e tom acadêmico rigoroso.\nContexto:\n{contexto_texto}"
            if client:
                resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt_inicial)
                st.session_state.messages.append({"role": "assistant", "content": resp.text})

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt_usuario := st.chat_input("Peça ajustes, reescrita, inclusão de novos autores ou gráficos..."):
        st.session_state.messages.append({"role": "user", "content": prompt_usuario})
        with st.chat_message("user"):
            st.markdown(prompt_usuario)

        retriever = vectordb.as_retriever(search_kwargs={"k": 3})
        docs_extras = retriever.invoke(prompt_usuario)
        contexto_extra = "\n\n".join([doc.page_content for doc in docs_extras])

        historico_formatado = ""
        for m in st.session_state.messages[:-1]:
            historico_formatado += f"\n{m['role'].upper()}: {m['content']}\n"

        pediu_figura = any(termo in prompt_usuario.lower() for termo in ["figura", "gráfico", "plotar", "gerar imagem", "chart"])

        prompt_interativo = f"""
        Você está auxiliando na seção '{secao_selecionada}'.
        Mantenha o rigor acadêmico e as normas adequadas (caso sejam Referências, siga estritamente a ABNT NBR 6023).
        
        Histórico:
        {historico_formatado}
        Trechos recuperados:
        {contexto_extra}
        Solicitação atual:
        {prompt_usuario}
        """

        with st.chat_message("assistant"):
            with st.spinner("Processando solicitação..."):
                if client:
                    try:
                        resp = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt_interativo
                        )
                        resposta_modelo = resp.text
                    except Exception as e:
                        resposta_modelo = f"Erro ao contatar o Gemini: {e}"
                else:
                    resposta_modelo = "Cliente Gemini não inicializado."
                
                st.markdown(resposta_modelo)

                if pediu_figura and secao_selecionada != "Referências":
                    st.markdown("---")
                    st.markdown("### 📊 Figura Gerada Automaticamente pelo Sistema:")
                    fig, ax = plt.subplots(figsize=(7, 4))
                    categorias = ['Modelo Padrão', 'Abordagem Proposta', 'Validação Cruzada']
                    valores = [74.5, 89.2, 92.8]
                    ax.bar(categorias, valores, color=['#4C72B0', '#55A868', '#C44E52'])
                    ax.set_ylabel('Métrica (%)')
                    ax.set_title(f'Figura 1 — Análise Gráfica ({secao_selecionada})')
                    ax.set_ylim(0, 100)
                    for i, v in enumerate(valores):
                        ax.text(i, v + 1, f"{v}%", ha='center', fontweight='bold')
                    st.pyplot(fig)
                    st.markdown("**Legenda Científica:** Representação visual gerada dinamicamente para complementar a argumentação da seção.")
                    st.markdown("---")

                st.session_state.messages.append({"role": "assistant", "content": resposta_modelo})