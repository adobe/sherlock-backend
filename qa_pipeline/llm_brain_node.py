from qa_pipeline.llm_utils import call_llm, tokenize, detokenize, context_size


class LLMBrainNode:
    """This Node will receive the query and relevant text and will do magic in different ways (chain of thought etc.)"""

    def run(self, query, related_docs, method="simple", template=None):
        if method == "simple":
            return self.run_simple(query, related_docs, template=template)
        return "IDK BRO (in ukrainian)"

    def run_simple(self, query, related_docs, template=None):
        if template is None:
            template = 'prompts/simple_prompt.txt'
        with open(template) as f:
            prompt = f.read()

        prompt_tokens = tokenize(prompt)
        docs_tokens = tokenize(
            '\n\n'.join(['Назва: ' + x['title'] + '\n' + 'Зміст: ' + x['content'] + '\n' for x in related_docs]))
        query_tokens = tokenize(query)
        if len(docs_tokens) + len(prompt_tokens) + len(query_tokens) >= context_size - 512:
            # truncate docs tokens
            docs_tokens = docs_tokens[:int(context_size - len(prompt_tokens) - len(query_tokens) - 512)]

        prompt = prompt.format(query=query,
                               docs=detokenize(docs_tokens))
        print(prompt)
        answer = call_llm(prompt)
        return answer
