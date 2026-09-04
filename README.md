Para estruturar o repositório e deixá-lo com padrão profissional para o GitHub, preparei um **`README.md`** completo e detalhado. Ele explica a arquitetura baseada em RAG local, o fluxo de escrita modular por seções (com as normas ABNT), a configuração do arquivo `.env` e a execução local via Streamlit.

Basta criar um arquivo chamado `README.md` na raiz do seu projeto e colar o conteúdo abaixo:

---

# 📚 Assistente de Escrita Acadêmica com RAG Local e Chat Interativo

Aplicação desenvolvida em **Python** utilizando **Streamlit**, **LangChain**, **ChromaDB** e a API do **Google Gemini** para auxiliar pesquisadores e estudantes na elaboração de artigos científicos modulares. O sistema realiza busca vetorial estrita (**RAG**) em arquivos PDF locais salvos no repositório, garantindo que o texto gerado seja ancorado exclusivamente nas fontes bibliográficas do usuário, sem alucinações e com suporte à formatação nas normas da **ABNT**.

---

## 🚀 Funcionalidades Principais

* **RAG Local Rigoroso:** Indexação de artigos em PDF (`.pdf`) utilizando embeddings abertos da Hugging Face (`all-MiniLM-L6-v2`) e banco vetorial ChromaDB.
* **Escrita Modular por Seção:** Permite alternar entre seções acadêmicas clássicas (*Resumo, Introdução, Referencial Teórico, Metodologia, Resultados, Discussão e Referências*), cada uma com metas específicas de extensão e estilo de escrita.
* **Chat Interativo Contextual (`st.chat_message`):** Histórico de conversas onde você pode interagir com o modelo, pedir refinamentos de parágrafos, reescritas e ajustes de tom cético/técnico.
* **Geração Automática de Tabelas e Figuras:** Capacidade de estruturar dados em tabelas Markdown e plotar gráficos estatísticos reais via Matplotlib no fluxo do chat, indicando os locais de inserção (`[INSERIR FIGURA X]`) e gerando as chamadas interpretativas no texto.
* **Geração de Referências ABNT:** Opção dedicada no menu para compilar e formatar automaticamente a seção de referências bibliográficas seguindo a norma ABNT NBR 6023 com base nos arquivos locais.

---

## 🛠️ Pré-requisitos e Tecnologias

* **Python** (versão 3.10 ou superior recomendada)
* Conta na API do Google Gemini para obtenção da chave de acesso (`GEMINI_API_KEY`).

---

## ⚙️ Configuração do Ambiente (.env)

Na raiz do seu projeto, crie um arquivo chamado **`.env`** (exatamente com esse nome) e insira as suas chaves de acesso de forma segura.

Exemplo de estrutura do arquivo `.env`:

```env
GEMINI_API_KEY="sua_chave_do_gemini_aqui"

```

> **Atenção:** Nunca compartilhe ou envie o seu arquivo `.env` para o GitHub. Ele já deve vir configurado no seu arquivo `.gitignore`.

---

## 📦 Instalação e Execução Local

Siga os passos abaixo para configurar o ambiente e rodar a aplicação no seu computador:

1. **Clone o repositório ou abra a pasta do projeto no terminal:**
```bash
cd seu-projeto-academic-assistant

```


2. **Crie e ative um ambiente virtual (Virtual Environment):**
* **No Windows (PowerShell):**
```bash
python -m venv venv
venv\Scripts\activate

```


* **No Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate

```




3. **Instale as dependências do projeto:**
Utilize o arquivo `requirements.txt` para instalar todas as bibliotecas necessárias de uma só vez:
```bash
pip install -r requirements.txt

```


4. **Adicione seus artigos PDF:**
Crie uma pasta chamada **`documents`** na raiz do projeto e coloque dentro dela todos os arquivos `.pdf` que servirão de base para a pesquisa:
```text
meu-projeto/
├── documents/
│   ├── artigo_exemplo_1.pdf
│   └── artigo_exemplo_2.pdf
├── app.py
├── requirements.txt
└── .env

```


5. **Execute a aplicação Streamlit:**
```bash
streamlit run app.py

```


O navegador abrirá automaticamente na porta `http://localhost:8501`.

---

## 📂 Estrutura do Repositório

```text
.
├── documents/            # Pasta para armazenamento dos PDFs locais (corpus de busca)
├── venv/                 # Ambiente virtual Python (ignorado no git)
├── .env                  # Chaves de API confidenciais (ignorado no git)
├── .gitignore            # Arquivos ignorados pelo controle de versão
├── requirements.txt      # Lista de dependências e bibliotecas Python
└── app.py                # Código principal da aplicação Streamlit e integração RAG/Gemini

```

---

## 💡 Dicas de Uso Acadêmico

1. **Tom de Escrita:** As diretrizes do sistema instruem o Gemini a adotar uma voz impessoal, técnica e direta, proibindo termos marqueteiros ou clichês comuns de IA.
2. **Criação de Gráficos:** Ao conversar no chat, digite comandos como *"Gere uma figura comparativa de acurácia"* para que o sistema plote o gráfico em Matplotlib e crie o gancho de referência no texto.

---

## 📄 Licença

Este projeto é desenvolvido para fins acadêmicos e de pesquisa educacional. Sinta-se à vontade para adaptá-lo ao seu fluxo de mestrado ou doutorado.