# import library Chroma + OpenAI + streamlit + loading variable env
import chromadb
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Client creation
chroma_client = chromadb.PersistentClient("C:/Users/richo")

# Create or get database
#collection = chroma_client.get_or_create_collection(name="DataCom")
#collection = chroma_client.get_or_create_collection(name="Hillary")
#collection = chroma_client.get_or_create_collection(name="Nico_Email")
collection = chroma_client.get_or_create_collection(name="texte")

# Creation of chatGPT for loaded dataset
first_question = True
while True:
    if first_question:
        # user request on dataset
        user_query = input("What do you want to know ? (or type 'quit to exit)'\n")
        first_question = False
    else:
        user_query = input("What else ? (or type 'quit to exit)'\n")

    if user_query.lower() == 'quit':
        break
# Request to database with the user request, number of result is 1 to get the most relevant answer
    results = collection.query(
       query_texts=[user_query],
        n_results=3
        )


    # client IA initialisation
    clientIA = OpenAI()

    # information given to system and answering your question
    system_prompt ="""
    You are a helpful assistant. If you don't know, just say i don't know
    ---------------------
    The data:
    """+str(results['documents'])+"""
    """+str(results['distances'])+"""
    """+str(results['metadatas'])+"""
    """

    print(system_prompt)

    # call response from chatGPT
    response = clientIA.chat.completions.create(
        model="gpt-4o-mini",
        messages= [
            {"role":"system","content":system_prompt},
            {"role":"user", "content":user_query}
        ])

    print("\n")
    # display of the response
    print(response.choices[0].message.content)

