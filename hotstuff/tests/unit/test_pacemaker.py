"""
Unit tests for Pacemaker implementations.
"""

import pytest

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.pacemaker.base_pacemaker import BasePacemaker
from hotstuff.pacemaker.adaptive_pacemaker import AdaptivePacemaker


class TestBasePacemaker:
    """Tests for the BasePacemaker class."""
    
    def test_fixed_timeout(self):
        """Test that timeout is always fixed."""
        pacemaker = BasePacemaker(base_timeout_ms=1000)
        
        pacemaker.start_timer(ViewNumber(1), current_time=0)
        assert pacemaker.get_current_timeout() == 1000
        
        pacemaker.on_timeout(current_time=1000)
        assert pacemaker.get_current_timeout() == 1000
        
        pacemaker.on_view_success(ViewNumber(1), duration_ms=500)
        assert pacemaker.get_current_timeout() == 1000
    
    def test_timer_expiry(self):
        """Test timer expiry time calculation."""
        pacemaker = BasePacemaker(base_timeout_ms=1000)
        
        timeout_time = pacemaker.start_timer(ViewNumber(1), current_time=500)
        
        assert timeout_time == 1500
        assert pacemaker.get_timeout_time() == 1500
    
    def test_view_increment_on_timeout(self):
        """Test that view increments on timeout."""
        pacemaker = BasePacemaker(base_timeout_ms=1000)
        pacemaker.start_timer(ViewNumber(5), current_time=0)
        
        next_view = pacemaker.on_timeout(current_time=1000)
        
        assert next_view == ViewNumber(6)
    
    def test_stop_timer(self):
        """Test stopping the timer."""
        pacemaker = BasePacemaker(base_timeout_ms=1000)
        pacemaker.start_timer(ViewNumber(1), current_time=0)
        
        assert pacemaker.is_timer_active is True
        
        pacemaker.stop_timer()
        
        assert pacemaker.is_timer_active is False
        assert pacemaker.get_timeout_time() == -1


class TestAdaptivePacemaker:
    """Tests for the AdaptivePacemaker class."""
    
    def test_timeout_adjusts_on_success(self):
        """Test that timeout adjusts based on view duration."""
        pacemaker = AdaptivePacemaker(
            base_timeout_ms=1000,
            alpha=0.5,
            min_timeout_ms=500,
            max_timeout_ms=5000
        )
        
        initial_timeout = pacemaker.get_current_timeout()
        
        pacemaker.on_view_success(ViewNumber(1), duration_ms=200)
        
        new_timeout = pacemaker.get_current_timeout()
        
        assert new_timeout != initial_timeout
        assert new_timeout >= 500
    
    def test_exponential_backoff_on_timeout(self):
        """Test exponential backoff on consecutive timeouts."""
        pacemaker = AdaptivePacemaker(
            base_timeout_ms=1000,
            alpha=0.5,
            min_timeout_ms=500,
            max_timeout_ms=5000
        )
        
        pacemaker.start_timer(ViewNumber(1), current_time=0)
        pacemaker.on_timeout(current_time=1000)
        timeout1 = pacemaker.get_current_timeout()
        
        pacemaker.start_timer(ViewNumber(2), current_time=1000)
        pacemaker.on_timeout(current_time=1000 + timeout1)
        timeout2 = pacemaker.get_current_timeout()
        
        assert timeout2 > timeout1
    
    def test_timeout_resets_on_success(self):
        """Test that consecutive timeout counter resets on success."""
        pacemaker = AdaptivePacemaker(
            base_timeout_ms=1000,
            alpha=0.5,
            min_timeout_ms=500,
            max_timeout_ms=5000
        )
        
        pacemaker.start_timer(ViewNumber(1), current_time=0)
        pacemaker.on_timeout(current_time=1000)
        pacemaker.start_timer(ViewNumber(2), current_time=1000)
        pacemaker.on_timeout(current_time=2000)
        
        assert pacemaker.consecutive_timeouts == 2
        
        pacemaker.on_view_success(ViewNumber(3), duration_ms=500)
        
        assert pacemaker.consecutive_timeouts == 0
    
    def test_timeout_bounded(self):
        """Test that timeout stays within bounds."""
        pacemaker = AdaptivePacemaker(
            base_timeout_ms=1000,
            alpha=0.5,
            min_timeout_ms=500,
            max_timeout_ms=2000
        )
        
        for i in range(10):
            pacemaker.start_timer(ViewNumber(i), current_time=i * 2000)
            pacemaker.on_timeout(current_time=i * 2000 + 2000)
        
        assert pacemaker.get_current_timeout() <= 2000
        
        pacemaker.reset()
        
        for i in range(10):
            pacemaker.on_view_success(ViewNumber(i), duration_ms=100)
        
        assert pacemaker.get_current_timeout() >= 500
