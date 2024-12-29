from langchain.load import loads, dumps
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)

import pandas as pd
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from operator import itemgetter

from langchain_openai import ChatOpenAI

from langchain_chroma import Chroma

from langchain.prompts import ChatPromptTemplate

class Rag:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens = 1000)
        embedding_function = SentenceTransformerEmbeddings(model_name="DeepPavlov/rubert-base-cased-sentence", model_kwargs={'device': 'cpu'})
        self.db = Chroma(embedding_function=embedding_function, persist_directory="../../artifacts/chroma_db")
        self.retriever = self.db.as_retriever()

        template = """You are an AI language model assistant. Your task is to generate five 
        different versions of the given user question to retrieve relevant documents from a vector 
        database. By generating multiple perspectives on the user question, your goal is to help
        the user overcome some of the limitations of the distance-based similarity search. 
        Provide these alternative questions separated by newlines. Original question: {question}"""
        prompt_perspectives = ChatPromptTemplate.from_template(template)

        generate_queries = (
            prompt_perspectives 
            | self.llm
            | StrOutputParser() 
            | (lambda x: x.split("\n"))
        )

        retrieval_chain = generate_queries | self.retriever.map() | self.get_unique_union

        template = """Answer the following question based on this context:

        {context}

        Question: {question}
        """

        prompt = ChatPromptTemplate.from_template(template)

        self.final_rag_chain = (
            {"context": retrieval_chain, 
            "question": itemgetter("question")} 
            | prompt
            | self.llm
            | StrOutputParser()
        )

        print('chain ready')

    @staticmethod
    def get_unique_union(documents: list[list]):
            """ Unique union of retrieved docs """
            # Flatten list of lists, and convert each Document to string
            flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
            # Get unique documents
            unique_docs = list(set(flattened_docs))
            # Return
            return [loads(doc) for doc in unique_docs]
    
rag = Rag()