"""Document ingestion pipeline with chunking and embedding."""
import asyncio
from pathlib import Path
from typing import List, Dict
import hashlib
from sentence_transformers import SentenceTransformer
import tiktoken

class DocumentIngestion:
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ):
        self.model = SentenceTransformer(embedding_model)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """Split text into overlapping chunks."""
        tokens = self.tokenizer.encode(text)
        chunks = []

        start = 0
        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)

            chunk_id = hashlib.sha256(
                (metadata['source'] + str(start)).encode()
            ).hexdigest()[:16]

            chunks.append({
                'id': chunk_id,
                'text': chunk_text,
                'metadata': {
                    **metadata,
                    'chunk_index': len(chunks),
                    'start_char': start
                }
            })

            start += self.chunk_size - self.chunk_overlap

        return chunks

    async def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Generate embeddings for text chunks."""
        texts = [c['text'] for c in chunks]

        # Batch embedding for efficiency
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )

        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding.tolist()

        return chunks

    async def ingest_document(
        self,
        file_path: Path,
        vector_db_client,
        collection_name: str = "knowledge_base"
    ):
        """Full ingestion pipeline for a single document."""
        # Read document
        text = file_path.read_text(encoding='utf-8')

        metadata = {
            'source': str(file_path),
            'filename': file_path.name,
            'type': file_path.suffix
        }

        # Chunk
        chunks = self.chunk_text(text, metadata)
        print(f"Created {len(chunks)} chunks from {file_path.name}")

        # Embed
        chunks_with_embeddings = await self.embed_chunks(chunks)

        # Upsert to vector DB
        await vector_db_client.upsert(
            collection_name=collection_name,
            documents=[
                {
                    'id': c['id'],
                    'embedding': c['embedding'],
                    'text': c['text'],
                    'metadata': c['metadata']
                }
                for c in chunks_with_embeddings
            ]
        )

        return len(chunks)

    async def ingest_directory(
        self,
        dir_path: Path,
        vector_db_client,
        extensions: List[str] = ['.txt', '.md', '.pdf']
    ):
        """Ingest all documents in a directory."""
        files = [
            f for f in dir_path.rglob('*')
            if f.suffix in extensions
        ]

        total_chunks = 0
        for file_path in files:
            try:
                chunks = await self.ingest_document(file_path, vector_db_client)
                total_chunks += chunks
            except Exception as e:
                print(f"Error ingesting {file_path}: {e}")

        print(f"Ingestion complete: {len(files)} files, {total_chunks} chunks")
        return total_chunks
