import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.auth import get_current_user, AuthenticatedUser
from app.models.document import Document
from app.schemas.envelope import APIResponse
from app.schemas.document import (
    DocumentUploadResponse,
    DocumentRead,
    DocumentListResponse,
)
from app.services.storage.storage_service import StorageService
from app.services.document.scanner import DocumentScanner
from app.services.document.extractor import DocumentExtractor

router = APIRouter()

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit


@router.post("/upload", response_model=APIResponse[DocumentUploadResponse])
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Form(None),
    customer_id: Optional[str] = Form(None),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[DocumentUploadResponse]:
    # 1. Read file content
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB.",
        )

    # 2. Path Traversal Defense: Sanitize file name
    safe_filename = DocumentScanner.sanitize_filename(file.filename or "upload")

    # 3. Magic-Byte Validation
    is_valid_format, detected_mime, format_error = DocumentScanner.validate_magic_bytes(content, safe_filename)
    if not is_valid_format:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=format_error or "Invalid or unapproved file format.",
        )

    # 4. Anti-Malware & EICAR Scan
    is_clean, malware_threat = DocumentScanner.scan_for_malware(content, safe_filename)
    doc_id = str(uuid.uuid4())
    file_hash = DocumentScanner.compute_sha256(content)

    if not is_clean:
        # Quarantine the file immediately
        quarantined_path = StorageService.build_storage_path(current_user.tenant_id, doc_id, f"QUARANTINED_{safe_filename}")
        doc = Document(
            id=doc_id,
            tenant_id=current_user.tenant_id,
            conversation_id=conversation_id,
            customer_id=customer_id,
            file_name=safe_filename,
            file_size_bytes=len(content),
            mime_type=detected_mime or "application/octet-stream",
            storage_path=quarantined_path,
            file_hash=file_hash,
            status="quarantined",
            is_quarantined=True,
            quarantine_reason=malware_threat,
            extracted_text=None,
            summary=f"Threat detected: {malware_threat}",
            doc_metadata={"threat": malware_threat, "status": "quarantined"},
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)

        return APIResponse.ok(
            data=DocumentUploadResponse.model_validate(doc),
            request_id=getattr(request.state, "request_id", None),
            tenant_id=current_user.tenant_id,
        )

    # 5. Save to tenant-isolated storage
    storage_path = StorageService.save_file(
        tenant_id=current_user.tenant_id,
        document_id=doc_id,
        filename=safe_filename,
        content=content,
    )

    # 6. Extract text & image intelligence
    raw_text, meta = DocumentExtractor.extract_text(content, detected_mime or "application/octet-stream", safe_filename)

    # 7. Document Anti-Prompt-Injection Defense
    safe_text_envelope, has_injection, threats = DocumentExtractor.sanitize_extracted_text(raw_text)
    if has_injection:
        meta["prompt_injection_threats"] = threats
        meta["security_flag"] = "ADVERSARIAL_INJECTION_SUSPECTED"

    # 8. Record in database
    doc = Document(
        id=doc_id,
        tenant_id=current_user.tenant_id,
        conversation_id=conversation_id,
        customer_id=customer_id,
        file_name=safe_filename,
        file_size_bytes=len(content),
        mime_type=detected_mime or "application/octet-stream",
        storage_path=storage_path,
        file_hash=file_hash,
        status="ready",
        is_quarantined=False,
        quarantine_reason=None,
        extracted_text=safe_text_envelope,
        summary=f"Indexed {detected_mime} document: {safe_filename}",
        doc_metadata=meta,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    return APIResponse.ok(
        data=DocumentUploadResponse.model_validate(doc),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("", response_model=APIResponse[DocumentListResponse])
async def list_documents(
    request: Request,
    conversation_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[DocumentListResponse]:
    query = select(Document).where(Document.tenant_id == current_user.tenant_id)
    if conversation_id:
        query = query.where(Document.conversation_id == conversation_id)
    if status_filter:
        query = query.where(Document.status == status_filter)

    query = query.order_by(Document.created_at.desc())
    result = await db.execute(query)
    docs = result.scalars().all()

    doc_reads = []
    for d in docs:
        read_obj = DocumentRead.model_validate(d)
        if not d.is_quarantined:
            read_obj.download_url = StorageService.generate_presigned_url(current_user.tenant_id, d.id)
        doc_reads.append(read_obj)

    return APIResponse.ok(
        data=DocumentListResponse(documents=doc_reads, total=len(doc_reads)),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/{document_id}", response_model=APIResponse[DocumentRead])
async def get_document(
    document_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[DocumentRead]:
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.tenant_id == current_user.tenant_id)
    )
    doc = result.scalars().first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found.",
        )

    read_obj = DocumentRead.model_validate(doc)
    if not doc.is_quarantined:
        read_obj.download_url = StorageService.generate_presigned_url(current_user.tenant_id, doc.id)

    return APIResponse.ok(
        data=read_obj,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    expires: Optional[int] = None,
    signature: Optional[str] = None,
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    # 1. Fetch document
    query = select(Document).where(Document.id == document_id)
    if current_user:
        query = query.where(Document.tenant_id == current_user.tenant_id)

    result = await db.execute(query)
    doc = result.scalars().first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied.",
        )

    # 2. Strict Quarantine Check: Block downloads of quarantined files
    if doc.is_quarantined:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Document is quarantined ({doc.quarantine_reason}).",
        )

    # 3. Presigned signature verification if using query param auth
    if expires and signature:
        is_valid_sig = StorageService.verify_presigned_signature(doc.tenant_id, doc.id, expires, signature)
        if not is_valid_sig:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Expired or tampered download signature.",
            )

    # 4. Fetch bytes from storage
    content = StorageService.get_file(doc.tenant_id, doc.storage_path)
    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File content not found in storage.",
        )

    headers = {
        "Content-Disposition": f'attachment; filename="{doc.file_name}"',
        "Content-Length": str(len(content)),
        "X-Content-Type-Options": "nosniff",
    }
    return Response(content=content, media_type=doc.mime_type, headers=headers)


@router.delete("/{document_id}", response_model=APIResponse[dict])
async def delete_document(
    document_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[dict]:
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.tenant_id == current_user.tenant_id)
    )
    doc = result.scalars().first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found.",
        )

    # Remove from storage
    try:
        StorageService.delete_file(current_user.tenant_id, doc.storage_path)
    except Exception:
        pass

    # Remove from database
    await db.delete(doc)
    await db.commit()

    return APIResponse.ok(
        data={"deleted": True, "document_id": document_id},
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
