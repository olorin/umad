UMAD - Unearth Me A Document
============================

It's like Google for all your digital shit (information), spread across multiple disjoint systems with no common data format.


Data flow
---------

Documents everywhere -> Distillation -> Document blobs -> Storage

Query to find documents -> Storage -> Results (URLs)


Document blobs
--------------

1. Retrieve a document from a **URL**
2. Run it through a **distiller** to produce a **document blob**
3. Put the key (URL) and value (document blob) relation into **storage**
4. Queries 
