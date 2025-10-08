from chromadb import PersistentClient
from typing import List, Dict

class VectorStore:
    def __init__(self, persist_directory="chroma_db", collection_name="user_answers"):
        self.client = PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_documents(self, docs: List[Dict]):
        ids = [doc["id"] for doc in docs]
        embeddings = [doc["embedding"] for doc in docs]
        metadatas = [doc["metadata"] for doc in docs]
        documents = [doc["metadata"]["answer_text"] for doc in docs]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

    def similarity_search(self, embedding: List[float], top_k: int = 5):
        return self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )


# from chromadb import PersistentClient
# from typing import List, Dict




# class VectorStore:
#     def __init__(self, persist_directory="chroma_db", collection_name="user_answers"):
#         self.client = PersistentClient(path=persist_directory)
#         self.collection = self.client.get_or_create_collection(name=collection_name)

#     def document_exists(self, doc_id: str) -> bool:
#         results = self.collection.get(ids=[doc_id])
#         return len(results['ids']) > 0

#     def add_documents(self, docs: List[Dict]):
#         new_docs = []
#         for doc in docs:
#             if not self.document_exists(doc['id']):
#                 new_docs.append(doc)

#         if not new_docs:
#             print("No new documents to add.")
#             return

#         ids = [doc["id"] for doc in new_docs]
#         embeddings = [doc["embedding"] for doc in new_docs]
#         metadatas = [doc["metadata"] for doc in new_docs]
#         documents = [doc["metadata"].get("answer_text", "") for doc in new_docs]

#         self.collection.add(
#             ids=ids,
#             embeddings=embeddings,
#             metadatas=metadatas,
#             documents=documents
#         )
#         self.client.persist()

#     def similarity_search(self, embedding: List[float], top_k: int = 5):
#         return self.collection.query(
#             query_embeddings=[embedding],
#             n_results=top_k
#         )