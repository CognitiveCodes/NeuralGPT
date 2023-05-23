import pinecone

# Initialize the Pinecone client library
pinecone.init(api_key="41ddf57b-2fc0-495c-9fff-47c6f6ff4e4e")

# Create a new index
pinecone.create_index(index_name="neuralai-a82b13f.svc.asia-northeast1-gcp.pinecone.io")

# Index some vectors
vectors = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
pinecone.index(index_name="neuralai-a82b13f.svc.asia-northeast1-gcp.pinecone.io", data=vectors)

# Search for similar vectors
query_vector = [2, 3, 4]
results = pinecone.query(index_name="neuralai-a82b13f.svc.asia-northeast1-gcp.pinecone.io", data=query_vector, top_k=10)

print(results)