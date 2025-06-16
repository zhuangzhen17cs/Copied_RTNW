import Utils
import Chroma_func
import importlib
importlib.reload(Utils)  # This will print "Utils.py is loaded" again
importlib.reload(Chroma_func)

import bm25s
import Stemmer  # optional: for stemming

def get_corpus(collection_name):
    collection = Chroma_func.get_collection(collection_name)
    corpus = collection.get()['documents']
    return corpus

def get_bm25_results(query, corpus, n=5):
    stemmer = Stemmer.Stemmer('english')
    
    # Tokenize the corpus and only keep the ids (faster and saves memory)
    corpus_tokens = bm25s.tokenize(corpus, stopwords="en", stemmer=stemmer)

    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)

    query_tokens = bm25s.tokenize(query, stemmer=stemmer)

    # Get top-k results as a tuple of (doc ids, scores). Both are arrays of shape (n_queries, k).
    # To return docs instead of IDs, set the `corpus=corpus` parameter.
    results_bm25s, scores = retriever.retrieve(query_tokens, k=n)

    ret_list_dicts = []

    for i in range(results_bm25s.shape[1]):
        doc, score = results_bm25s[0, i], scores[0, i]
        ret_dict = {'id': Utils.generate_sha256_id(corpus[doc]),'score': score, 'rank': i+1, 'text': corpus[doc]}
        print(f"Rank {i+1} (score: {score:.2f}): {doc}: {corpus[doc][:50]}")
        ret_list_dicts.append(ret_dict)


    return ret_list_dicts
