# Warming up components
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.dataclasses import Document

doc = Document(content="I love koshari!")
doc_embedder = SentenceTransformersDocumentEmbedder()
doc_embedder.warm_up()

result = doc_embedder.run([doc])
print(result['documents'][0].embedding)