import os
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_core import prompts
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


model = OllamaLLM(model="deepseek-r1")
model2 = OllamaLLM(model="deepseek-r1")

template = """
            {{ 
           {{
            You are a Person, Express Behaviour Like an actual human being. 
            You are a civilian of Place ( Extopia ). 
            It is ruled by a king and their is a prophecy a outlander will arrive to destory the world
            Traits that you have : 
            Profession :              A guide. 
            Emotion : jolly
            }}

            Your Job is to answer question to anybody who asks

            This is the question : {question}
"""
prompt = ChatPromptTemplate.from_template(template)

chain = prompt | model

result = chain.invoke({"reviews": [], "question": "Where am i , what is this place"})

print(result)
