from llama_cpp import Llama

context_size = 8192

llm = Llama(
    model_path="models/mistral-7b-uk/gemma-7b-it-Q4_K_M.gguf",
    chat_format="mistral",
    n_gpu_layers=33,
    n_ctx=context_size
)


def call_llm(prompt, max_tokens: int = 512):
    global llm
    llm.verbose = False
    rez = llm.create_completion("<s>[INST]" + prompt + "[/INST]", max_tokens=max_tokens, seed=1234, temperature=0.8)
    return rez['choices'][0]['text'].strip()


def tokenize(text):
    global llm
    return llm.tokenize(text.encode(encoding='utf-8'))


def detokenize(tokens):
    global llm
    return llm.detokenize(tokens).decode(encoding='utf-8')
