from flask import Flask, render_template, request, jsonify
from transformers import pipeline
from textblob import TextBlob

app = Flask(__name__)

# Use your Hugging Face API key here
API_KEY = ""

# Initialize the text generation pipeline with GPT-J using the API key
generator = pipeline('text-generation', model='EleutherAI/gpt-j-6B', use_auth_token=API_KEY)

# Define the global conversation state
conversation_state = {"step": 0, "favorite_dishes": [], "suggested_dish": ""}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    step = conversation_state["step"]

    if step == 0:
        conversation_state["favorite_dishes"].append(user_input)
        if len(conversation_state["favorite_dishes"]) < 3:
            return jsonify({'response': f"Great! Please tell me another favorite dish."})
        else:
            dishes = ", ".join(conversation_state["favorite_dishes"])
            # Use TextBlob to process the input and provide basic correction
            blob = TextBlob(dishes)
            corrected_dishes = str(blob.correct())
            
            # Generate a suggestion based on the favorite dishes
            suggestion_prompt = f"Based on the favorite dishes: {corrected_dishes}, suggest a similar dish that uses similar ingredients."
            suggestions = generator(suggestion_prompt, max_length=100, num_return_sequences=1, truncation=True)
            suggested_dish = suggestions[0]['generated_text']
            conversation_state["suggested_dish"] = suggested_dish
            conversation_state["step"] = 1
            return jsonify({'response': f"Based on your favorite dishes, I suggest: {suggested_dish}. Would you like a recipe for this dish? (yes/no)"})

    elif step == 1:
        if user_input.lower() == "yes":
            dish = conversation_state["suggested_dish"]
            recipe_prompt = f"Create a detailed recipe for the dish: {dish}. Include instructions for cooking."
            recipe = generator(recipe_prompt, max_length=200, num_return_sequences=1, truncation=True)
            generated_recipe = recipe[0]['generated_text']
            return jsonify({'response': f"Here’s the recipe for {dish}: {generated_recipe}"})
        else:
            conversation_state["step"] = 0
            conversation_state["favorite_dishes"].clear()
            conversation_state["suggested_dish"] = ""
            return jsonify({'response': "No problem! Let's start over. Please tell me your first favorite dish."})

if __name__ == '__main__':
    app.run(debug=True)
