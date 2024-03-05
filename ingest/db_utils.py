from ingest.db_setup import client
import spacy
from tqdm import tqdm
import fitz
import os
import uuid


# nlp = spacy.load("uk_core_news_sm")


def ingest_text_from_pdf(filename, pdf_path, index, nlp):
    text = ""
    with fitz.open(pdf_path) as pdf_doc:
        for page_num in range(pdf_doc.page_count):
            page = pdf_doc[page_num]
            text = page.get_text("text")
            ingest_text(filename, text, index, nlp)

    return text


def ingest_folder(path, index, nlp):
    for subject in os.listdir(path):
        if subject == 'Ukrainian literature':
            subject_folder = os.path.join(path, subject)
            for file in os.listdir(subject_folder):
                f_path = os.path.join(subject_folder, file)
                ingest_text_from_pdf(file, f_path, index, nlp)


def group_sentences(sentences, max_length):
    chunks, current_chunk, current_length = [], [], 0

    for sentence in sentences:
        if current_length + len(sentence) <= max_length:
            current_chunk += [sentence]
            current_length += len(sentence)
        else:
            chunks += ["".join(current_chunk)]
            current_chunk, current_length = [sentence], len(sentence)

    if current_chunk:
        chunks += ["".join(current_chunk)]

    return chunks


def ingest_text(title, content, index, nlp, max_ch_length=-1, lang="uk"):
    if max_ch_length != -1:
        doc = nlp(content)
        sentences = [sent.text for sent in doc.sents]
        texts = group_sentences(sentences, max_ch_length)
    else:
        texts = [content]

    documents = [{"title": title, "content": txt} for txt in texts]
    for document in tqdm(documents, desc=f"Ingesting: {title}", unit="chunk"):
        client.index(index=index, body=document, id=str(uuid.uuid4()), refresh=True)


def search(q, index, top_k=100):
    query = {
        'size': top_k,
        'query': {
            'multi_match': {
                'query': q,
                'fields': ['title', 'content']
            }
        }
    }
    response = client.search(
        body=query,
        index=index,
    )

    hits = response['hits']['hits']
    documents = []
    for hit in hits:
        score = hit['_score']
        hit = hit['_source']
        title = "No title"
        if 'title' in hit:
            title = hit['title']
        content = ''
        if 'content' in hit:
            content = hit['content']

        documents.append({"title": title,
                          "content": content,
                          "score": score})

    return documents


if __name__ == "__main__":
    # ingest_text_from_pdf('Ukrainian literature v1 - 11.pdf',
    #                      '../Ukranian Dataset/Ukrainian literature/NEW HANDBOOK: UKRAINIAN LANGUAGE. UKRAINIAN LITERATURE.pdf',
    #                      'ukrainian', nlp)
    # ingest_folder('../Ukranian Dataset', 'ukrainian', nlp)
    print('started')
    results = search('Елементи експресіонізму наявні у творі «LКамінний хрест»', 'ukrainian')
    print(results)
