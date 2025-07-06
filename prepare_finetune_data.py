import json

# Load the dataset
with open("C:\\Users\\PRANJAL\\Downloads\\AcadBot-main\\AcadBot-main - Copy\\archive\\intents.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Output file
output_file = "finetune_dataset.txt"

with open(output_file, "w", encoding="utf-8") as f:
    for intent in data["intents"]:
        tag = intent["tag"]
        responses = intent["responses"]

        for pattern in intent["patterns"]:
            # Choose one response randomly (or loop over responses)
            response = responses[0]

            # Formatting as a conversational dialogue
            formatted_text = f"User: {pattern}\nNOVA: {response}\n\n"
            f.write(formatted_text)

print(f"Dataset formatted and saved as '{output_file}'")
