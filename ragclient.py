import os
from loguru import logger
import time
import grpc
import rag_service_pb2_grpc as pb2_grpc
import rag_service_pb2 as pb2



class RAGClient:
    def __init__(self):
        # Get host and port from environment variables
        self.host = os.getenv('SERVER_HOST', 'rag-server')
        self.port = int(os.getenv('SERVER_PORT', '50051'))
        self.channel = None
        self.stub = None
        self._is_connected = False
        
        # Initial connection attempt
        self.connect()

    def connect(self) -> bool:
        """Establish connection to the gRPC server"""
        try:
            if self.channel is not None:
                self.channel.close()
            

            logger.info(f"Connecting to RAG service at {self.host}:{self.port}")

            self.channel = grpc.insecure_channel(f'{self.host}:{self.port}')
            time.sleep(30)
            
            # Wait for channel to be ready with a timeout
            grpc.channel_ready_future(self.channel).result(timeout=30)
            
            self.stub = pb2_grpc.RAGServiceStub(self.channel)
            self._is_connected = True
            logger.info("Successfully connected to RAG service")
            return True
            
        except grpc.FutureTimeoutError:
            logger.error(f"Timeout while connecting to RAG service at {self.host}:{self.port}")
            self._is_connected = False
            return False
        except Exception as e:
            logger.error(f"Failed to connect to RAG service: {e}")
            self._is_connected = False
            return False
    
 
    def get_response(self, query: str) -> str:
        """Get response from RAG service"""
        if not self._is_connected:
            self.connect()
        
        try:
            logger.info("Sending request to server....")
            request = pb2.QueryRequest(query=query)
            response =  self.stub.GetResponse(request)
            return response.response
        except grpc.RpcError as e:
            logger.error(f"RPC failed: {e}")
            return "Error: Could not connect to RAG service"
        except Exception as e:
            logger.error(f"Unexpected error in get_response: {e}")
            return "Error: An unexpected error occurred"