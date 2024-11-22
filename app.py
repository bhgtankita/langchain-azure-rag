# Import required modules
import os
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores.azuresearch import AzureSearch
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai import AzureChatOpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize embeddings
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

vector_store_address: str = os.getenv("AZURE_SEARCH_ENDPOINT")
vector_store_password: str = os.getenv("AZURE_SEARCH_ADMIN_KEY")

# Initialize AzureSearch with the endpoint, key, index name, and embedding function
index_name: str = "langchain-vector-demo"

vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=vector_store_address,
    azure_search_key=vector_store_password,
    index_name=index_name,
    embedding_function=embeddings.embed_query,
)

openai_api_base: str = os.getenv("AZURE_OPENAI_ENDPOINT")
openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY")
openai_api_version: str = os.getenv("API_VERSION")
deployment_name: str = os.getenv("DEPLOYMENT_NAME")

llm = AzureChatOpenAI(
    deployment_name=deployment_name,
    azure_endpoint=openai_api_base,
    api_key=openai_api_key,
    api_version=openai_api_version,
    temperature=0.7,  # Optional: Adjust model response randomness
    max_tokens=500    # Optional: Adjust token limit
)

def project_idea(certification, level, k=4):
    """
    This function takes a query and an optional parameter k, performs a similarity search on the vector store, joins the page content of the returned documents, invokes the language model with the query and the documents, and returns the response from the language model.
    
    Parameters:
    query (str): The question to ask the language model.
    k (int, optional): The number of similar documents to return. Defaults to 4.

    Returns:
    str: The response from the language model.
    """

    # Perform a similarity search on the vector store
    docs = vector_store.similarity_search(
        query=certification,
        k=k,
        search_type="similarity",
    )
    # Join the page content of the returned documents
    docs = " ".join([d.page_content for d in docs])

    # llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7)

    prompt = PromptTemplate(
        input_variables=["certification", "level", "docs"],
        template="""
        You are a helpful cloud instructor that provides cloud project ideas about Microsoft Azure Certifications based on the certification guide.
        
        Give me a project idea for certification: {certification} of the level: {level}
        By searching the following certification guide: {docs}
        
        Only use the factual information from the guide to provide the project idea.
        
        If you feel like you don't have enough information to answer the question, say "I don't know".
        
        Your answers should be verbose and detailed. Include a Project Name, Project Description, list of Services Used and Steps to make the project. Make sure your response is in markdown format like:

        ### Project Name:
        Project Description:
        Services Used:
        - Service 1
        - Service 2
        #### Steps:
        - Step 1
        - Step 2
        """,
    )
    
    chain = prompt | llm
    
    response = chain.invoke({"certification":certification, "level":level, "docs":docs})
    
    response = response.content.replace("\n", "").replace("###", "\n\n")

    return response