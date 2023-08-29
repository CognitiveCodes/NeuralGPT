from transformers import GPT2LMHeadModel, GPT2Tokenizer

model_path = "E:/AI/NeuralGPT/NeuralGPT/models/gpt-j/"

tokenizer = GPT2Tokenizer.from_pretrained(model_path)

model = GPT2LMHeadModel.from_pretrained(model_path)

def generate_response(input_text):

    input_ids = tokenizer.encode(input_text, return_tensors="pt")

    output_ids = model.generate(input_ids, max_length=50, num_return_sequences=1)

    output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    return output_text


