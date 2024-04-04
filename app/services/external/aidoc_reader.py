import threading
import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import google.generativeai as genai
import subprocess  # To run shell commands


class AIDOC_READER:
    def __init__(self, name, queue_name, queue_handler, event_handler):
        self.name = name
        self.queue_name = queue_name
        self.stop_flag = False
        self.event = threading.Event()
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.event_handler.subscribe(self)
        self._key = "AIzaSyAWE6advew5ze_OM6WqQBxag9m_Wpl1V0U"
        self.ai = genai.configure(api_key=self._key)
        self.loaded_documents = {}  # Dictionary to store loaded documents and their vectors

    def get_pdf_text(self, pdf_docs):
        text = ""
        for pdf in pdf_docs:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def get_text_chunks(self, text):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=10000, chunk_overlap=1000)
        chunks = text_splitter.split_text(text)
        return chunks

    def get_vector_store(self, text_chunks, document_id):
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        self.loaded_documents[document_id] = vector_store

    def get_conversational_chain(self):
        prompt_template = """
        Answer the question using all the details you have. If the information isn't there just say, "answer is not available in the context", don't provide the wrong answer\n\n
        Context:\n {context}?\n
        Question: \n{question}\n
        Answer:
        """

        model = ChatGoogleGenerativeAI(model="gemini-pro",
                                       temperature=0.3)
        prompt = PromptTemplate(template=prompt_template,
                                input_variables=["context", "question"])
        chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
        return chain

    def document_ask(self, user_question):
        chain = self.get_conversational_chain()
        response = {}
        for document_id, vector_store in self.loaded_documents.items():
            docs = vector_store.similarity_search(user_question)
            response[document_id] = chain(
                {"input_documents": docs, "question": user_question}, return_only_outputs=True)["output_text"]

        return response

    def document_vectorizing(self, document, document_id):
        raw_text = self.get_pdf_text(document)
        text_chunks = self.get_text_chunks(raw_text)
        self.get_vector_store(text_chunks, document_id)

    def convert_to_pdf(self, file_path):
        if file_path.lower().endswith(".pdf"):
            return file_path

        pdf_path = file_path + ".pdf"
        if file_path.lower().endswith(".docx"):
            subprocess.run(["libreoffice", "--headless",
                           "--convert-to", "pdf", file_path])
        elif file_path.lower().endswith(".doc"):
            subprocess.run(["libreoffice", "--headless",
                           "--convert-to", "pdf", file_path])

        return pdf_path

    def main(self):
        self.queue_handler.add_to_queue(
            "CONSOLE", [self.name, "Has been instantiated"])
        self.event.wait()

        if not self.stop_flag:
            self.queue_handler.add_to_queue(
                "CONSOLE", [self.name, "Is Started"])

        while not self.stop_flag:
            ids, doc, channel = self.queue_handler.get_queue(
                "AI_DOC_READER", 0.1, (None, None, None))
            if ids is None:
                continue

            try:
                if isinstance(doc, str) and not doc.lower().endswith(".pdf"):
                    doc = self.convert_to_pdf(doc)

                self.document_vectorizing(doc, ids[0])
                self.queue_handler.add_to_queue(
                    f'AIDOC_READER_RESPONSE', (ids, channel))

            except Exception as e:
                print(f"Error: {e}")
                return

    def run(self):
        self.event.set()

    def stop(self):
        self.stop_flag = True

    def handle_shutdown(self):  # This for event handling
        self.stop_flag = False


if __name__ == "__main__":
    pass
