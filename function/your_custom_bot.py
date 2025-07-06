import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from datetime import datetime

# Load the fine-tuned model and tokenizer
model_path = r'C:\\Users\\PRANJAL\\Downloads\\AcadBot-main\\AcadBot-main - Copy\\gpt2_finetuned'
model = GPT2LMHeadModel.from_pretrained(model_path)
tokenizer = GPT2Tokenizer.from_pretrained(model_path)
tokenizer.pad_token = tokenizer.eos_token

# Function to detect intent
def detect_intent(prompt_lower):
    intents = {
        "greeting": ["hi", "hello", "hey"],
        "name": ["what's your name", "what is your name", "who are you", "your name"],
        "wellbeing": ["how are you", "how are you doing"],
        "goodbye": ["goodbye", "bye", "see you"],
        "acknowledgment": ["ok", "alright", "thank you", "thanks"]
    }

    for intent, keywords in intents.items():
        if any(keyword in prompt_lower for keyword in keywords):
            return intent
    return None

# Function to generate response
def generate_response(prompt):
    prompt_lower = prompt.lower()
    intent = detect_intent(prompt_lower)

    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning!"
    elif 12 <= current_hour < 18:
        greeting = "Good afternoon!"
    else:
        greeting = "Good evening!"

    # Handle basic responses
    if intent == "greeting":
        return f"{greeting} How can I assist you today?"
    if intent == "wellbeing":
        return "I'm NOVA, your virtual assistant. I'm doing well! How about you?"
    if intent == "name":
        return "I'm NOVA, your AcadBot. How can I assist you today?"
    if intent == "goodbye":
        return "Goodbye! Have a great day!"
    if intent == "acknowledgment":
        return "You're welcome! Feel free to ask me anything."

    # If not a small talk response, generate a GPT-2 response
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(inputs['input_ids'], max_length=100, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return response.strip()
