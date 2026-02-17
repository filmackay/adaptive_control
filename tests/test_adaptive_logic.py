"""Tests for adaptive_logic."""

import numpy as np

from custom_components.adaptive_control.adaptive_logic import (
    AdaptiveFIRController,
    State,
)


async def test_initialization():
    """Test default initialization."""
    ctl = AdaptiveFIRController()
    assert ctl.fir_order == 10
    assert ctl.state.rls_forgetting == 0.99
    assert ctl.state.control_regularization == 0.5
    assert np.all(np.isnan(ctl.state.control_history))


async def test_state_load():
    """Test state loading from history."""
    weights = [0.1, 0.2, 0.3]
    state = State(weights=weights, rls_forgetting=0.8)
    ctl = AdaptiveFIRController(state=state)
    assert ctl.fir_order == 3
    assert ctl.state.rls_forgetting == 0.8
    assert len(ctl.state.control_history) == 3


async def test_update_learning():
    """Test that weights update when learning is enabled."""
    # Pre-fill history to enable learning immediately
    weights = [0.0, 1.0]  # Simple gain of 1 with 1-step delay
    history = [10, 10]
    state = State(weights=weights, control_history=history)
    ctl = AdaptiveFIRController(state=state)

    # Target 10, Measured 5 (Prediction Error = 5 - (0*10 + 1*10) = 5 - 10 = -5)
    # Weights should adjust downwards to fix the over-prediction
    _, metrics = ctl.update(target=10, measured=5, control=10, min_out=0, max_out=20)

    # Check if weights changed
    assert not np.array_equal(ctl.state.weights, np.array(weights))
    assert metrics["prediction_error"] != 0


async def test_dead_time_learning():
    """Test learning Dead Time (0 weights at start)."""
    # Weights: [0.0, 0.0, 1.0] (2-step delay)
    weights = [0.0, 0.0, 1.0]
    history = [10, 10, 10]
    state = State(weights=weights, control_history=history)
    ctl = AdaptiveFIRController(state=state)

    # Measured 10. Prediction = 0*10 + 0*10 + 1*10 = 10. Error=0.
    _, metrics = ctl.update(target=10, measured=10, control=10, min_out=0, max_out=20)

    # Weights should NOT change significantly if error is 0
    assert np.allclose(ctl.state.weights, np.array(weights), atol=1e-5)

    # Now introduce error. Measured 5. Error = -5.
    _, metrics = ctl.update(target=10, measured=5, control=10, min_out=0, max_out=20)
    assert metrics["prediction_error"] == -5.0
    assert not np.allclose(ctl.state.weights, np.array(weights), atol=1e-5)
