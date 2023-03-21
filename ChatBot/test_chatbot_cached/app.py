import openai
from flask import Flask, render_template, request
from flask_caching import Cache

# Set up the OpenAI API credentials
openai.api_key = "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"

# Set up the caching system
config = {
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 300  # 5 minutes
}
cache = Cache(config=config)

app = Flask(__name__, template_folder='template')
cache.init_app(app)

@app.route("/")
def hello():
    return "Hello World"

@app.route("/use")
def use():
    return render_template('index.html')

@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg')
    bot_response = cache.get(user_text)
    if bot_response is None:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=user_text,
            max_tokens=200,
            n=1,
            stop=None,
            temperature=0.7
        )
        bot_response = response.choices[0].text.strip()
        cache.set(user_text, bot_response)
    return bot_response


if __name__ == "__main__":
    app.run(debug=True)


# import openai
# import pymongo
# from flask import Flask, request, jsonify, render_template

# app = Flask(__name__, template_folder='template')
# client = pymongo.MongoClient('mongodb://localhost:27017/')
# db = client['chatbot_db']

# openai.api_key = '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'
# model_engine = 'text-davinci-003'

# @app.route("/")
# def home():
#     return render_template('index.html')

# @app.route('/chatbot', methods=['POST'])
# def chatbot():
#     message = request.args.get('message-input')
#     username = "user1"
#     chat_history = db.chat_history.find_one({'username': username})
#     if chat_history is not None:
#         context = chat_history['context']
#     else:
#         context = ''
#     prompt = f"{context}{username}: {message}\nAI:"
#     response = openai.Completion.create(
#         engine=model_engine,
#         prompt=prompt,
#         max_tokens=1024,
#         n=1,
#         stop=None,
#         temperature=0.5,
#     )
#     bot_response = response.choices[0].text.strip()
#     db.chat_history.update_one({'username': username}, {'$set': {'context': prompt}}, upsert=True)
#     return jsonify({'message': bot_response})

# if __name__ == '__main__':
#     app.run()