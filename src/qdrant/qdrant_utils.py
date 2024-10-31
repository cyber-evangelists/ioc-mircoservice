from qdrant_client import QdrantClient
import time
from qdrant_client.models import Distance, VectorParams, PointStruct, FilterSelector

class QdrantWrapper:
    def __init__(self, collection_name="threadmon-reports-ioc"):
        self.host = "qdrant"
        self.port = 6333
        self.max_retries = 5
        self.retry_delay = 5  # seconds
        self.client = None
        self.collection_name = collection_name
        self._connect_with_retry()


    def _connect_with_retry(self):
        """Establish connection to Qdrant with retry logic"""
        for attempt in range(self.max_retries):
            try:
                print(f"Attempting to connect to Qdrant at {self.host}:{self.port} (Attempt {attempt + 1}/{self.max_retries})")
                self.client = QdrantClient(
                    host=self.host,
                    port=self.port,
                    timeout=60  # Increased timeout for stability
                )
                # Test connection by calling an API
                self.client.get_collections()
                print("Successfully connected to Qdrant")
                self._create_collection_if_not_exists()
                break
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    raise Exception(f"Failed to connect to Qdrant after {self.max_retries} attempts")


    def _create_collection_if_not_exists(self):
        collections = self.client.get_collections().collections
        if not any(collection.name == self.collection_name for collection in collections):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            print("Collection is Created")
        else:
            print("Collection already exists")
                
    def clear_collection(self):
        """
        Deletes all vectors/points from the collection while keeping the collection structure.
        """
        try:
            
            # Delete all points in the collection

            if self.client:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector= FilterSelector(filter=None)  # No filter means delete all points
                )
                print(f"Successfully cleared all vectors from collection: {self.collection_name}")
        except Exception as e:
            print(f"Error clearing collection: {e}")

    def ingest_embeddings(self, docs):

        points = [
            PointStruct(
                id=i,
                vector=doc["embeddings"],
                payload={"text": doc["text"], "document": doc["document"]}
            )
            for i, doc in enumerate(docs)
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(self, query_vector, limit=5):
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        return [
            {"document": hit.payload["document"], "content": hit.payload["text"]}
            for hit in search_result
        ]



# docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant:v0.10.1