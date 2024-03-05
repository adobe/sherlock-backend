from opensearchpy import OpenSearch

host = '127.0.0.1'
port = 9200
auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.

client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_auth=auth,
    http_compress=True,  # enables gzip compression for request bodies
    use_ssl=False,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False
)

if __name__ == "__main__":
    index_name = 'ukrainian'
    index_body = {
        'settings': {
            'index': {
                'number_of_shards': 1
            }
        }
    }

    client.indices.create(index_name, body=index_body)
