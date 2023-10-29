import gradio as gr
import PyPDF2
import os
from langchain.embeddings import CohereEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms.fireworks import Fireworks 
from langchain import VectorDBQA

FIREWORKS_API_KEY = "<paste your Fireworks API key here>"
os.environ["FIREWORKS_API_KEY"] = FIREWORKS_API_KEY

def pdf_to_text(pdf_file, query):
  # Open the PDF file in binary mode
  with open(pdf_file.name, 'rb') as pdf_file:
      # Create a PDF reader object
      pdf_reader = PyPDF2.PdfReader(pdf_file)

      # Create an empty string to store the text
      text = ""

      # Loop through each page of the PDF
      for page_num in range(len(pdf_reader.pages)):
          # Get the page object
          page = pdf_reader.pages[page_num]
          # Extract the texst from the page and add it to the text variable
          text += page.extract_text()
  #embedding step 
  llm = Fireworks(model="accounts/fireworks/models/llama-v2-13b-chat", model_kwargs={"temperature": 0, "max_tokens": 500, "top_p": 1.0})  
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
  texts = text_splitter.split_text(text)

  embeddings = CohereEmbeddings(cohere_api_key="<PASTE COHERE API KEY HERE>")
  #vector store
  vectorstore = FAISS.from_texts(texts, embeddings)

  #inference
  qa = VectorDBQA.from_chain_type(llm=llm, chain_type="stuff", vectorstore=vectorstore)
  return qa.run(query)

# Define the Gradio interface
pdf_input = gr.inputs.File(label="PDF File")
query_input = gr.inputs.Textbox(label="Query")
outputs = gr.outputs.Textbox(label="Chatbot Response")
interface = gr.Interface(fn=pdf_to_text, inputs=[pdf_input, query_input], outputs=outputs)

# Run the interface
interface.launch(server_port=1112)
