from fetchers import WikiFetcher
from parsers import WikiSectionParser
from storers import PineconeStorer
from model_connectors import GoogleEmbeddingAdapter
import os
from dotenv import load_dotenv

load_dotenv()

print('fetching laws...')
#TODO: change to fetch_all() in production
laws = WikiFetcher.test_fetch_all()
print('laws fetched successfuly')
chunks = []
for law in laws:
    chuck_item = WikiSectionParser.parse(law['content'])
    chunks.extend(chuck_item)
print('laws chunked successfuly')

adapter = GoogleEmbeddingAdapter(api_key=os.getenv('GOOGLE_API_KEY'))

embedding_dimension = 768

print('initialize storer...')
storer = PineconeStorer(
    api_key=os.getenv('PINECONE_API_KEY'), 
    dimension=embedding_dimension,
    embedding_adapter=adapter
    )
print('storer initialized successfuly')
print('storing in Pinecone DB')
results = storer.store(chunks)
print('storing completed successfuly')
