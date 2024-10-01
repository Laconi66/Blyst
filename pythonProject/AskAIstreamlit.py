import chromadb
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from chromadb.utils import embedding_functions

load_dotenv()

# Client creation
chroma_client = chromadb.PersistentClient("C:/Users/richo")

# Create or get database
#collection = chroma_client.get_or_create_collection(name="Nico_Outlook_email")
collection = chroma_client.get_or_create_collection(name="Texte")
#collection = chroma_client.get_or_create_collection(name="shopping_trends")

# client IA initialisation
clientIA = OpenAI()

# Initialize the Streamlit app
st.title("Chat with : " + collection.name)

# Function to query ChromaDB and get relevant document context
def get_relevant_documents(user_input):
    results = collection.query(query_texts=[user_input], n_results=10)  # Get relevant documents
    return results

# Initialize chat history (this is local in the session, not globally)
if 'chat' not in st.session_state:
    st.session_state.chat = []

# Display existing chat messages
for user_message, assistant_response in st.session_state.chat:
    with st.chat_message("user"):
        st.write(user_message)
    with st.chat_message("assistant"):
        st.write(assistant_response)

# User input for new messages
if prompt := st.chat_input("What is your question?"):

    # Get context from ChromaDB based on user input
    context = get_relevant_documents(prompt)

    chat_messages = [
                        {"role": "user", "content": user_message} for user_message, _ in st.session_state.chat
                    ] + [
                        {"role": "assistant", "content": assistant_response} for _, assistant_response in
                        st.session_state.chat
                    ]

    # Prepare the messages for OpenAI including context
    full_context = [{"role": "user", "content": f"{context}\n\n{prompt}"}]

    # Now combine everything together
    messages = [{"role": "system", "content": "You are a helpful assistant."}] + chat_messages + full_context

    # Call OpenAI to get the assistant's response
    response = clientIA.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # Extract the assistant's response
    assistant_message = response.choices[0].message.content

    # Store user input and assistant response in chat history
    st.session_state.chat.append((prompt, assistant_message))

    # Display the user's response
    with st.chat_message("user"):
        st.write(prompt)

    # Display the assistant's response
    with st.chat_message("assistant"):
        st.write(assistant_message)