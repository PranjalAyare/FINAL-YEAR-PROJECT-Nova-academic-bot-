
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load the model **once** when the script starts
MODEL_PATH = r'C:\\Users\\PRANJAL\\Downloads\\AcadBot-main\\AcadBot-main - Copy\\gpt2_finetuned'

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)

def chatmodel(user_input):
    """Generates a response using the fine-tuned GPT-2 model with improved settings."""
    try:
        # Tokenize input
        input_ids = tokenizer.encode(user_input, return_tensors="pt")

        # Generate response with improved settings
        output = model.generate(
            input_ids, 
            max_length=200,          # Increase length to avoid truncation
            pad_token_id=tokenizer.eos_token_id,
            temperature=0.7,         # Balance between randomness and determinism
            top_p=0.9,               # Nucleus sampling to improve coherence
            do_sample=True,          # Enable stochastic sampling
            repetition_penalty=1.2,  # Reduce repetitive outputs
            num_return_sequences=1   # Generate only one response
        )

        # Decode response
        response = tokenizer.decode(output[:, input_ids.shape[-1]:][0], skip_special_tokens=True)

        return response.strip()
    
    except Exception as e:
        return f"⚠ Error: {str(e)}"
