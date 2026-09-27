import json
from pathlib import Path

import faiss
import numpy as np
import logging
import warnings

warnings.filterwarnings("ignore")

logging.getLogger("pypdf").setLevel(logging.ERROR)

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


class Researcher:

    def __init__(
        self,
        client,
        pdf_path=None
    ):

        self.client = client

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        self.pdf_path = (
            Path(pdf_path)
            if pdf_path
            else None
        )

        self.chunks = []
        self.metadata = []

        self.index = None

        if self.pdf_path and self.pdf_path.exists():

            print(
                f"Loading knowledge base: {self.pdf_path}",
                flush=True
            )

            self._build_index(
                [self.pdf_path]
            )


    # ========================================================
    # PDF PROCESSING
    # ========================================================

    def _extract_pdf_text(
        self,
        pdf_path
    ):

        print(
            f"Reading PDF: {pdf_path.name}",
            flush=True
        )

        reader = PdfReader(
            str(pdf_path)
        )

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = page.extract_text()

            if text:

                pages.append(
                    {
                        "page": page_number,
                        "text": text
                    }
                )

        return pages


    def _chunk_text(
        self,
        text,
        chunk_size=800,
        overlap=120
    ):

        words = text.split()

        if not words:
            return []

        chunks = []

        start = 0

        while start < len(words):

            end = min(
                start + chunk_size,
                len(words)
            )

            chunk = " ".join(
                words[start:end]
            )

            chunks.append(chunk)

            if end == len(words):
                break

            start = end - overlap

        return chunks


    # ========================================================
    # INDEX BUILDING
    # ========================================================

    def _build_index(
        self,
        pdf_paths
    ):

        self.chunks = []
        self.metadata = []

        print(
            "Building document index...",
            flush=True
        )

        for pdf_path in pdf_paths:

            pages = self._extract_pdf_text(
                pdf_path
            )

            for page_data in pages:

                page_chunks = self._chunk_text(
                    page_data["text"]
                )

                for chunk in page_chunks:

                    self.chunks.append(
                        chunk
                    )

                    self.metadata.append(
                        {
                            "source": pdf_path.name,
                            "page": page_data["page"]
                        }
                    )


        if not self.chunks:

            raise ValueError(
                "No readable text was found in the PDF documents."
            )


        print(
            f"Created {len(self.chunks)} chunks.",
            flush=True
        )

        print(
            "Creating embeddings...",
            flush=True
        )

        embeddings = self.embedding_model.encode(
            self.chunks,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )


        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.index.add(
            embeddings
        )

        print(
            "Document index ready.",
            flush=True
        )


    # ========================================================
    # USER DOCUMENTS
    # ========================================================

    def set_user_documents(
        self,
        pdf_paths
    ):

        valid_paths = []

        for path in pdf_paths:

            path = Path(path)

            if path.exists() and path.suffix.lower() == ".pdf":

                valid_paths.append(
                    path
                )


        if not valid_paths:

            raise ValueError(
                "No valid user PDF documents were found."
            )


        print(
            f"Indexing {len(valid_paths)} user PDF(s)...",
            flush=True
        )

        self._build_index(
            valid_paths
        )


    # ========================================================
    # RETRIEVAL
    # ========================================================

    def retrieve(
        self,
        query,
        top_k=5
    ):

        if self.index is None:

            raise ValueError(
                "Researcher index has not been built."
            )


        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )


        scores, indices = self.index.search(
            query_embedding,
            min(top_k, len(self.chunks))
        )


        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index < 0:
                continue

            results.append(
                {
                    "text": self.chunks[index],
                    "score": float(score),
                    "source": self.metadata[index]["source"],
                    "page": self.metadata[index]["page"]
                }
            )


        return results


    # ========================================================
    # RESEARCH
    # ========================================================

    def research(
        self,
        query
    ):

        print(
            "\n===== RESEARCHER =====",
            flush=True
        )

        print(
            f"Query: {query}",
            flush=True
        )


        retrieved = self.retrieve(
            query,
            top_k=5
        )


        context_parts = []

        for result in retrieved:

            context_parts.append(
                f"""
Source: {result["source"]}
Page: {result["page"]}

{result["text"]}
"""
            )


        context = "\n\n".join(
            context_parts
        )


        prompt = f"""
You are Atlas, an AI learning researcher.

Answer the student's question using ONLY the
provided document context.

Student question:
{query}

Document context:
{context}

Rules:

1. Use the document context as the primary source.
2. Do not invent facts that are not supported by the context.
3. If the answer cannot be determined from the documents,
   clearly say that the documents do not contain enough information.
4. Explain the answer clearly for a student.
5. Mention the relevant document name and page number when useful.
6. Do not discuss the retrieval process.

Return a clear, helpful answer.
"""


        print(
            "Sending retrieved context to Gemini...",
            flush=True
        )


        response = self.client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )


        print(
            "Research response received.",
            flush=True
        )


        sources = []

        for result in retrieved:

            source = {
                "document": result["source"],
                "page": result["page"],
                "similarity": round(
                    result["score"],
                    4
                )
            }

            if source not in sources:

                sources.append(
                    source
                )


        return {
            "answer": response.text,
            "sources": sources
        }
