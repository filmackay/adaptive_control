# Adaptive FIR Control Design

This integration implements an **Adaptive Model Predictive Controller (MPC)** using a **Finite Impulse Response (FIR)** filter model, learned in real-time via **Recursive Least Squares (RLS)**.

> [!NOTE]
> This logic was originally developed as a Pyscript automation and ported to a native Home Assistant integration for better performance, usability, and distribution.

## Core Concepts

### 1. The "Weights" (Impulse Response)
The controller models the physical system (e.g., EV Charger) as an FIR filter. The "weights" array represents the system's memory of past inputs.

If `weights = [0.0, 0.1, 0.5, 0.2]`, it means:
- A change in input **1 second ago** has **0.0** impact now (Dead Time).
- A change in input **2 seconds ago** has **0.1** impact now (Ramp Up).
- A change in input **3 seconds ago** has **0.5** impact now (Peak Response).
- A change in input **4 seconds ago** has **0.2** impact now (Settling).

The sum of all weights is the **Static Gain** (or Steady-State Gain). If I send a constant input of 10 Amps, and the system settles at 9.5 Amps, the System Gain is 0.95. Ideally, for a 1:1 control system, this should be 1.0.

### 2. The Control Loop
The controller runs a continuous loop (typically every 10-60 seconds):

1.  **Measure**: Read the current `measured` value (e.g., Grid Import) and the last `control` output (e.g., EV Charger Amps).
2.  **Learn (RLS)**: Compare the *actual* change in measurement to what the model *predicted*. Update the weights to minimize this prediction error. This allows the controller to **learn the dead-time and gain automatically**.
3.  **Plan (Inverse Control)**: Calculate the optimal control output `u(t)` to achieve the `target` (e.g., 0 Grid Import), accounting for the known system delay represented by the weights.

### 3. Tuning Parameters

While the controller is self-tuning, it has two "Hyperparameters" that govern *how* it learns and acts.

#### RLS Forgetting Factor (`lambda_rls`)
*   **Default:** `0.99`
*   **Description:** Determines the "memory" of the learner.
    *   `1.0`: Infinite memory. Good for static systems that never change.
    *   `0.99`: Adaptive. Good for slowly changing systems (e.g., battery voltage drops, grid voltage changes).
    *   `< 0.95`: Fast adaptation. Good for systems that change drastically, but risk of instability due to noise.

#### Control Regularization (`lambda_control`)
*   **Default:** `0.5`
*   **Description:** Damping factor for the control action. It adds a penalty for "effort" (Control Magnitude) in the Inverse Control calculation.
    *   `> 1.0`: **Passive**. Sluggish response, very low overshoot risk. Use if the system is noisy or safety is critical.
    *   `0.1 - 1.0`: **Balanced**. Fast response with minimal overshoot.
    *   `< 0.1`: **Aggressive**. Very fast response, high risk of overshoot/oscillation.
