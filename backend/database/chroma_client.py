import logging
import chromadb
from chromadb.config import Settings
from config import Config

logger = logging.getLogger(__name__)

class ChromaManager:
    """
    ChromaDB manager for vector storage operations.
    Handles collection creation, document storage, and similarity search.
    """

    def __init__(self):
        """Initialize ChromaDB client."""
        self.client = chromadb.PersistentClient(
            path=str(Config.CHROMA_DB_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collections = {}
        logger.info(f'ChromaDB initialized at {Config.CHROMA_DB_DIR}')

    def _get_or_create_collection(self, collection_name: str = "documents"):
        """Get existing collection or create new one."""
        if collection_name not in self.collections:
            self.collections[collection_name] = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f'Collection loaded/created: {collection_name}')
        return self.collections[collection_name]
    
    def add_documents(
        self,
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
        ids: list[str],
        collection_name: str = "documents"
    ) -> None:
        """
        Add documents with embeddings to the collection.

        Args:
            documents: List of text chunks
            embeddings: List of embedding vectors
            metadatas: List of metadata dicts
            ids: List of unique document IDs
            collection_name: Name of the collection to add to
        """
        try:
            collection = self._get_or_create_collection(collection_name)
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f'Added {len(documents)} documents to collection {collection_name}')
        except Exception as e:
            logger.exception(f'Failed to add documents: {e}')
            raise
    
    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        collection_names: list[str] = None,
        metadata_filter: dict = None
    ) -> dict:
        """
        Perform similarity search using query embedding across collections.

        Args:
            query_embedding: Query vector
            top_k: Number of results to return per collection
            collection_names: List of collection names to search (None = all)
            metadata_filter: Optional metadata filter for ChromaDB

        Returns:
            dict: Search results with documents, metadatas, distances
        """
        try:
            all_documents = []
            all_metadatas = []
            all_distances = []

            if collection_names is None:
                collection_names = list(self.client.list_collections())
                collection_names = [c.name for c in collection_names] if collection_names else []

            if not collection_names:
                return {'documents': [], 'metadatas': [], 'distances': []}

            for coll_name in collection_names:
                try:
                    collection = self._get_or_create_collection(coll_name)

                    query_kwargs = {
                        'query_embeddings': [query_embedding],
                        'n_results': top_k
                    }

                    if metadata_filter:
                        query_kwargs['where'] = metadata_filter

                    results = collection.query(**query_kwargs)

                    if results['documents'] and results['documents'][0]:
                        all_documents.extend(results['documents'][0])
                        all_metadatas.extend(results['metadatas'][0])
                        all_distances.extend(results['distances'][0])
                except Exception as e:
                    logger.warning(f'Failed to search collection {coll_name}: {e}')
                    continue

            sorted_results = sorted(
                zip(all_documents, all_metadatas, all_distances),
                key=lambda x: x[2]
            )[:top_k]

            if sorted_results:
                all_documents, all_metadatas, all_distances = zip(*sorted_results)
                all_documents = list(all_documents)
                all_metadatas = list(all_metadatas)
                all_distances = list(all_distances)
            else:
                all_documents, all_metadatas, all_distances = [], [], []

            logger.info(f'Similarity search returned {len(all_documents)} results')

            return {
                'documents': all_documents,
                'metadatas': all_metadatas,
                'distances': all_distances
            }
        except Exception as e:
            logger.exception(f'Similarity search failed: {e}')
            raise
    
    def get_count(self, collection_name: str = "documents") -> int:
        """Get total number of documents in collection."""
        collection = self._get_or_create_collection(collection_name)
        return collection.count()

    def delete_collection(self, collection_name: str) -> None:
        """Delete a specific collection."""
        try:
            self.client.delete_collection(collection_name)
            if collection_name in self.collections:
                del self.collections[collection_name]
            logger.info(f'Collection deleted: {collection_name}')
        except Exception as e:
            logger.exception(f'Failed to delete collection {collection_name}: {e}')
            raise

    def get_all_collections(self) -> list[str]:
        """Get list of all collection names."""
        collections = self.client.list_collections()
        return [c.name for c in collections] if collections else []
