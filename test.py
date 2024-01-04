from openai import OpenAI

client = OpenAI(
    api_key= "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"
)

prompt = "Say hi - because I'm testing something"

response = client.chat.completions.create(
    messages=[
        {
           "role":"user", 
           "content":prompt
        }
    ],    
    model="gpt-3.5-turbo"      
)

print(response.choices[0].message.content)
