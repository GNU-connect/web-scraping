from datetime import datetime
from unittest.mock import MagicMock, call
import pytest

from src.data_access.shuttle_repository import ShuttleRepository
from src.models.shuttle import ShuttleTimetable


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def repository(mock_client, mocker):
    mocker.patch('src.data_access.shuttle_repository.get_supabase_client', return_value=mock_client)
    return ShuttleRepository()


@pytest.fixture
def sample_timetable():
    return ShuttleTimetable(
        route_name='가좌캠퍼스 → 칠암캠퍼스',
        timetable={'오전': ['08:20', '09:00 (금요일 미운행)'], '오후': ['13:10 (금요일 미운행)', '13:40']},
        updated_at=datetime(2026, 3, 13, 9, 47, 30),
    )


class TestUpsertTimetable:
    def test_upsert_timetable_calls_supabase_upsert(self, repository, mock_client, sample_timetable):
        repository.upsert_timetable(sample_timetable)
        mock_client.table.assert_called_once_with('shuttle_timetable')

    def test_upsert_timetable_passes_correct_route_name(self, repository, mock_client, sample_timetable):
        repository.upsert_timetable(sample_timetable)
        upsert_call = mock_client.table.return_value.upsert
        payload = upsert_call.call_args[0][0]
        assert payload['route_name'] == '가좌캠퍼스 → 칠암캠퍼스'

    def test_upsert_timetable_passes_correct_timetable(self, repository, mock_client, sample_timetable):
        repository.upsert_timetable(sample_timetable)
        upsert_call = mock_client.table.return_value.upsert
        payload = upsert_call.call_args[0][0]
        assert payload['timetable'] == sample_timetable.timetable

    def test_upsert_timetable_passes_correct_updated_at(self, repository, mock_client, sample_timetable):
        repository.upsert_timetable(sample_timetable)
        upsert_call = mock_client.table.return_value.upsert
        payload = upsert_call.call_args[0][0]
        assert payload['updated_at'] == '2026-03-13T09:47:30'

    def test_upsert_timetable_uses_on_conflict_route_name(self, repository, mock_client, sample_timetable):
        repository.upsert_timetable(sample_timetable)
        upsert_call = mock_client.table.return_value.upsert
        kwargs = upsert_call.call_args[1]
        assert kwargs.get('on_conflict') == 'route_name'

    def test_upsert_timetable_calls_execute(self, repository, mock_client, sample_timetable):
        repository.upsert_timetable(sample_timetable)
        mock_client.table.return_value.upsert.return_value.execute.assert_called_once()
