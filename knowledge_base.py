import os

from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import UnstructuredURLLoader
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

# Initialize embeddings from HuggingFace
azure_endpoint: str = os.getenv("AZURE_EMBD_ENDPOINT")
azure_openai_api_key: str = os.getenv("AZURE_EMBD_API_KEY")
azure_openai_api_version: str = os.getenv("AZURE_EMBD_API_VERSION")
azure_deployment: str = os.getenv("AZURE_EMBD_MODEL")

embeddings: AzureOpenAIEmbeddings = AzureOpenAIEmbeddings(
    azure_deployment=azure_deployment,
    openai_api_version=azure_openai_api_version,
    azure_endpoint=azure_endpoint,
    api_key=azure_openai_api_key,
)

# """
# List of URLs for the certification knowledge base. This includes the study guides for the most popular cloud certifications:
# 1. Microsoft Certified Azure Administrator Associate AZ-104
# 2. Microsoft Certified Azure Developer Associate AZ-204
# 3. Microsoft Certified Azure Solutions Architect Expert AZ-305
# 4. Microsoft Certified DevOps Engineer Expert AZ-400
# """

urls = [
    'https://learn.microsoft.com/en-us/certifications/resources/study-guides/az-104',
    'https://learn.microsoft.com/en-us/certifications/resources/study-guides/az-204',
    'https://learn.microsoft.com/en-us/certifications/resources/study-guides/az-305',
    'https://learn.microsoft.com/en-us/certifications/resources/study-guides/az-400',
]

# Configure vector store settings
vector_store_address: str = os.getenv("AZURE_SEARCH_ENDPOINT")
vector_store_password: str = os.getenv("AZURE_SEARCH_ADMIN_KEY")

def del_index_if_exist(index_name):
    # Define Azure Search credentials and endpoint
    search_client = SearchIndexClient(
        endpoint=vector_store_address,
        credential=AzureKeyCredential(vector_store_password)
    )

    # Check if the index exists
    if index_name in [index.name for index in search_client.list_indexes()]:
        search_client.delete_index(index_name)
        msg = f"Index '{index_name}' already exists. deleting and recreating the index."
        return msg

def create_knowledge_base(index_name):

    try:

        # Initialize the Azure Search vector store
        vector_store: AzureSearch = AzureSearch(
                azure_search_endpoint=vector_store_address,
                azure_search_key=vector_store_password,
                index_name=index_name,
                embedding_function=embeddings.embed_query
        )

        # Load and chunk the documents
        loader = UnstructuredURLLoader(urls)
        documents = loader.load()

        # print(documents)
        text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)

        vector_store.add_documents(documents=docs)

    finally:
        del vector_store


def perform_similarity_search():

    try:
        vector_store: AzureSearch = AzureSearch(
            azure_search_endpoint=vector_store_address,
            azure_search_key=vector_store_password,
            index_name=index_name,
            embedding_function=embeddings.embed_query
        )

        # Perform a similarity search
        docs = vector_store.similarity_search(query="Azure Administrator", k=3)

        print(docs)

    finally:
        del vector_store