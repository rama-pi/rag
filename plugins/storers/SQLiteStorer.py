import os, sys, json, re, string 
from datetime import datetime
import ctypes
from contextlib import contextmanager

from framework.base_classes import Storer

import struct
import ollama

# 1. Path to  custom dylib for FTS support
custom_sqlite_path = "/Users/rama-mac/CODE/sqlite/libsqlite3.dylib"
if os.path.exists(custom_sqlite_path):
    ctypes.CDLL(custom_sqlite_path, mode=ctypes.RTLD_GLOBAL)
    print("✅ Custom SQLite library injected successfully!")
else:
    raise RuntimeError(
            "No FTS support in this SQLite build"
            )
# import now after above
import sqlite3
import sqlite_vec

class TransactionAborted(sqlite3.DatabaseError):
    """Raised when a database transaction is intentionally or forcedly aborted."""
    pass


class SQLiteStorer(Storer, storage_type="sqlite"):
    def __init__(self, storage_type: str, db_collection: str):
        # Establish connection
        self.db_conn = sqlite3.connect(db_collection)
        # load 
        # 1. extension
        self.db_conn.enable_load_extension(True)
        # 2. vector search functions
        sqlite_vec.load(self.db_conn)
        self.db_conn.enable_load_extension(False)
        self.cur = self.db_conn.cursor()

        # tables for doc, chunk, embeddings
        with self.db_conn:
            self.cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS documents
                    (
                        document_id INTEGER PRIMARY KEY,
                        filename TEXT,
                        metadata TEXT,
                        file_content_hash TEXT,

                        UNIQUE(filename, file_content_hash)
                    );
                    """
            )
            self.cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS chunks
                    (
                        chunk_id INTEGER PRIMARY KEY,
                        doc_id INT, chunk TEXT,

                        FOREIGN KEY 
                            (doc_id) REFERENCES documents(document_id)
                            ON DELETE CASCADE
                    );
                    """
            )
            self.cur.execute(
                    """
                    CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks USING vec0
                    (
                        chunk_id INTEGER PRIMARY KEY,
                        vec_len INT,
                        embedding float[768]
                    );
                    """
            )
            self.cur.execute(
                    """
                    CREATE TRIGGER IF NOT EXISTS cascade_delete_vec_chunks
                    AFTER DELETE ON chunks
                    BEGIN
                        DELETE FROM vec_chunks WHERE chunk_id = OLD.chunk_id;
                    END;
                    """
            )
            self.db_conn.execute("PRAGMA trusted_schema = ON;")
            self.db_conn.execute("PRAGMA foreign_keys = ON;")
    @contextmanager
    def transaction(self):
        self.transaction_begin()

        try:
            yield
        except Exception as e:
            self.transaction_abort()
            raise TransactionAborted(
                    "Transaction rolled back and terminated."
                    ) from e
        else:
            self.transaction_finalize()
    def transaction_begin(self):
        # begin a transaction
        if not self.db_conn.in_transaction:
            self.db_conn.execute(
                """
                BEGIN DEFERRED TRANSACTION
                """
                )
        return True
    def transaction_finalize(self):
        # commit a transaction
        if self.db_conn.in_transaction:
            self.db_conn.execute(
                """
                COMMIT TRANSACTION
                """
                )
        return True
    def transaction_abort(self):
        # abort a transaction
        if self.db_conn.in_transaction:
            self.db_conn.execute(
                """
                ROLLBACK TRANSACTION
                """
                )
        return True
    def store_document(self, document_name: str, metadata: str, file_content_hash: str) -> int:
        # store doc, ret doc ID
        row = self.cur.execute(
            """
            INSERT INTO documents (filename, metadata, file_content_hash)
            VALUES (?, ?, ?)
            ON CONFLICT(filename, file_content_hash) DO NOTHING
            RETURNING document_id
            """,
            (
                document_name,
                metadata,
                file_content_hash
            )).fetchone()
        document_id = row[0] if row else None
        return document_id
    def store_chunk(self, doc_id: int, chunk: str) -> int:
        # store chunk, ret chunk id
        self.cur.execute(
            """
            INSERT INTO chunks (doc_id, chunk) VALUES (:doc_id, :chunk)
            """,
            {"doc_id": doc_id,
             "chunk": chunk
             }
            )
        generated_id = self.cur.lastrowid
        # chunk_id
        return generated_id
    def get_chunks(self, doc_id: int | None = None):
        # ret chunks of doc_id doc
        rows = self.db_conn.execute(
            """
            SELECT chunk_id, doc_id, chunk from chunks WHERE (:doc_id IS NULL OR doc_id = :doc_id)
            """,
            {
                "doc_id": doc_id
            }
            ).fetchall()
        # [(chunk_id, doc_id, chunk), (chunk_id, doc_id, chunk)]
        return rows
    def store_vector(self, chunk_id: int, vec: list) -> None:
        # store chunk chunk_id's embedding
        vector_len = len(vec)
        vector_bytes = struct.pack(f"{vector_len}f", *vec)
        with self.db_conn:
            self.cur.execute(
                """
                INSERT INTO vec_chunks (chunk_id, vec_len, embedding) VALUES (:id, :vec_len, :emb)
                """,
                {
                    "id":chunk_id,
                    "vec_len": vector_len,
                    "emb":vector_bytes
                }
                )
        return None
    def get_vector(self, chunk_id: int) -> list:
        packed_vec = self.cur.execute(
                """
                SELECT vec_len, embedding FROM vec_chunks WHERE chunk_id = :chunk_id
                """,
                {"chunk_id": chunk_id
                 }
                ).fetchone()
        unpacked_vec = struct.unpack(f"{packed_vec[0]}f", packed_vec[1])
        return unpacked_vec
    def query(self, query_vec: list):
        results = self.db_conn.execute(
                """
                SELECT chunk_id, distance
                FROM vec_chunks
                WHERE embedding MATCH ?
                ORDER BY distance
                LIMIT 3
                """
                ,
                (query_vec,)
                ).fetchall()
        # convert row-id's to chunks
        t = tuple(i[0] for i in results)
        placeholders = ",".join("?" for _ in t)
        rows = self.db_conn.execute(
                f"SELECT chunk_id, text FROM chunks WHERE chunk_id IN ({placeholders})", t
                ).fetchall()

        # add distance to rows 
        rows = [rows[i]+(result[1],) for i, result in enumerate(results)]
        return rows
    '''
    def store(self, doc_id: int, chunks: list, store_vecs: list):
        with self.db_conn:
            for i in range(len(chunks)):
                self.cur.execute(
                        """
                        INSERT INTO chunks (doc_id, chunk) VALUES (:doc_id, :chunk)
                        """,
                        {"doc_id": doc_id,
                         "chunk": chunks[i]
                         }
                        )
                generated_id = self.cur.lastrowid

                vector_len = len(store_vecs.embeddings[i])
                vector_bytes = struct.pack(f"{vector_len}f", *store_vecs.embeddings[i])
                self.cur.execute(
                        """
                        INSERT INTO vec_chunks (chunk_id, embedding) VALUES (:id, :emb)
                        """
                        ,
                        {"id": generated_id, "emb": vector_bytes
                         }
                        )
        return

    '''

