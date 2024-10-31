# threatmon_parser.py
from typing import Dict, List, Optional, Union
from pathlib import Path
import os

from src.embedder.embedder import EmbeddingWrapper


class FileProcessor:
    """Process and manage YARA and IOC files for threat monitoring."""

    def __init__(self) -> None:
        """Initialize FileProcessor with required components."""
        self.embedder = EmbeddingWrapper()
        self.yara_extensions: tuple = ('.yar', '.yara')
        self.ioc_extensions: tuple = ('.txt',)
        self.files_found: Dict[str, List[Path]] = {
            'yara': [],
            'ioc': []
        }
        self.chunks: List[Dict[str, Any]] = []

    def read_file(self, file_path: Path) -> Optional[str]:
        """
        Read a file and return its contents as a string.

        Args:
            file_path: Path to the file to read

        Returns:
            Contents of the file as a string, or None if reading fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found")
            return None
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return None

    def find_all_files(self, root_directory: str) -> Dict[str, List[Path]]:
        """
        Recursively find all YARA and IOC files in the directory.

        Args:
            root_directory: Root directory to start the search

        Returns:
            Dictionary containing lists of found YARA and IOC files
        """
        root_path = Path(root_directory)
        
        # Reset files found
        self.files_found = {'yara': [], 'ioc': []}
        
        for file_path in root_path.rglob('*'):
            if file_path.is_file():
                if file_path.suffix.lower() in self.yara_extensions:
                    self.files_found['yara'].append(file_path)
                elif file_path.suffix.lower() in self.ioc_extensions:
                    self.files_found['ioc'].append(file_path)

        return self.files_found

    def process_file(self, file_path: Path, file_type: str) -> None:
        """
        Process a single file and add it to the chunks list.

        Args:
            file_path: Path to the file to process
            file_type: Type of file ('yara' or 'ioc')
        """
        content = self.read_file(file_path)
        file_name = self.extract_directory_name(file_path)

        if content:
            try:
                embeddings = self.embedder.generate_embeddings(content)
                chunk = {
                    "embeddings": embeddings,
                    "text": content,
                    "document": file_name
                }
                self.chunks.append(chunk)
            except Exception as e:
                print(f"Error processing {file_path.name}: {str(e)}")

    def extract_directory_name(self, file_path: Path) -> str:
        """
        Extract the directory name from a file path.

        Args:
            file_path: Path to the file

        Returns:
            Directory name without leading slash
        """
        directory_path = os.path.dirname(file_path)
        return directory_path.split("/")[-1]

    def process_all_files(self, root_directory: str) -> List[Dict[str, Any]]:
        """
        Process all YARA and IOC files in the directory and its subdirectories.

        Args:
            root_directory: Root directory containing the files

        Returns:
            List of dictionaries containing processed file data
        """
        self.chunks = []  # Reset chunks list at the start of processing
        files = self.find_all_files(root_directory)
        
        # Process all files
        for file_type, file_list in files.items():
            for file_path in file_list:
                self.process_file(file_path, file_type)

        return self.chunks