import openai

openai.api_key = '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'
completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Tell the world about the ChatGPT API in the style of a professional."}])
print(completion["choices"][0]["message"]["content"])