from chromadb import Settings
import chromadb
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions

# function embedding by default of ChromaDB "all-MiniLM-L6-v2"
default_ef = embedding_functions.DefaultEmbeddingFunction()

def load_csv_to_chromadb(dir_file_path):
    # Client creation
    chroma_client = chromadb.PersistentClient("C:/Users/richo", settings=Settings(allow_reset=True))

    # Collection is where we store embeddings
    collection = chroma_client.get_or_create_collection(name="Texte")

    # loading PDF data
    loader = DirectoryLoader(dir_file_path, glob="*", show_progress=True, use_multithreading=True, silent_errors=True)
    dataset = loader.load()

    #split the text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=0)
    chunks = text_splitter.split_documents(dataset)

    # create 3 lists, IDs = keep track of chunks, metadata = info from source, documents = text
    documents = []
    metadata = []
    ids = []

    i = 0
    # prepare text for loading in DB
    for chunk in chunks:
        #load DB
        collection.add(
            embeddings=default_ef,
            documents=chunk.page_content,
            metadatas=chunk.metadata,
            ids=str(i)
        )

        print(f"Successfully added {chunk.metadata} documents to {collection.name} from {dir_file_path}")
        i += 1

# Main function
def main():
    dir_file_path = "./Data/Unstructured/"
    load_csv_to_chromadb(dir_file_path)

if __name__ == "__main__":
    main()