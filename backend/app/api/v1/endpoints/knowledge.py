import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.auth import get_current_user, require_roles, AuthenticatedUser
from app.models.knowledge import KBCollection, KBDocument, KBChunk
from app.schemas.envelope import APIResponse
from app.schemas.knowledge import (
    CollectionCreate,
    CollectionRead,
    KBDocumentCreate,
    KBDocumentRead,
    RAGQueryRequest,
    RAGQueryResponse,
    RAGSearchResult,
)
from app.services.rag.chunker import TextChunker
from app.services.rag.embedder import VectorEmbedder
from app.services.rag.retriever import HybridRetriever

router = APIRouter()


@router.post("/collections", response_model=APIResponse[CollectionRead])
async def create_collection(
    col_in: CollectionCreate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[CollectionRead]:
    col = KBCollection(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        name=col_in.name,
        description=col_in.description,
        is_public=col_in.is_public,
    )
    db.add(col)
    await db.commit()
    await db.refresh(col)

    return APIResponse.ok(
        data=CollectionRead.model_validate(col),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/collections", response_model=APIResponse[List[CollectionRead]])
async def list_collections(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[CollectionRead]]:
    query = (
        select(KBCollection)
        .where(KBCollection.tenant_id == current_user.tenant_id)
        .order_by(KBCollection.name.asc())
    )
    result = await db.execute(query)
    cols = result.scalars().all()
    data = [CollectionRead.model_validate(c) for c in cols]

    return APIResponse.ok(
        data=data,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/documents", response_model=APIResponse[KBDocumentRead])
async def create_document(
    doc_in: KBDocumentCreate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[KBDocumentRead]:
    # 1. Verify collection exists in tenant
    col_res = await db.execute(
        select(KBCollection).where(
            KBCollection.id == doc_in.collection_id,
            KBCollection.tenant_id == current_user.tenant_id,
        )
    )
    collection = col_res.scalars().first()
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection '{doc_in.collection_id}' not found.",
        )

    # 2. Chunk document content
    chunk_data = TextChunker.chunk_text(doc_in.content, chunk_size=400, chunk_overlap=50)

    # 3. Create document record
    doc_id = str(uuid.uuid4())
    doc = KBDocument(
        id=doc_id,
        tenant_id=current_user.tenant_id,
        collection_id=doc_in.collection_id,
        title=doc_in.title,
        source_type=doc_in.source_type,
        source_url=doc_in.source_url,
        version=1,
        status="indexed",
        chunk_count=len(chunk_data),
        doc_metadata=doc_in.doc_metadata or {},
    )
    db.add(doc)

    # 4. Generate embeddings and save chunks
    for item in chunk_data:
        emb = VectorEmbedder.embed_text(item["content"])
        chunk = KBChunk(
            id=str(uuid.uuid4()),
            tenant_id=current_user.tenant_id,
            document_id=doc_id,
            collection_id=doc_in.collection_id,
            chunk_index=item["chunk_index"],
            content=item["content"],
            embedding=emb,
            token_count=item["token_count"],
            chunk_metadata=item["metadata"],
        )
        db.add(chunk)

    await db.commit()

    # Re-fetch with loaded chunks
    stmt = (
        select(KBDocument)
        .options(selectinload(KBDocument.chunks))
        .where(KBDocument.id == doc_id, KBDocument.tenant_id == current_user.tenant_id)
    )
    loaded = (await db.execute(stmt)).scalars().first()

    return APIResponse.ok(
        data=KBDocumentRead.model_validate(loaded),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/documents", response_model=APIResponse[List[KBDocumentRead]])
async def list_documents(
    request: Request,
    collection_id: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[KBDocumentRead]]:
    query = (
        select(KBDocument)
        .options(selectinload(KBDocument.chunks))
        .where(KBDocument.tenant_id == current_user.tenant_id)
    )
    if collection_id:
        query = query.where(KBDocument.collection_id == collection_id)

    query = query.order_by(KBDocument.created_at.desc())
    result = await db.execute(query)
    docs = result.scalars().all()
    data = [KBDocumentRead.model_validate(d) for d in docs]

    return APIResponse.ok(
        data=data,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/documents/{document_id}", response_model=APIResponse[KBDocumentRead])
async def get_document(
    document_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[KBDocumentRead]:
    query = (
        select(KBDocument)
        .options(selectinload(KBDocument.chunks))
        .where(KBDocument.id == document_id, KBDocument.tenant_id == current_user.tenant_id)
    )
    result = await db.execute(query)
    doc = result.scalars().first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found.",
        )

    return APIResponse.ok(
        data=KBDocumentRead.model_validate(doc),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.delete("/documents/{document_id}", response_model=APIResponse[dict])
async def delete_document(
    document_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[dict]:
    query = select(KBDocument).where(
        KBDocument.id == document_id,
        KBDocument.tenant_id == current_user.tenant_id,
    )
    result = await db.execute(query)
    doc = result.scalars().first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found.",
        )

    await db.delete(doc)
    await db.commit()

    return APIResponse.ok(
        data={"deleted": True, "document_id": document_id},
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/query", response_model=APIResponse[RAGQueryResponse])
async def query_knowledge_base(
    query_in: RAGQueryRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[RAGQueryResponse]:
    # 1. Fetch candidate chunks for tenant
    stmt = (
        select(KBChunk, KBDocument.title.label("doc_title"), KBCollection.name.label("col_name"))
        .join(KBDocument, KBChunk.document_id == KBDocument.id)
        .join(KBCollection, KBChunk.collection_id == KBCollection.id)
        .where(KBChunk.tenant_id == current_user.tenant_id)
    )
    if query_in.collection_ids:
        stmt = stmt.where(KBChunk.collection_id.in_(query_in.collection_ids))

    result = await db.execute(stmt)
    rows = result.all()

    candidates = []
    for chunk, doc_title, col_name in rows:
        candidates.append({
            "id": chunk.id,
            "document_id": chunk.document_id,
            "document_title": doc_title,
            "collection_name": col_name,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "embedding": chunk.embedding,
            "chunk_metadata": chunk.chunk_metadata,
        })

    # 2. Run Hybrid Retrieval
    ranked_results = HybridRetriever.search_and_rank(
        query=query_in.query,
        chunks=candidates,
        top_k=query_in.top_k,
        alpha=query_in.alpha,
    )

    data = RAGQueryResponse(
        query=query_in.query,
        results=[RAGSearchResult(**r) for r in ranked_results],
        total_matched=len(ranked_results),
    )

    return APIResponse.ok(
        data=data,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
