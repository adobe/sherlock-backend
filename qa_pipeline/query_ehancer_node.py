from qa_pipeline.llm_utils import call_llm


class QueryEnhancer:

    """This Node will try to enrich/transform the query for better retrieval"""

    # Enhancing query can be simple with one  LLM call or much complicated
    def enhance_query(self, query, method='simple_enhancement'):
        if method == 'simple_enhancement':
            return self.enhance_query_simple(query)
        return query

    # Enhance query with one LLM call. Maybe we can also add related keywords and stuff.
    def enhance_query_simple(self, query):
        with open('prompts/simple_enhancement.txt') as f:
            enhancement_prompt = f.read()
        enhancement_prompt = enhancement_prompt.format(query=query)
        query = call_llm(enhancement_prompt)
        return query
