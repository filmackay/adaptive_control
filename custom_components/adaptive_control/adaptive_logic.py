"""Core logic for Adaptive FIR Controller."""

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

_LOGGER = logging.getLogger(__name__)


@dataclass
class State:
    """Represents the full persistent state of the adaptive controller."""

    # --- Learned Parameters (Impulse Response) ---
    weights: np.ndarray

    # --- Control History ---
    control_history: np.ndarray

    # --- Learning Confidence (Covariance Matrix) ---
    covariance: np.ndarray

    # --- Tuning Parameters ---
    rls_forgetting: float
    control_regularization: float

    def __init__(
        self,
        weights: list[float] | None = None,
        covariance: list[float] | None = None,
        control_history: list[int] | None = None,
        rls_forgetting: float = 0.99,
        control_regularization: float = 0.5,
        **kwargs: dict[str, Any],  # noqa: ARG002
    ) -> None:
        # Default Weights: 3s Delay + Linear Ramp
        if weights and len(weights) > 0:
            self.weights = np.array(weights)
        else:
            self.weights = np.array(
                [
                    0.01,
                    0.01,
                    0.01,  # t=0,1,2 (Dead Time)
                    0.10,
                    0.20,
                    0.30,  # t=3,4,5 (Ramp Up)
                    0.20,
                    0.10,
                    0.05,  # t=6,7,8 (Settle)
                    0.02,  # t=9     (Tail)
                ]
            )
        count = len(self.weights)

        # Control History
        # Ensure it has the correct length (same as weights)
        hist_len = len(control_history) if control_history else 0
        if hist_len < count:
            # Pad with NaNs if history is missing/short
            padding = np.full(count - hist_len, np.nan)
            if hist_len > 0 and control_history:
                self.control_history = np.concatenate(
                    [np.array(control_history), padding]
                )
            else:
                self.control_history = padding
        elif control_history:
            self.control_history = np.array(control_history[:count])
        else:
            self.control_history = np.zeros(
                count
            )  # Should catch this logic branch but safer to init

        # Default Covariance: 0.1=certain, 10=uncertain
        if covariance and len(covariance) > 0:
            self.covariance = np.array(covariance)
            # Resize if dimensions mismatch (safety)
            if self.covariance.shape != (count, count):
                self.covariance = np.eye(count) * 1.0
        else:
            self.covariance = np.eye(count) * 1.0

        self.rls_forgetting = float(rls_forgetting)
        self.control_regularization = float(control_regularization)

    def to_attributes(self) -> dict[str, Any]:
        """Serialize state to entity attributes."""
        return {
            "weights": self.weights.tolist(),
            "covariance": self.covariance.tolist(),
            "control_history": [
                float(x) if not np.isnan(x) else None for x in self.control_history
            ],
            "rls_forgetting": self.rls_forgetting,
            "control_regularization": self.control_regularization,
        }

    @classmethod
    def from_attributes(cls, attrs: dict[str, Any]) -> "State":
        """Deserialize from entity attributes."""
        # Clean up None values in history back to NaN or 0
        if "control_history" in attrs:
            hist = attrs["control_history"]
            attrs["control_history"] = [x if x is not None else np.nan for x in hist]

        return cls(**attrs)


class AdaptiveFIRController:
    """Adaptive Finite Impulse Response (FIR) Controller."""

    def __init__(self, state: State | None = None):
        self.state = state if state else State()

    @property
    def fir_order(self):
        """Return the number of weights (FIR order)."""
        return self.state.weights.size

    def update(
        self, target: float, measured: float, control: int, min_out: int, max_out: int
    ) -> tuple[int, dict[str, Any]]:
        """Run the main control loop.

        1. Learn: Update weights based on predicted vs actual (RLS).
        2. Plan: Calculate next control signal (Inverse Control).
        """
        s = self.state

        lambda_rls = s.rls_forgetting
        lambda_control = s.control_regularization

        # --- 0. VALID HISTORY CHECK ---
        # Cannot learn if history contains NaNs (initial startup)
        history_valid = not np.isnan(s.control_history).any()

        # --- 1. LEARNING (Recursive Least Squares) ---
        prediction_error = 0.0

        if history_valid:
            # Regressor vector (phi) is the history vector.
            phi = s.control_history

            # Compute Gain Vector (K)
            # P * phi
            P_phi = np.dot(s.covariance, phi)
            # Denominator (Scalar)
            phi_P_phi = np.dot(phi.T, P_phi)
            denom = lambda_rls + phi_P_phi

            # Safety: denom shouldn't be 0 if lambda_rls > 0
            if denom < 1e-9:
                denom = 1e-9

            K = P_phi / denom

            # Prediction Error
            y_hat = np.dot(s.weights, phi)
            error = measured - y_hat
            prediction_error = error

            # Update Weights
            s.weights = s.weights + K * error

            # Update Covariance Matrix
            # P = (P - K * phi^T * P) / lambda
            term2 = np.outer(K, P_phi)
            s.covariance = (s.covariance - term2) / lambda_rls

            # Numerical Stability Check (Trace Monitoring)
            if np.trace(s.covariance) > 1000:
                s.covariance = np.eye(self.fir_order) * 10

        # --- 2. CONTROL (Regularized Inverse) ---

        # Solve for u(t):
        # u(t) = (Target - Free_Response) / (w[0] + lambda)

        # Free Response (Effect of past actions)
        # w[1:] dot u_past[:-1]
        # Note: If history has NaNs, we treat them as 0 for prediction safety
        safe_history = np.nan_to_num(s.control_history)
        free_response = np.dot(s.weights[1:], safe_history[:-1])

        needed = target - free_response

        # Regularized Gain
        denom_control = s.weights[0] + lambda_control

        # Safety: Avoid divide by zero
        if abs(denom_control) < 0.1:
            denom_control = 0.1 * (1 if denom_control >= 0 else -1)

        u_calculated = needed / denom_control

        # --- 3. SATURATION & UPDATE ---

        # Clamp & Quantize
        u_final = int(max(min_out, min(max_out, round(u_calculated))))

        # Update History
        # Shift Right, Insert 'control' (last output) at Head
        s.control_history = np.roll(s.control_history, 1)
        s.control_history[0] = control

        # Metrics
        cost = (target - measured) ** 2

        return u_final, {
            "cost": float(cost),
            "system_gain": float(np.sum(s.weights)),
            "immediate_gain": float(s.weights[0]),
            "prediction_error": float(prediction_error) if history_valid else 0.0,
        }
