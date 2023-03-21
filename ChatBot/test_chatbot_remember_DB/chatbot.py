import openai
import pymongo
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import transformers
import torch

# Connect to MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017/') # MongoDB
db = client['chatbot'] # MongoDB
collection = db['history'] # MongoDB

# Set up OpenAI API
openai.api_key = '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' # Leo's OpenAi API

# Load pre-trained language model
tokenizer = transformers.AutoTokenizer.from_pretrained('bert-base-multilingual-uncased')
model = transformers.AutoModel.from_pretrained('bert-base-multilingual-uncased')

# Define function to convert text to vectors using BERT
def encode_text(text):
    input_ids = tokenizer.encode(text, max_length=2048)
    input_ids = np.array(input_ids)
    input_ids = np.reshape(input_ids, (1,-1))
    with torch.no_grad():
        outputs = model(torch.tensor(input_ids))[0]
    return outputs.numpy()[0]

# Define function to retrieve top n most similar conversations
def get_top_n_similar_conversations(prompt, collection, n):
    prompt_vector = encode_text(prompt)
    conversations = []
    for conversation in collection.find():
        message = conversation["message"]
        response = conversation["response"]
        conversation_vector = encode_text("User: " + message +"\nBot: " + response )
        #print(conversation_vector)
        similarity = cosine_similarity(prompt_vector, conversation_vector)[0][0]
        conversations.append((conversation, similarity))
    conversations = sorted(conversations, key=lambda x: x[1], reverse=True)
    return [conversation[0] for conversation in conversations[:n]]

# Define chatbot functionality
def get_latest_message():
    # Retrieve the latest message from the user from MongoDB
    latest_message = collection.find_one(sort=[('timestamp', pymongo.DESCENDING)])
    if latest_message:
        return latest_message['message']
    else:
        return ''

def send_message(message):
    # Send the user's message to OpenAI and get a response
    response = openai.ChatCompletion.create(model = 'gpt-3.5-turbo'
                                                    , messages = [{"role" : "system", "content": "You are a Smart Chatbot. try to answer the prompts professionally and make sure you answer correctly."},
                                                                  {"role" : "user", "content": f" prompts:{message}"}]
                                                    , temperature=0.7
                                                    , frequency_penalty= 0.5
                                                    , max_tokens=1024
                                                    )
    return str(response['choices'][0]['message']['content']).strip()

def store_history(user_message, bot_response):
    # Store the conversation history in MongoDB
    history = {
        'timestamp': pymongo.MongoClient().get_database('chatbot').command('serverStatus')['localTime'],
        'message': user_message,
        'response': bot_response
    }
    collection.insert_one(history)

def get_response(user_message):
    # Retrieve the conversation history from MongoDB and use it to generate a response
    # TODO:How to get previous prompts with at least top 3 and at most of 6 relate history converstions to current questions in MongoDB
    ## start here
    real_select = ""
    top_n_similar_conversations = get_top_n_similar_conversations(user_message, collection, 6)
    for conversation in top_n_similar_conversations:
        message = conversation["message"]
        response = conversation["response"]
        context = "User: " + message +"\nBot: " + response
        real_select += context + "\n"
    ## end here
    prompt = f'\nHistory:{real_select} User: {user_message}\nBot:'
    bot_response = send_message(prompt)
    print(prompt + "  " + bot_response)
    store_history(user_message, bot_response)
    return bot_response


#Can you remember NLP models you had mentioned in early coversation?