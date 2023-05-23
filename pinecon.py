import pinecone

pinecone.init(api_key="b372ae78-2b81-49bb-9f4d-d3c3e833921d")

# Create a new index
pinecone.create_index(index_name="my_index")

# Index some vectors
vectors = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
pinecone.index(index_name="my_index", data=vectors)

# Search for similar vectors
query_vector = [2, 3, 4]
results = pinecone.query(index_name="my_index", data=query_vector, top_k=10)

print(results)