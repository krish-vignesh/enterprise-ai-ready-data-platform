"""Real PostgreSQL integration tests for the repository layer."""

from __future__ import annotations

import asyncio
import os
from urllib.parse import quote
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://"
    f"AURORA:{quote('Suvi@123456789', safe='')}@127.0.0.1:5433/"
    "enterprise_ai_platform_test"
)

from app.config.settings import settings
from app.db.base import Base
from app.models.company import Company
from app.models.dataset import Dataset
from app.models.document import Document, DocumentStatus
from app.models.enums import UploadAttemptStatus
from app.models.source_system import SourceSystem
from app.models.storage_object import StorageObject
from app.models.upload_attempt import UploadAttempt
from app.repositories.company_repository import CompanyRepository
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.source_repository import SourceSystemRepository
from app.repositories.storage_object_repository import StorageObjectRepository
from app.repositories.upload_attempt_repository import UploadAttemptRepository


if not settings.database_url.endswith("/enterprise_ai_platform_test"):
    raise RuntimeError(
        "Integration tests must target enterprise_ai_platform_test; "
        f"got {settings.database_url!r}"
    )


def run_async(coro):
    """Run async work with a selector loop compatible with psycopg on Windows."""
    return asyncio.run(coro, loop_factory=lambda: asyncio.SelectorEventLoop())


async def _new_session():
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
            await engine.dispose()


def test_repositories_persist_and_join_data():
    async def run_test() -> None:
        engine = create_async_engine(settings.database_url, pool_pre_ping=True)
        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.drop_all)
                await connection.run_sync(Base.metadata.create_all)

            async_session_factory = async_sessionmaker(
                bind=engine,
                class_=AsyncSession,
                autoflush=False,
                expire_on_commit=False,
            )

            async with async_session_factory() as session:
                company_repo = CompanyRepository(session)
                source_repo = SourceSystemRepository(session)
                dataset_repo = DatasetRepository(session)
                document_repo = DocumentRepository(session)
                storage_repo = StorageObjectRepository(session)
                upload_attempt_repo = UploadAttemptRepository(session)

                company = Company(company_name="Northwind Labs")
                company_repo.add(company)
                await session.flush()
                assert await company_repo.get_by_id(company.company_id) == company

                source = SourceSystem(
                    company_id=company.company_id,
                    source_name="erp-main",
                    source_type="ERP",
                )
                source_repo.add(source)
                await session.flush()
                assert await source_repo.get_by_id(source.source_id) == source

                dataset = Dataset(source_id=source.source_id, dataset_name="customers")
                dataset_repo.add(dataset)
                await session.flush()
                assert (
                    await dataset_repo.get_by_source_and_name(
                        source.source_id, "customers"
                    )
                ) == dataset

                document = Document(
                    dataset_id=dataset.dataset_id,
                    original_filename="customers.csv",
                    detected_format="csv",
                    content_type="text/csv",
                    file_size_bytes=2048,
                    sha256="a" * 64,
                    status=DocumentStatus.UPLOADING,
                )
                document_repo.add(document)
                await session.flush()
                assert (
                    await document_repo.get_by_dataset_and_sha256(
                        dataset.dataset_id, "a" * 64
                    )
                ) == document

                storage_object = StorageObject(
                    document_id=document.document_id,
                    bucket_name="workspace-records",
                    object_key="northwind/customers.csv",
                )
                storage_repo.add(storage_object)
                await session.flush()
                assert (
                    await storage_repo.get_by_bucket_and_key(
                        "workspace-records",
                        "northwind/customers.csv",
                    )
                ) == storage_object

                attempt = UploadAttempt(
                    document_id=document.document_id,
                    attempt_number=1,
                    status=UploadAttemptStatus.IN_PROGRESS,
                )
                upload_attempt_repo.add(attempt)
                await session.flush()
                assert (
                    await upload_attempt_repo.get_by_document_and_attempt_number(
                        document.document_id,
                        1,
                    )
                ) == attempt
                assert (
                    await upload_attempt_repo.get_latest_by_document(
                        document.document_id
                    )
                    == attempt
                )

                second_company = Company(company_name="Other Company")
                company_repo.add(second_company)
                await session.flush()

                second_source = SourceSystem(
                    company_id=second_company.company_id,
                    source_name="file-archive",
                    source_type="SFTP",
                )
                source_repo.add(second_source)
                await session.flush()

                second_dataset = Dataset(
                    source_id=second_source.source_id,
                    dataset_name="invoices",
                )
                dataset_repo.add(second_dataset)
                await session.flush()

                second_document = Document(
                    dataset_id=second_dataset.dataset_id,
                    original_filename="invoices.csv",
                    detected_format="csv",
                    content_type="text/csv",
                    file_size_bytes=4096,
                    sha256="b" * 64,
                    status=DocumentStatus.AVAILABLE,
                )
                document_repo.add(second_document)
                await session.flush()

                second_storage = StorageObject(
                    document_id=second_document.document_id,
                    bucket_name="workspace-records",
                    object_key="other/invoices.csv",
                )
                storage_repo.add(second_storage)
                await session.flush()

                company_objects = await storage_repo.list_by_company(
                    company.company_id, limit=10
                )
                assert [obj.storage_object_id for obj in company_objects] == [
                    storage_object.storage_object_id
                ]
        finally:
            await engine.dispose()

    run_async(run_test())


def test_database_enforces_constraints():
    async def run_test() -> None:
        engine = create_async_engine(settings.database_url, pool_pre_ping=True)
        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.drop_all)
                await connection.run_sync(Base.metadata.create_all)

            async_session_factory = async_sessionmaker(
                bind=engine,
                class_=AsyncSession,
                autoflush=False,
                expire_on_commit=False,
            )

            async with async_session_factory() as session:
                company = Company(company_name="Constraint Test")
                session.add(company)
                await session.flush()

                source = SourceSystem(
                    company_id=company.company_id,
                    source_name="crm-source",
                    source_type="CRM",
                )
                session.add(source)
                await session.flush()

                dataset = Dataset(source_id=source.source_id, dataset_name="accounts")
                session.add(dataset)
                await session.flush()

                document = Document(
                    dataset_id=dataset.dataset_id,
                    original_filename="accounts.csv",
                    detected_format="csv",
                    content_type="text/csv",
                    file_size_bytes=100,
                    sha256="c" * 64,
                    status=DocumentStatus.AVAILABLE,
                )
                session.add(document)
                await session.flush()

                with pytest.raises(IntegrityError):
                    session.add(
                        Dataset(source_id=source.source_id, dataset_name="accounts")
                    )
                    await session.flush()
                await session.rollback()

                with pytest.raises(IntegrityError):
                    second_document = Document(
                        dataset_id=dataset.dataset_id,
                        original_filename="accounts-dup.csv",
                        detected_format="csv",
                        content_type="text/csv",
                        file_size_bytes=100,
                        sha256="c" * 64,
                        status=DocumentStatus.AVAILABLE,
                    )
                    session.add(second_document)
                    await session.flush()
                await session.rollback()

                with pytest.raises(IntegrityError):
                    session.add(
                        StorageObject(
                            document_id=document.document_id,
                            bucket_name="workspace-records",
                            object_key="northwind/accounts.csv",
                        )
                    )
                    session.add(
                        StorageObject(
                            document_id=document.document_id,
                            bucket_name="workspace-records",
                            object_key="northwind/accounts.csv",
                        )
                    )
                    await session.flush()
                await session.rollback()

                with pytest.raises(IntegrityError):
                    session.add(
                        UploadAttempt(
                            document_id=document.document_id,
                            attempt_number=1,
                            status=UploadAttemptStatus.IN_PROGRESS,
                        )
                    )
                    session.add(
                        UploadAttempt(
                            document_id=document.document_id,
                            attempt_number=1,
                            status=UploadAttemptStatus.FAILED,
                        )
                    )
                    await session.flush()
                await session.rollback()

                with pytest.raises(IntegrityError):
                    session.add(
                        UploadAttempt(
                            document_id=document.document_id,
                            attempt_number=0,
                            status=UploadAttemptStatus.IN_PROGRESS,
                        )
                    )
                    await session.flush()
                await session.rollback()

                with pytest.raises(IntegrityError):
                    session.add(
                        Document(
                            dataset_id=dataset.dataset_id,
                            original_filename="bad-size.csv",
                            detected_format="csv",
                            content_type="text/csv",
                            file_size_bytes=-1,
                            sha256="d" * 64,
                            status=DocumentStatus.AVAILABLE,
                        )
                    )
                    await session.flush()
                await session.rollback()

                with pytest.raises(IntegrityError):
                    await session.execute(
                        text(
                            "INSERT INTO documents "
                            "(document_id, dataset_id, original_filename, detected_format, content_type, file_size_bytes, sha256, status, created_at, updated_at) "
                            "VALUES (:document_id, :dataset_id, :original_filename, :detected_format, :content_type, :file_size_bytes, :sha256, :status, NOW(), NOW())"
                        ),
                        {
                            "document_id": str(uuid4()),
                            "dataset_id": str(dataset.dataset_id),
                            "original_filename": "invalid-status.csv",
                            "detected_format": "csv",
                            "content_type": "text/csv",
                            "file_size_bytes": 100,
                            "sha256": "e" * 64,
                            "status": "INVALID_STATUS",
                        },
                    )
                    await session.flush()
                await session.rollback()

                with pytest.raises(IntegrityError):
                    await session.execute(
                        text(
                            "INSERT INTO source_systems "
                            "(source_id, company_id, source_name, source_type, created_at, updated_at) "
                            "VALUES (:source_id, :company_id, :source_name, :source_type, NOW(), NOW())"
                        ),
                        {
                            "source_id": str(uuid4()),
                            "company_id": str(uuid4()),
                            "source_name": "broken-foreign-key",
                            "source_type": "CRM",
                        },
                    )
                    await session.flush()
                await session.rollback()
        finally:
            await engine.dispose()

    run_async(run_test())


def test_repository_add_is_not_committed_and_rollback_removes_rows():
    async def run_test() -> None:
        engine = create_async_engine(settings.database_url, pool_pre_ping=True)
        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.drop_all)
                await connection.run_sync(Base.metadata.create_all)

            async_session_factory = async_sessionmaker(
                bind=engine,
                class_=AsyncSession,
                autoflush=False,
                expire_on_commit=False,
            )

            async with async_session_factory() as session:
                company_repo = CompanyRepository(session)
                company = Company(company_name="Rollback Test")

                company_repo.add(company)
                await session.flush()
                assert await company_repo.get_by_id(company.company_id) == company

                await session.rollback()
                assert await company_repo.get_by_id(company.company_id) is None
        finally:
            await engine.dispose()

    run_async(run_test())
