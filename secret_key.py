from openai import OpenAI

openai_api_key = "Your OPEN AI API KEY HERE"


#add secret key here
client = OpenAI(
    api_key=openai_api_key,
)