# client.py
import grpc
import src.grpc_files.rag_service_pb2_grpc as pb2_grpc
import src.grpc_files.rag_service_pb2 as pb2
import time
import sys
import gradio as gr
import os
from typing import Tuple, List, Optional
from loguru import logger
from src.utils.ragclient import RAGClient

class ChatbotUI:
    def __init__(self):
        self.rag_client = RAGClient()
        self.max_history = 50  # Maximum number of messages to keep
    
    def handle_search(
        self, 
        query: str, 
        history: Optional[List[Tuple[str, str]]]
    ) -> Tuple[str, List[Tuple[str, str]]]:
        """Handle search requests and update chat history"""
        if not query or not query.strip():
            return "", history or []
        
        try:
            query = query.strip()
            response = self.rag_client.get_response(query)
            
            history = history or []
            history.append((query, response))
            
            if len(history) > self.max_history:
                history = history[-self.max_history:]
            
            return "", history
        except Exception as e:
            logger.error(f"Error in handle_search: {e}")
            error_msg = "Sorry, an error occurred while processing your request."
            return "", (history or []) + [(query, error_msg)]
    
    def clear_chat(self) -> None:
        """Clear the chat history"""
        return None

    # def ingest_data(self) -> None:
    #     """Ingest data"""
    #     return None
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface"""
        with gr.Blocks(
            title="ASM Chatbot",
            theme=gr.themes.Soft(),
            css=".gradio-container {max-width: 800px; margin: auto}"
        ) as demo:
            gr.Markdown("""
            # ASM Chatbot
            Ask questions about ASM and get detailed responses.
            """)
            
            with gr.Row():
                msg = gr.Textbox(
                    label="Type your message here...",
                    placeholder="Enter your query",
                    show_label=True,
                    container=True,
                    scale=8
                )
            
            with gr.Row():
                search_btn = gr.Button("Search", variant="primary", scale=2)
                # ingest_data = gr.Button("Ingest Data", variant="primary", scale=1)
                clear_btn = gr.Button("Clear", variant="secondary", scale=1)
            
            chatbot = gr.Chatbot(
                height=400,
                show_label=False,
                container=True,
                elem_id="chatbot"
            )
            
            submit_click = search_btn.click(
                fn=self.handle_search,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot],
                api_name="search"
            )
            
            msg.submit(
                fn=self.handle_search,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot]
            )
            
            clear_btn.click(
                fn=self.clear_chat,
                inputs=[],
                outputs=[chatbot]
            )

            # ingest_data.click(
            #     fn=self.ingest_data,
            #     inputs=[],
            #     outputs=[]
            # )
                    
        return demo


def start_server_connection() -> bool:
    """Attempt to start server connection with retries, returns True if successful."""
    MAX_RETRIES = 5
    retry_count = 0
    
    while retry_count < MAX_RETRIES:
        try:
            channel = grpc.insecure_channel('rag-server:50051')
            try:
                grpc.channel_ready_future(channel).result(timeout=10)
            except grpc.FutureTimeoutError:
                logger.error("Error: Timeout while connecting to server. Server might be down or unreachable.")
                channel.close()
                retry_count += 1
                time.sleep(2)
                continue
                
            stub = pb2_grpc.RAGServiceStub(channel)
            request = pb2.QueryRequest(query="test")
            response = stub.GetResponse(request)
            logger.info("Connection successful!")
            return True
        except grpc.RpcError as e:
            logger.error(f"RPC failed with status code: {e.code()}. Details: {e.details()}")
            retry_count += 1
            time.sleep(2)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            retry_count += 1
            time.sleep(2)
        finally:
            if 'channel' in locals():
                channel.close()
    
    logger.error("Maximum retry attempts reached. Please check server status and network configuration.")
    return False


def launch_gradio_interface():
    """Launch the Gradio interface after server connection is established."""
    chatbot_ui = ChatbotUI()
    demo = chatbot_ui.create_interface()
    
    server_name = os.getenv('GRADIO_SERVER_NAME', '0.0.0.0')
    server_port = int(os.getenv('GRADIO_SERVER_PORT', '7860'))
    
    demo.launch(
        server_name=server_name,
        server_port=server_port,
        share=False,
        debug=True,
        show_error=True,
    )


if __name__ == "__main__":
    if start_server_connection():
        launch_gradio_interface()
