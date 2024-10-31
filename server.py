# server.py
from typing import Any
import grpc
from concurrent import futures
from loguru import logger

import src.grpc_files.rag_service_pb2_grpc as pb2_grpc
import src.grpc_files.rag_service_pb2 as pb2
from src.llm.groqwrapper import GroqWrapper
from src.embedder.embedder import EmbeddingWrapper
from src.qdrant.qdrant_utils import QdrantWrapper
from src.parser.threatmon_parser import FileProcessor
from src.utils.utils import prepare_prompt, rerank_docs


class RAGServiceServicer(pb2_grpc.RAGServiceServicer):
    """Implements the RAG (Retrieval-Augmented Generation) service."""

    def __init__(self) -> None:
        """Initialize the RAG service with required components and data ingestion."""
        self.groq_client = GroqWrapper()
        self.embedder = EmbeddingWrapper()
        self.qdrant_client = QdrantWrapper()

        logger.info("Ingesting Data")
        self.data_directory = "data/"
        self.processor = FileProcessor()
        processed_chunks = self.processor.process_all_files(self.data_directory)
        self.qdrant_client.ingest_embeddings(processed_chunks)
        logger.info("Successfully ingested Data")

    def GetResponse(
        self,
        request: pb2.QueryRequest,
        context: grpc.ServicerContext
    ) -> pb2.QueryResponse:
        """
        Process incoming queries and generate responses using RAG pipeline.

        Args:
            request: The incoming query request
            context: gRPC service context

        Returns:
            QueryResponse containing the generated response
        """
        try:
            logger.info("Processing request....")
            query = request.query

            logger.info("Generating Embeddings")
            query_embeddings = self.embedder.generate_embeddings(query)

            logger.info("Searching for top 5 results")
            top_5_results = self.qdrant_client.search(query_embeddings, 5)
            logger.info("Top 5 results received")

            logger.info("Re ranking documents")
            reranked_docs = rerank_docs(query, top_5_results)
            reranked_top_5_list = [item['content'] for item in reranked_docs]
            logger.info("Re ranked documents")

            # Context contains top 2 documents only
            context = " ".join(reranked_top_5_list[:2])
            query = prepare_prompt(query, context)

            logger.info("Generating Response")
            response = self.groq_client.get_response(query)

            return pb2.QueryResponse(response=response)
        except Exception as e:
            logger.error(f"Error in processing app request {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pb2.QueryResponse()


def serve() -> None:
    """
    Start and run the gRPC server with configured settings.
    """
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', 100 * 1024 * 1024),
            ('grpc.max_receive_message_length', 100 * 1024 * 1024)
        ]
    )
    pb2_grpc.add_RAGServiceServicer_to_server(RAGServiceServicer(), server)

    server_address = '[::]:50051'
    server.add_insecure_port(server_address)

    logger.info(f"Starting RAG gRPC server on {server_address}")
    server.start()

    try:
        logger.info("Server is running...")
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down server gracefully...")
        server.stop(0)


if __name__ == "__main__":
    serve()