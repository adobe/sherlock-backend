import sys

sys.path.append('')
from qa_pipeline.retriever_node import RetrieverNode
from qa_pipeline.query_ehancer_node import QueryEnhancer
from qa_pipeline.llm_brain_node import LLMBrainNode


class QAPipeline:

    def __init__(self):
        self.retriever = RetrieverNode()
        self.enhancer = QueryEnhancer()
        self.llm = LLMBrainNode()

    def run(self, query, enhance=True, prompt_template=None):
        enhanced_query = query if enhance is False else self.enhancer.enhance_query(query)
        relevant_docs = []#self.retriever.retrieve(enhanced_query, methods=('keywords',))
        answer = self.llm.run(query, relevant_docs, template=prompt_template)
        return answer


if __name__ == '__main__':
    pipeline = QAPipeline()
    print(pipeline.run("Синонімічним до речення «Коли в людини є народ, тоді вона уже людина» є\n"
                       "Варіант A. Щоб відчувати себе людиною, треба мати підтримку свого народу.\n"
                       "Варіант Б. Оскільки в людини є народ, то вона вже людина.\n"
                       "Варіант В. Через те що в людини є народ, вона почуває себе людиною.\n"
                       "Варіант Г. Аби бути людиною, треба бути частиною рідного народу.\n"
                       "Варіант Д. Якщо в людини є народ, то вона тоді вже людина.\n"))
