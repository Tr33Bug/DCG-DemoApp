from flask import Flask, request, jsonify
import transformers
import torch

app = Flask(__name__)

## define run name
run_name = "finalTraining_v1"

# define model for tokenizer
model_name = "codellama/CodeLlama-7b-hf"

# model save path
model_save_path = "./models/" + run_name + "/"

# load quantization config
quantization_config = transformers.BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)

# load model
model = transformers.AutoModelForCausalLM.from_pretrained(model_save_path, quantization_config=quantization_config, low_cpu_mem_usage=True)

# load tokenizer
tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)

# add pad token
tokenizer.add_special_tokens({'pad_token': '[PAD]'})


def generate_donainlifecycles_dsl_json(model, tokenizer, prompt, seed=42, custom_eos_token="<END>", max_length=400):
    print(f"Generating response for prompt: {prompt}")
    # set a seed for generation
    torch.manual_seed(seed)

    input_ids = tokenizer.encode(prompt, return_tensors='pt')
    input_ids = input_ids.to('cuda')
    end_token_id = tokenizer.encode(custom_eos_token, add_special_tokens=False)[0]

    output = model.generate(input_ids, eos_token_id=end_token_id, temperature=0.1, max_length=max_length, do_sample=True, num_return_sequences=1)
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    
    # # delete <START> from generated text
    # generated_text = generated_text.replace("<START>", "")
    print(generated_text)
    
    # cleanup
    del output
    del input_ids
    torch.cuda.empty_cache()

    return generated_text

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data['message']
    response = generate_donainlifecycles_dsl_json(model, tokenizer, prompt, max_length=400)

    ## Generate 4k tokens
    # response = generate_donainlifecycles_dsl_json(model, tokenizer, prompt, max_length=4000)

    return jsonify({'response': response})

if __name__ == '__main__':
    # run on server
    app.run(host='0.0.0.0', port=5000)

    # run on local host
    # app.run(port=5000)
