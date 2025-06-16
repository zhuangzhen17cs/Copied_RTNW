import Utils

import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

import chromadb.utils.embedding_functions as embedding_functions

# Can use SentenceTransformer to get embeddings for sentences
# https://docs.trychroma.com/docs/embeddings/embedding-functions
# 3 as of 3/7/2025: "intfloat/multilingual-e5-large-instruct", but only 514 Max tokens!!!!
# https://huggingface.co/spaces/mteb/leaderboard
# https://huggingface.co/intfloat/multilingual-e5-large-instruct


sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="intfloat/multilingual-e5-large-instruct"
)

client = chromadb.PersistentClient(
    path="db",
    settings=Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
)

def get_collection(collection_name):
    collection = client.get_or_create_collection(name=collection_name,embedding_function=sentence_transformer_ef)
    return collection

def get_query_results(collection, querystr, n_results=10):    
    results = collection.query(query_texts=[querystr], n_results=n_results)
    return results