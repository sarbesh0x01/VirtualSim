import os
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_core import prompts
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate


model = OllamaLLM(model="deepseek-r1")


template = """
            You are a game NPC in an isekai world, interact with the player and don't let them know that this is an isekai world

            This is the background of the game : {reviews}

            This is the question : {question}

"""
prompt = ChatPromptTemplate.from_template(template)

chain = prompt | model

result = chain.invoke({"reviews": [], "question": "Where am i , what is this place"})

print(result)
