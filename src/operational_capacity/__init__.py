"""Domínio do Simulador de Capacidade Operacional."""

from .calculations import CapacityInputs, CapacityResults, InputValidationError, calculate_capacity

__all__ = [
    "CapacityInputs",
    "CapacityResults",
    "InputValidationError",
    "calculate_capacity",
]
