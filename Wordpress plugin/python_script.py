import sys
import re
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig, AutoModel

def respond_to_user_local_model(model_name: str, message: str):
    config = AutoConfig.from_pretrained(f"{model_name}/{model_name}-config", cache_dir=None)
    tokenizer = AutoTokenizer.from_pretrained(f"{model_name}/{model_name}", cache_dir=None)
    model = AutoModel.from_pretrained(f"{model_name}/{model_name}", config=config, cache_dir=None)
    input_ids = tokenizer.encode(message, return_tensors="pt")
    output = model.generate(input_ids)    
    decoded_output = tokenizer.decode(output[0])
    return decoded_output

def respond_to_user_model_download(model_name: str, message: str):
    tokenizer = AutoTokenizer.from_pretrained(f"{model_name}")
    model = AutoModelForCausalLM.from_pretrained(f"{model_name}")
    input_ids = tokenizer.encode(message, return_tensors="pt")
    output = model.generate(input_ids, max_length=50, num_beams=5, no_repeat_ngram_size=2, early_stopping=True)    
    decoded_output = tokenizer.decode(output[0], skip_special_tokens=True)
    return decoded_output

def generate_response(message):
    print("Do you want to use a model stored locally (type \"1\") or choose a model from the kobold horde (type \"2\") ?")
    answer = input()
    #user locally stored model
    if (answer=="1"):
        print("Please give name of the represtantion of the model challenge folder. This can be a suffix if you want to create multiple variations of the same model.")
        model_name = input()
        if (model_name[0] == '_'):
            model_name = model_name[1:]
        print(respond_to_user_local_model(model_name, message))
    #user model from kobold horde    
    elif (answer == "2"):
        print("Please give the exact name of the model to be downloaded from kobold horde and used to generate a response as it is listed there.")
        model_name = input()
        if (model_name[0] == '_'):
            model_name = model_name[1:]
        print(respond_to_user_model_download(model_name, message))
    else:
        print("You did not give 1 or 2 as an option. So we assume you want to use the default model included in this script. You can access that at any time without providing any inputs by simply running it without any arguments")
        model_name = "tekkithorse/GPT-J-6B-PNY-GGML"
        tokenizer = AutoTokenizer.from_pretrained(f"{model_name}")
        model = AutoModelForCausalLM.from_pretrained(f"{model_name}")
        input_ids = tokenizer.encode(message, return_tensors="pt")
        output = model.generate(input_ids, max_length=50, num_beams=5, no_repeat_ngram_size=2, early_stopping=True)
        decoded_output = tokenizer.decode(output[0], skip_special_tokens=True)
        return decoded_output

# Get the input message from the first command line argument
if (len(sys.argv)==1):
    print("No input given. Using default model to generate a greeting")
    response = generate_response("こんにちは")
    input_message = "MSG:"+response
else:
    input_message = sys.argv[1]
if "MSG:" not in input_message:
    input_message = "MSG:"+input_message
if not re.match(r"[^\x01-\x7F]+$", input_message):
    input_message = japanizer.japanize(input_message)
    input_message = input_message.replace(" ", "%20")
    print("Charset interpreted as non Japanese,  using a Japanese language model anyway but translating input. Note that for input in other languages you cant use this script because it would not make any sense.")
response = generate_response(input_message[4:])
print(response)
