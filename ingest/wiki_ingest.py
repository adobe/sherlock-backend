import os
import re
from tqdm import tqdm
from db_setup import client
import uuid
import multiprocessing


def process_file(file_path):
    results = []
    with open(file_path, 'r') as file:
        file_contents = file.read()
        articles = re.findall(r'<doc[^>]*>(.*?)<\/doc>', file_contents, re.DOTALL)
        for article in articles:
            lines = article.strip().split('\n')
            title = lines[0]
            client.index(index='ukrainian', body={"title": title, "content": article.strip()}, id=str(uuid.uuid4()))
    return results


if __name__ == "__main__":
    file_paths = []
    for root, dirs, files in os.walk('../Ukranian Dataset/text'):
        for file in files:
            file_paths.append(os.path.join(root, file))

    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        r = list(tqdm(pool.imap(process_file, file_paths), total=len(file_paths), desc=f"Ingesting uk wiki"))
