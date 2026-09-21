.headers on
.mode column
.load /Users/rama-mac/miniconda3/envs/ds/lib/python3.13/site-packages/sqlite_vec/vec0.dylib

SELECT
    d.document_id AS "Document ID",
    d.filename AS "Document name",
    d.metadata AS "Metadata",

    COUNT(DISTINCT c.chunk_id) AS "Number of chunks",

    COUNT(DISTINCT v.chunk_id) AS "Number of embeddings",

    GROUP_CONCAT(
        DISTINCT v.vec_len
    ) AS "Embedding dimension(s)"

FROM documents AS d

LEFT JOIN chunks AS c
    ON d.document_id = c.doc_id

LEFT JOIN vec_chunks AS v
    ON v.chunk_id = c.chunk_id

GROUP BY
    d.document_id,
    d.filename,
    d.metadata

ORDER BY
    d.document_id;

