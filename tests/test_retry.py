"""Tests for retry decorator."""

from unittest.mock import MagicMock

import pytest

from src.core.retry import retry_with_backoff


class TestRetryWithBackoff:
    def test_success_on_first_try(self):
        mock = MagicMock(return_value="ok")

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def func():
            return mock()

        result = func()
        assert result == "ok"
        assert mock.call_count == 1

    def test_retries_on_failure(self):
        mock = MagicMock(side_effect=[ValueError("fail"), ValueError("fail"), "ok"])

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def func():
            return mock()

        result = func()
        assert result == "ok"
        assert mock.call_count == 3

    def test_exhausts_retries(self):
        mock = MagicMock(side_effect=ValueError("always fail"))

        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def func():
            return mock()

        with pytest.raises(ValueError, match="always fail"):
            func()
        assert mock.call_count == 3

    def test_only_catches_specified_exceptions(self):
        mock = MagicMock(side_effect=TypeError("wrong type"))

        @retry_with_backoff(max_retries=3, base_delay=0.01, retryable_exceptions=(ValueError,))
        def func():
            return mock()

        with pytest.raises(TypeError):
            func()
        assert mock.call_count == 1

    @pytest.mark.asyncio
    async def test_async_retry(self):
        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        async def async_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("fail")
            return "ok"

        result = await async_func()
        assert result == "ok"
        assert call_count == 3
