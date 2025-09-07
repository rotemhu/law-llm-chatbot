import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore
# from langchain.chains import RetrievalQA
from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class LLMPipeline:
    def __init__(self):
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", 
            google_api_key=os.getenv('GOOGLE_API_KEY')
            )

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro", 
            google_api_key=os.getenv('GOOGLE_API_KEY'), 
            streaming=True,
            temperature=0
            )

        #TODO: put it on .env
        index_name = "law-agent"
        vectorstore = PineconeVectorStore(
            index_name=index_name, 
            embedding=embeddings
            )

        # RAG pipeline
        self.retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

        self.prompt_template = """Use the following context to answer the question.
        If you don't know, say you don't know.


        Context:
        {context}
        You are an exprienced Israeli lawyer.
        Write a legal opinion according to the question.
        Always base your answer by giving citations and references.
        Each reference should contain the law name(חוק) and section number(סעיף).
        if there isn't a section number - reference to law name and addendum.

        Question: {question}
        Answer:"""


        prompt = PromptTemplate(template=self.prompt_template,
                                input_variables=["context", "question"])


        # self.qa_chain = RetrievalQA.from_chain_type(
        #     llm=llm,
        #     retriever=retriever,
        #     chain_type="stuff",
        #     chain_type_kwargs={"prompt": prompt},
        #     return_source_documents=True
        # )

    async def prompt(self, question: str):
        """
        Async generator: streams tokens from Gemini.
        Yields partial chunks of the answer.
        """
        # Step 1: Retrieve documents
        docs = await self.retriever.ainvoke(question)
        context = "\n\n".join([doc.page_content for doc in docs])

        # Step 2: Build full prompt
        full_prompt = self.prompt_template.format(context=context, question=question)

        # Step 3: Stream LLM response
        async for chunk in self.llm.astream([HumanMessage(content=full_prompt)]):
            if chunk.content:
                yield chunk.content
    
    # def prompt(self, question: str):
    #     """
    #     Gets a question and returns answer
    #     (Legal Opinion) from LLM.
        
    #     Args:
    #         input: A question for Chatbot
    #     Returns:
    #         The LLM's answer
    #     """
    #     response = self.qa_chain.invoke({'query': question})
        
    #     #Extracting the answer from the response
    #     #TODO: maybe do it on the fastApi app
    #     answer = response.get("result")
    #     if not isinstance(answer, str):
    #         answer = str(answer)
    #     return answer


# pr = input('Enter question')
# print('Thinking...')
# response = qa_chain.invoke({"query": pr})
# print(response['result'])

# import asyncio

# async def main():
#     pipeline = LLMPipeline()
#     question = input('Enter question: ')

#     print("Streaming answer:\n")
#     async for token in pipeline.prompt(question):
#         print(token, end="", flush=True)

# if __name__ == "__main__":
#     asyncio.run(main())