import chromadb
import os
from chromadb import Settings
from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Function to load CSV data into ChromaDB
def load_csv_to_chromadb(csv_file_path):
    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient("C:/Users/richo", settings=Settings(allow_reset=True))

    # Create or get your collection
    #collection = chroma_client.get_or_create_collection(name="Nico_Outlook_email")
    chroma_client.delete_collection(name="shopping_trends")
    collection = chroma_client.get_or_create_collection(name="shopping_trends")

    # Load CSV using Langchain's CSVLoader
    loader = CSVLoader(csv_file_path, csv_args={'delimiter':','})  # Specify the CSV file to load
    dataset = loader.load()  # This will give you a list of Document objects

    # split the text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    chunks = text_splitter.split_documents(dataset)

    #embeddings = get_embeddings(chunks)

    # create 3 lists, IDs = keep track of chunks, metadata = info from source, documents = text
    documents = []
    metadata = []

    i = 0
    # prepare text for loading in DB
    for chunk in chunks:

        # load DB
        collection.add(
           #embeddings=embeddings,     # get embeddings for dataset
           documents=documents.append(chunk.page_content),
           metadatas=metadata.append(chunk.metadata),
           ids=str(i)
        )

        print(f"Successfully added {chunk.metadata} documents to {collection.name} from {csv_file_path}")
        i += 1

#def get_embeddings(texts):
    # client IA initialisation
#    client = OpenAI()

#    response = client.embeddings.create(
#        input=texts,  # This should be a list of strings
#        model="text-embedding-ada-002"
#    )
    # Extract and return the embeddings
#    return [item['embedding'] for item in response['data']]

# Main function
def main():
    csv_file_path = "./Data/Structured/shopping_trends_updated.csv"  # Update with your CSV path
    load_csv_to_chromadb(csv_file_path)

if __name__ == "__main__":
    main()