#!/usr/bin/env python3
"""
Pytest test suite for tool_db module.
Tests database wrapper functionality with mocked asyncpg connections.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any

# Import the module under test
from app.infrastructure.tools.tool_db import ToolDB, get_tool_db, query
from app.infrastructure.database.client import DatabaseClient


class TestToolDB:
    """Test suite for ToolDB class."""
    
    @pytest.fixture
    def mock_db_client(self):
        """Create a mocked database client."""
        client = MagicMock(spec=DatabaseClient)
        client.connect = AsyncMock(return_value=True)
        
        # Mock connection pool
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock()
        
        mock_pool = AsyncMock()
        mock_pool.acquire = AsyncMock()
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        
        client.pool = mock_pool
        return client, mock_conn
    
    @pytest.fixture
    def tool_db(self, mock_db_client):
        """Create ToolDB instance with mocked client."""
        db_client, _ = mock_db_client
        return ToolDB(db_client)
    
    @pytest.mark.asyncio
    async def test_tool_db_initialization(self, tool_db):
        """Test ToolDB initialization."""
        assert tool_db is not None
        assert hasattr(tool_db, 'allowed_tables')
        assert 'ai_courses' in tool_db.allowed_tables
        assert 'bond' in tool_db.allowed_tables
    
    @pytest.mark.asyncio
    async def test_ensure_connection_success(self, tool_db):
        """Test successful database connection."""
        result = await tool_db.ensure_connection()
        assert result is True
        assert tool_db._connection_ready is True
    
    @pytest.mark.asyncio
    async def test_ensure_connection_failure(self, mock_db_client):
        """Test database connection failure."""
        db_client, _ = mock_db_client
        db_client.connect = AsyncMock(side_effect=Exception("Connection failed"))
        
        tool_db = ToolDB(db_client)
        result = await tool_db.ensure_connection()
        assert result is False
        assert tool_db._connection_ready is False
    
    @pytest.mark.asyncio
    async def test_query_success(self, mock_db_client):
        """Test successful database query."""
        db_client, mock_conn = mock_db_client
        
        # Mock successful query result
        mock_rows = [
            {'id_course': 1, 'name': 'Test Course', 'price': 4500},
            {'id_course': 2, 'name': 'Another Course', 'price': 3000}
        ]
        mock_conn.fetch.return_value = mock_rows
        
        tool_db = ToolDB(db_client)
        result = await tool_db.query('ai_courses', {}, limit=2)
        
        assert len(result) == 2
        assert result[0]['name'] == 'Test Course'
        assert result[1]['name'] == 'Another Course'
    
    @pytest.mark.asyncio
    async def test_query_with_filters(self, mock_db_client):
        """Test database query with filters."""
        db_client, mock_conn = mock_db_client
        
        mock_rows = [{'id_course': 1, 'name': 'Online Course', 'modality': 'online'}]
        mock_conn.fetch.return_value = mock_rows
        
        tool_db = ToolDB(db_client)
        result = await tool_db.query('ai_courses', {'modality': 'online'}, limit=1)
        
        assert len(result) == 1
        assert result[0]['modality'] == 'online'
        
        # Verify that fetch was called with correct parameters
        mock_conn.fetch.assert_called_once()
        call_args = mock_conn.fetch.call_args[0]
        assert 'modality = $1' in call_args[0]  # SQL query
        assert 'online' in call_args[1:]  # Parameters
    
    @pytest.mark.asyncio
    async def test_query_table_not_allowed(self, tool_db):
        """Test query with non-allowed table."""
        result = await tool_db.query('unauthorized_table', {}, limit=1)
        assert result == []
    
    @pytest.mark.asyncio
    async def test_query_limit_protection(self, mock_db_client):
        """Test query limit protection."""
        db_client, mock_conn = mock_db_client
        mock_conn.fetch.return_value = []
        
        tool_db = ToolDB(db_client)
        
        # Test excessive limit gets capped
        await tool_db.query('ai_courses', {}, limit=100)
        
        call_args = mock_conn.fetch.call_args[0]
        # The last parameter should be the limit, capped at 20
        assert call_args[-1] == 20
    
    @pytest.mark.asyncio
    async def test_query_unsafe_filters(self, mock_db_client):
        """Test query with unsafe filter fields."""
        db_client, mock_conn = mock_db_client
        mock_conn.fetch.return_value = []
        
        tool_db = ToolDB(db_client)
        
        # Try with unsafe filter field
        result = await tool_db.query('ai_courses', {'malicious_field': 'value'}, limit=1)
        
        # Should execute but ignore unsafe filters
        assert isinstance(result, list)
        
        # Verify SQL doesn't contain malicious field
        call_args = mock_conn.fetch.call_args[0]
        sql_query = call_args[0]
        assert 'malicious_field' not in sql_query
    
    @pytest.mark.asyncio
    async def test_get_course_by_name_exact_match(self, mock_db_client):
        """Test get_course_by_name with exact match."""
        db_client, mock_conn = mock_db_client
        
        mock_rows = [{'id_course': 1, 'name': 'Experto en IA', 'price': 4500}]
        mock_conn.fetch.return_value = mock_rows
        
        tool_db = ToolDB(db_client)
        result = await tool_db.get_course_by_name('Experto en IA')
        
        assert result is not None
        assert result['name'] == 'Experto en IA'
    
    @pytest.mark.asyncio
    async def test_get_course_by_name_partial_match(self, mock_db_client):
        """Test get_course_by_name with partial match."""
        db_client, mock_conn = mock_db_client
        
        # First call (exact match) returns empty, second call (ILIKE) returns result
        mock_conn.fetch.side_effect = [
            [],  # Exact match fails
            [{'id_course': 1, 'name': 'Experto en IA para Profesionales', 'price': 4500}]  # Partial match succeeds
        ]
        
        tool_db = ToolDB(db_client)
        result = await tool_db.get_course_by_name('Experto')
        
        assert result is not None
        assert 'Experto' in result['name']
    
    @pytest.mark.asyncio
    async def test_get_course_sessions(self, mock_db_client):
        """Test get_course_sessions helper method."""
        db_client, mock_conn = mock_db_client
        
        mock_rows = [
            {'id_session': 1, 'title': 'Introducción', 'id_course_fk': 'course-123'},
            {'id_session': 2, 'title': 'Fundamentos', 'id_course_fk': 'course-123'}
        ]
        mock_conn.fetch.return_value = mock_rows
        
        tool_db = ToolDB(db_client)
        result = await tool_db.get_course_sessions('course-123')
        
        assert len(result) == 2
        assert result[0]['title'] == 'Introducción'
        assert result[1]['title'] == 'Fundamentos'
    
    @pytest.mark.asyncio
    async def test_get_active_bonuses(self, mock_db_client):
        """Test get_active_bonuses helper method."""
        db_client, mock_conn = mock_db_client
        
        mock_rows = [
            {'id_bond': 1, 'content': 'Workbook Gratis', 'active': True},
            {'id_bond': 2, 'content': 'Templates Coda', 'active': True}
        ]
        mock_conn.fetch.return_value = mock_rows
        
        tool_db = ToolDB(db_client)
        result = await tool_db.get_active_bonuses()
        
        assert len(result) == 2
        assert all(bonus['active'] for bonus in result)
    
    @pytest.mark.asyncio
    async def test_query_connection_failure(self, mock_db_client):
        """Test query with connection failure."""
        db_client, _ = mock_db_client
        db_client.connect = AsyncMock(return_value=False)
        
        tool_db = ToolDB(db_client)
        result = await tool_db.query('ai_courses', {}, limit=1)
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_query_exception_handling(self, mock_db_client):
        """Test query exception handling."""
        db_client, mock_conn = mock_db_client
        mock_conn.fetch = AsyncMock(side_effect=Exception("Database error"))
        
        tool_db = ToolDB(db_client)
        result = await tool_db.query('ai_courses', {}, limit=1)
        
        assert result == []


class TestToolDBGlobalFunctions:
    """Test suite for global tool_db functions."""
    
    @pytest.mark.asyncio
    async def test_get_tool_db_singleton(self):
        """Test get_tool_db singleton behavior."""
        with patch('app.infrastructure.tools.tool_db._tool_db_instance', None):
            tool_db1 = await get_tool_db()
            tool_db2 = await get_tool_db()
            
            assert tool_db1 is tool_db2  # Same instance
    
    @pytest.mark.asyncio
    async def test_direct_query_function(self):
        """Test direct query function."""
        with patch('app.infrastructure.tools.tool_db.get_tool_db') as mock_get_tool_db:
            mock_tool_db = AsyncMock()
            mock_tool_db.query = AsyncMock(return_value=[{'test': 'data'}])
            mock_get_tool_db.return_value = mock_tool_db
            
            result = await query('ai_courses', {'test': 'filter'}, limit=3)
            
            assert result == [{'test': 'data'}]
            mock_tool_db.query.assert_called_once_with('ai_courses', {'test': 'filter'}, 3)


@pytest.mark.asyncio
async def test_tool_db_allowed_tables_configuration():
    """Test that allowed tables are properly configured."""
    tool_db = ToolDB()
    
    required_tables = ['ai_courses', 'ai_course_session', 'bond', 'elements_url', 'ai_tema_activity']
    
    for table in required_tables:
        assert table in tool_db.allowed_tables
        assert 'columns' in tool_db.allowed_tables[table]
        assert 'safe_filters' in tool_db.allowed_tables[table]
        assert len(tool_db.allowed_tables[table]['columns']) > 0
        assert len(tool_db.allowed_tables[table]['safe_filters']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])