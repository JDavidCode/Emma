import threading
import os
import traceback
import subprocess
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import google.generativeai as genai


class AIDOC_READER:
    def __init__(self, name, queue_name, queue_handler, event_handler):
        self.name = name
        self.queue_name = queue_name
        self.stop_flag = False
        self.event = threading.Event()
        self.queue_handler = queue_handler
        self.event_handler = event_handler
        self.event_handler.subscribe(self)
        self.ai = genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.chain = None
        self.embeddings = None
        self.loaded_documents = {}

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

    def get_vector_store(self, uid, document_id, text_chunks):
        vector_store = FAISS.from_texts(text_chunks, embedding=self.embeddings)
        self.loaded_documents[uid][document_id] = vector_store

    def get_conversational_chain(self):
        prompt_template = """
        Answer the question using all the details you have. If the information isn't there just say, "answer is not available in the context", don't provide the wrong answer\n\n
        Context:\n {context}?\n
        Question: \n{question}\n
        Answer:
        """

        model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
        prompt = PromptTemplate(template=prompt_template, input_variables=[
                                "context", "question"])
        chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
        return chain

    def document_vectorizing(self, uid, fid, document):
        raw_text = self.get_pdf_text(document)
        text_chunks = self.get_text_chunks(raw_text)
        self.loaded_documents[uid] = {}
        self.get_vector_store(uid, fid, text_chunks)

    def convert_to_pdf(self, file_path):
        if file_path.lower().endswith(".pdf"):
            return file_path

        pdf_path = file_path + ".pdf"
        if file_path.lower().endswith(".docx") or file_path.lower().endswith(".doc"):
            subprocess.run(["libreoffice", "--headless",
                           "--convert-to", "pdf", file_path])
        return pdf_path

    def main(self):
        try:
            self.event.wait()
            self.queue_handler.add_to_queue(
                "CONSOLE", [self.name, "Is Started"])

            while not self.stop_flag:
                try:
                    ids, data, channel = self.queue_handler.get_queue(
                        "AIDOC_READER_QUESTION", 0.1, (None, None, None))
                    if ids is None:
                        continue
                    for uid in self.loaded_documents:
                        if ids[0] == uid:
                            for fid in self.loaded_documents[uid]:
                                if ids[2] == fid:
                                    docs = self.loaded_documents[uid][fid]
                                    docs = docs.similarity_search(data)
                                    response = self.chain(
                                        {"input_documents": docs, "question": data}, return_only_outputs=True)["output_text"]
                                    self.queue_handler.add_to_queue(
                                        "AIDOC_READER_RESPONSE", ("response", ids, response, channel))
                except Exception as e:
                    traceback_str = traceback.format_exc()
                    self.queue_handler.add_to_queue(
                        "LOGGING", (self.name, (e, traceback_str)))
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue(
                "LOGGING", (self.name, (e, traceback_str)))

        return response

    def document_loader(self):
        try:
            while not self.stop_flag:
                try:
                    ids, doc, channel = self.queue_handler.get_queue(
                        "AIDOC_READER", 0.1, (None, None, None))
                    if ids is None:
                        continue

                    try:
                        doc_name = doc[0]
                        doc_path = doc[1]
                        if isinstance(doc_path, str) and not doc_path.lower().endswith(".pdf"):
                            doc_path = self.convert_to_pdf(doc)
                        elif not isinstance(doc_path, list):
                            doc_path = [doc_path]
                        self.document_vectorizing(ids[0], ids[2], doc_path)
                        self.queue_handler.add_to_queue(
                            f'AIDOC_READER_RESPONSE', ("load",  ids,  doc_name, channel))
                    except Exception as e:
                        traceback_str = traceback.format_exc()
                        self.queue_handler.add_to_queue(
                            "LOGGING", (self.name, (e, traceback_str)))
                except Exception as e:
                    traceback_str = traceback.format_exc()
                    self.queue_handler.add_to_queue(
                        "LOGGING", (self.name, (e, traceback_str)))
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.queue_handler.add_to_queue(
                "LOGGING", (self.name, (e, traceback_str)))

    def run(self):
        self.event.set()

    def _handle_system_ready(self):
        self.chain = self.get_conversational_chain()
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001")
        aidoc_reader_thread = threading.Thread(
            target=self.document_loader, name=f"{self.name}_WEB")
        aidoc_reader_thread.start()
        self.run()
        return True

    def stop(self):
        self.stop_flag = True

    def handle_error(self, error, message=None):
        error_message = f"Error in {self.name}: {error}"
        if message:
            error_message += f" - {message}"
        traceback_str = traceback.format_exc()
        self.queue_handler.add_to_queue("LOGGING", (self.name, traceback_str))

    def _handle_shutdown(self):
        try:
            self.queue_handler.add_to_queue(
                "CONSOLE", (self.name, "Handling shutdown..."))
            self.event_handler.subscribers_shutdown_flag(
                self)
        except Exception as e:
            self.handle_error(e)


if __name__ == "__main__":
    pass
