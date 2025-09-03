import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class LLMPipeline:
    def __init__(self):
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", 
            google_api_key=os.getenv('GOOGLE_API_KEY')
            )

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro", 
            google_api_key=os.getenv('GOOGLE_API_KEY'), 
            temperature=0
            )

        #TODO: put it on .env
        index_name = "law-agent"
        vectorstore = PineconeVectorStore(
            index_name=index_name, 
            embedding=embeddings
            )

        # RAG pipeline
        retriever = vectorstore.as_retriever(search_kwargs={"k": 30})

        prompt_template = """Use the following context to answer the question.
        If you don't know, say you don't know.


        Context:
        {context}
        You are an exprienced Israeli lawyer.
        Write a legal opinion according to the question.
        Always base your answer by giving citations and references.
        Each reference should contain the law name(חוק) and section number(סעיף).
        if there isn't a section number - reference to law name and addendum highlight.

        Question: {question}
        Answer:"""


        prompt = PromptTemplate(template=prompt_template,
                                input_variables=["context", "question"])


        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )

    def prompt(self, question: str):
        """
        Gets a question and returns answer
        (Legal Opinion) from LLM.
        
        Args:
            input: A question for Chatbot
        Returns:
            The LLM's answer
        """
        response = self.qa_chain.invoke({'query': question})
        
        #Extracting the answer from the response
        #TODO: maybe do it on the fastApi app
        answer = response.get("result")
        if not isinstance(answer, str):
            answer = str(answer)
        return answer

# pr = input('Enter question')
# print('Thinking...')
# response = qa_chain.invoke({"query": pr})
# print(response['result'])