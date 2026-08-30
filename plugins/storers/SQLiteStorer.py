import os, sys, json, re, string
from datetime import datetime

from framework.base_classes import Storer

import sqlite3
import sqlite_vec
import struct
import ollama

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

        self.cur.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks 
                (
                chunk_id INTEGER PRIMARY KEY, text TEXT
                )
                """
                )
        self.cur.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks USING vec0
                (
                chunk_id INTEGER PRIMARY KEY,embedding float[768]
                )
                """
                )

    def store(self, chunks: list, store_vecs: list):
        with self.db_conn:
            for i in range(len(chunks)):
                self.cur.execute(
                        """
                        INSERT INTO chunks (text) VALUES (:text)
                        """,
                        {"text": chunks[i]
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

