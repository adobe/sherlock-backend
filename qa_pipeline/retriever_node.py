import sys
import copy
import tqdm

sys.path.append('')
from qa_pipeline.llm_utils import call_llm
from ingest.db_utils import search
import re


class RetrieverNode:

    def __init__(self, top_k=5):
        # Add DB connection params
        self.DB_HOST = None
        self._top_k = top_k

    def retrieve(self, query, methods=("keywords",)):
        relevant_text = []
        if "keywords" in methods:
            relevant_text.extend(self.retrieve_by_keywords(query))

        return relevant_text

    def retrieve_by_keywords(self, query):
        return self.retrieve_keywords(query)

    def retrieve_keywords(self, query):
        prompt_lang = 'en'
        prompt_steps = open(f'prompts/retrieve_get_steps_{prompt_lang}.txt').read()
        prompt_ngrams = open(f'prompts/retrieve_get_ngrams_{prompt_lang}.txt').read()

        prompt = prompt_steps.replace('{query}', query)
        matched_content = []
        print("\033[93m" + prompt + "\033[0m")
        response = call_llm(prompt)
        print("\033[92mExtracted steps are : \033[0m")
        print("\033[92m" + response + "\033[0m")

        parts = response.split('\n')
        for part in parts:
            prompt = prompt_ngrams.replace('{query}', query).replace('{step}', part)

            print("\033[93m" + prompt + "\033[0m")

            response2 = call_llm(prompt)
            # extract search terms
            print("\033[92mStep" + part + "\033[0m")

            pp = response2.split('\n')
            unigrams = pp[0].split(':')[-1].strip()
            if len(pp) > 1:
                bigrams = pp[1].split(':')[-1].strip()
            else:
                bigrams = []
            if len(pp) > 2:
                trigrams = pp[2].split(':')[-1].strip()
            else:
                trigrams = []

            print(f"\033[92m Unigrams : {unigrams}\033[0m")
            print(f"\033[92m Bigrams : {bigrams}\033[0m")
            print(f"\033[92m Trigrams : {trigrams}\033[0m")
            unigrams = _tolist(unigrams)
            bigrams = _tolist(bigrams)
            trigrams = _tolist(trigrams)
            documents = search(' '.join(unigrams + bigrams + trigrams), "ukrainian2")
            reranked_documents = _rerank(documents, unigrams, bigrams, trigrams)

            rr_top = self._top_k // 2
            nr_top = self._top_k // 2
            if self._top_k % 2 == 1:
                rr_top += 1
            final_documents = reranked_documents[:rr_top] + documents[:nr_top]
            print("\033[93mWill analyze the following documents:\033[0m")
            for ii in range(len(final_documents)):
                print(f"\033[93m\t{final_documents[ii]['title']}\033[0m")

            for ii in range(len(final_documents)):
                print(f"\033[92m Analyzing {ii + 1}/{len(final_documents)}: {final_documents[ii]['title']}\033[0m")

                buffer = self._extract_relevant_text(query, final_documents[ii]['title'],
                                                     final_documents[ii]['content'], prompt_lang)
                print(f"\t\tWrote down: {buffer}")

                if buffer.strip() != '':
                    if {'title': final_documents[ii]['title'], 'content': buffer} not in matched_content:  # sorry :(
                        matched_content.append({'title': final_documents[ii]['title'], 'content': buffer})

        return matched_content

    def _extract_relevant_text(self, query, title, content, prompt_lang):
        parts = content.split('\n')
        buffer = ""
        prompt_useful = open(f'prompts/retrieve_is_useful_{prompt_lang}.txt').read()
        for iip in tqdm.tqdm(range(len(parts)), ncols=80, desc="\t Processing paragraphs"):
            part = parts[iip]
            if part.strip() == '':
                continue
            prompt = prompt_useful.replace('{query}', query).replace('{title}', title).replace('{content}', part)
            try:
                write_down = call_llm(prompt, max_tokens=10)
                # filter out data
                if 'Так' in write_down:
                    buffer += part
            except Exception as e:
                print(f"Exception calling LLM - {e}")
        return buffer


def _tolist(text):
    text = str(text).strip()
    delim = ','
    if ';' in text:
        delim = ';'
    elif '\n' in text:
        delim = '\n'
    elif ',' not in text:
        delim = ' '
    parts = text.split(delim)
    return [part.strip() for part in parts]


def _rerank(documents, unigrams, bigrams, trigrams):
    new_docs = []
    for document in documents:
        new_doc = copy.deepcopy(document)
        new_doc['score'] = _score(document['title'], document['content'], unigrams, bigrams, trigrams)
        new_docs.append(new_doc)
    return list(sorted(new_docs, key=lambda d: d['score'], reverse=True))


def _ngram_score(ngram, words):
    score = 0
    ngram = ngram.lower()
    parts = ngram.split(' ')
    while len(words) > 0:
        try:
            f_index = words.index(parts[0])
        except:
            break
        # search for match
        if len(parts) == 1:
            score += 1
        else:
            match = True
            for p in parts[1:]:
                try:
                    f_index = words.index(p, f_index, min(f_index + 5, len(words)))
                except:
                    match = False  # no match
                    break
            if match:
                score += 1

        # move
        if f_index < len(words) - 1:
            words = words[f_index + 1:]
        else:
            break

    score = score * len(parts)
    return score


def _score(title, text, unigrams, bigrams, trigrams):
    new_text = re.sub('\W', ' ', text, flags=re.UNICODE).lower()
    tmp = new_text.replace('  ', ' ')
    while tmp != new_text:
        new_text = tmp
        tmp = new_text.replace('  ', ' ')

    new_title = re.sub('\W', ' ', title, flags=re.UNICODE).lower()
    tmp = new_text.replace('  ', ' ')
    while tmp != new_title:
        new_title = tmp
        tmp = new_title.replace('  ', ' ')

    words_content = new_text.strip().split(' ')
    words_title = new_title.strip().split(' ')
    score = 0
    for unigram in unigrams:
        score += _ngram_score(unigram, words_content)
        score += _ngram_score(unigram, words_title) * 10
    for bigram in bigrams:
        score += _ngram_score(bigram, words_content)
        score += _ngram_score(bigram, words_title) * 10
    for trigram in trigrams:
        score += _ngram_score(trigram, words_content)
        score += _ngram_score(trigram, words_title) * 10
    # from ipdb import set_trace
    # set_trace()
    return score


if __name__ == '__main__':
    _score("Елементи експресіонізму наявні у творі",
           "Елементи експресіонізму наявні у творі: (a) «Камінний хрест», (b) «Інститутка», (c) «Маруся»", ["Елементи"],
           ["Елементи наявні"], "Елементи експресіонізму наявні")
    rn = RetrieverNode()
    print(rn.retrieve_keywords(
        "Елементи експресіонізму наявні у творі: (a) «Камінний хрест», (b) «Інститутка», (c) «Маруся»"))
