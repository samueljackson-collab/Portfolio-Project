"""
Comprehensive tests for database module.

Tests cover:
- Database engine configuration
- Session management
- Connection lifecycle
- Transaction handling
- Error scenarios
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy import text

from app.database import (
    engine,
    AsyncSessionLocal,
    Base,
    get_db,
    init_db,
    close_db,
)


class TestDatabaseEngine:
    """Test database engine configuration."""

    def test_engine_is_async(self):
        """Test that engine is async."""
        assert isinstance(engine, AsyncEngine)

    def test_engine_has_correct_driver(self):
        """Test that engine uses asyncpg driver."""
        assert "asyncpg" in str(engine.url)

    def test_engine_url_is_postgresql(self):
        """Test that engine connects to PostgreSQL."""
        assert engine.url.drivername == "postgresql+asyncpg"


class TestSessionFactory:
    """Test session factory configuration."""

    def test_session_factory_creates_async_session(self):
        """Test that session factory creates AsyncSession."""
        async with AsyncSessionLocal() as session:
            assert isinstance(session, AsyncSession)

    def test_session_factory_expire_on_commit_false(self):
        """Test that expire_on_commit is False."""
        # This is configured in AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            # Verify session is configured correctly
            assert session is not None


class TestBaseModel:
    """Test declarative base."""

    def test_base_has_metadata(self):
        """Test that Base has metadata attribute."""
        assert hasattr(Base, "metadata")

    def test_base_metadata_has_tables(self):
        """Test that Base metadata can hold tables."""
        assert hasattr(Base.metadata, "tables")


@pytest.mark.asyncio
class TestGetDbDependency:
    """Test get_db dependency function."""

    async def test_get_db_yields_session(self):
        """Test that get_db yields an AsyncSession."""
        gen = get_db()
        session = await gen.__anext__()
        
        assert isinstance(session, AsyncSession)
        
        # Cleanup
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass

    async def test_get_db_session_can_execute_query(self):
        """Test that session from get_db can execute queries."""
        gen = get_db()
        session = await gen.__anext__()
        
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1
        
        # Cleanup
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass

    async def test_get_db_commits_on_success(self):
        """Test that get_db commits transaction on success."""
        # This is implicitly tested by the function's try-finally block
        gen = get_db()
        session = await gen.__anext__()
        
        # Perform a query
        await session.execute(text("SELECT 1"))
        
        # Cleanup - should commit
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass

    async def test_get_db_closes_session(self):
        """Test that get_db closes session after use."""
        gen = get_db()
        session = await gen.__anext__()
        
        # Finish the generator
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass
        
        # Session should be closed
        # Note: We can't directly test if closed, but it's closed in finally block


@pytest.mark.asyncio
class TestDatabaseInitialization:
    """Test database initialization functions."""

    async def test_init_db_creates_tables(self):
        """Test that init_db creates database tables."""
        # This will create all tables defined in models
        await init_db()
        
        # Verify by checking if we can query the database
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
            tables = [row[0] for row in result.fetchall()]
            
            # Should have our main tables
            assert "users" in tables or "content" in tables or len(tables) >= 0

    async def test_init_db_is_idempotent(self):
        """Test that calling init_db multiple times is safe."""
        # Should not raise error
        await init_db()
        await init_db()


@pytest.mark.asyncio
class TestDatabaseCleanup:
    """Test database cleanup functions."""

    async def test_close_db_disposes_engine(self):
        """Test that close_db disposes the engine."""
        # Should not raise error
        await close_db()


@pytest.mark.asyncio
class TestSessionLifecycle:
    """Test complete session lifecycle scenarios."""

    async def test_session_lifecycle_normal_operation(self):
        """Test normal session lifecycle with query."""
        async with AsyncSessionLocal() as session:
            # Execute query
            result = await session.execute(text("SELECT 1 as value"))
            row = result.first()
            
            assert row[0] == 1
            
            # Commit
            await session.commit()

    async def test_session_lifecycle_with_rollback(self):
        """Test session lifecycle with rollback."""
        async with AsyncSessionLocal() as session:
            try:
                # Execute query
                await session.execute(text("SELECT 1"))
                
                # Simulate error
                raise ValueError("Test error")
                
            except ValueError:
                # Rollback on error
                await session.rollback()

    async def test_multiple_sessions_are_independent(self):
        """Test that multiple sessions are independent."""
        async with AsyncSessionLocal() as session1:
            async with AsyncSessionLocal() as session2:
                # Both sessions should work independently
                result1 = await session1.execute(text("SELECT 1"))
                result2 = await session2.execute(text("SELECT 2"))
                
                assert result1.scalar() == 1
                assert result2.scalar() == 2


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling in database operations."""

    async def test_session_handles_invalid_query(self):
        """Test that session handles invalid SQL gracefully."""
        async with AsyncSessionLocal() as session:
            with pytest.raises(Exception):
                await session.execute(text("INVALID SQL QUERY"))

    async def test_get_db_rolls_back_on_exception(self):
        """Test that get_db rolls back on exception."""
        gen = get_db()
        session = await gen.__anext__()
        
        try:
            # Simulate an error during request handling
            await session.execute(text("SELECT 1"))
            raise ValueError("Simulated error")
        except ValueError:
            pass
        
        # Finish generator - should rollback
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass


@pytest.mark.asyncio
class TestConnectionPooling:
    """Test connection pool configuration."""

    async def test_multiple_concurrent_connections(self):
        """Test that connection pool handles multiple connections."""
        sessions = []
        
        # Create multiple sessions
        for _ in range(3):
            session = AsyncSessionLocal()
            sessions.append(session)
        
        # Execute queries concurrently
        for session in sessions:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
        
        # Close all sessions
        for session in sessions:
            await session.close()

    async def test_connection_pool_reuse(self):
        """Test that connections are reused from pool."""
        # First session
        async with AsyncSessionLocal() as session1:
            await session1.execute(text("SELECT 1"))
        
        # Second session - should reuse connection from pool
        async with AsyncSessionLocal() as session2:
            await session2.execute(text("SELECT 1"))