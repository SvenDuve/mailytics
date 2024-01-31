
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import LLMRouterChain,RouterOutputParser
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

import os
import openai
from dotenv import load_dotenv, find_dotenv

load_dotenv()
#_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']


MULTI_PROMPT_ROUTER_TEMPLATE = """Given a raw text input to a \
language model select the model prompt best suited for the input. \
You will be given the names of the available prompts and a \
description of what the prompt is best suited for. \
You may also revise the original input if you think that revising\
it will ultimately lead to a better response from the language model.

<< FORMATTING >>
Return a markdown code snippet with a JSON object formatted to look like:
```json
{{{{
    "destination": string \ name of the prompt to use or "DEFAULT"
    "next_inputs": string \ a potentially modified version of the original input
}}}}
```

REMEMBER: "destination" MUST be one of the candidate prompt \
names specified below OR it can be "DEFAULT" if the input is not\
well suited for any of the candidate prompts.
REMEMBER: "next_inputs" can just be the original input \
if you don't think any modifications are needed.

<< CANDIDATE PROMPTS >>
{destinations}

<< INPUT >>
{{input}}

<< OUTPUT (remember to include the ```json)>>"""


# account for deprecation of LLM model
import datetime
# Get the current date
current_date = datetime.datetime.now().date()

# Define the date after which the model should be set to "gpt-3.5-turbo"
target_date = datetime.date(2024, 6, 12)

# Set the model variable based on the current date
if current_date > target_date:
    llm_model = "gpt-3.5-turbo"
else:
    llm_model = "gpt-3.5-turbo-0301"


llm = ChatOpenAI(temperature=0.9, model=llm_model)


class TextRequest(BaseModel):
    text: str


def process_text(request: TextRequest):

    user_text = request.text
    # Process the text with your LLM here
    print(user_text)
    llm_engine = set_llm_engine()
    # Placeholder response
    user_text = llm_engine.run(user_text)
    response = {"processed_text": user_text}
    return response
    



def set_llm_engine():
    # Call your LLM here
    regulatory_template = """You are a experienced lawyer in regulatory matters and you are very good at summarizing texts. \
    You process texts such that all important information is represented in your summary and less important matters are at least mentioned.\
    When you don't know how to summarize a certain aspect, you will always highlight this difficulty.\

    Here is a text to summarize:
    {input}"""


    trading_template = """You are a experienced lawyer in the subect of european energy commodity trading matters and you are very good at summarizing texts. \
    You process texts such that all important information is represented in your summary and less important matters are at least mentioned.\
    When you don't know how to summarize a certain aspect, you will always highlight this difficulty.\

    Here is a text to summarize:
    {input}"""



    prompt_infos = [
        {
            "name": "regulatory", 
            "description": "This is a prompt for regulatory matters", 
            "prompt_template": regulatory_template
        },
        {
            "name": "trading", 
            "description": "This is a prompt for trading matters", 
            "prompt_template": trading_template
        }
    ]

    destination_chains = {}
    for p_info in prompt_infos:
        name = p_info["name"]
        prompt_template = p_info["prompt_template"]
        prompt = ChatPromptTemplate.from_template(template=prompt_template)
        chain = LLMChain(llm=llm, prompt=prompt)
        destination_chains[name] = chain  
    
    destinations = [f"{p['name']}: {p['description']}" for p in prompt_infos]
    destinations_str = "\n".join(destinations)

    default_prompt = ChatPromptTemplate.from_template("{input}")
    default_chain = LLMChain(llm=llm, prompt=default_prompt)


    router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(
        destinations=destinations_str
    )

    router_prompt = PromptTemplate(
        template=router_template,
        input_variables=["input"],
        output_parser=RouterOutputParser(),
    )

    router_chain = LLMRouterChain.from_llm(llm, router_prompt)


    return MultiPromptChain(router_chain=router_chain, destination_chains=destination_chains, default_chain=default_chain)#, verbose=True