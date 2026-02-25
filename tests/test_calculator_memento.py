"""
Tests for CalculatorMemento class.

This test module covers the Memento pattern implementation for the calculator,
testing state serialization and deserialization functionality.
"""

import datetime
import pytest
from decimal import Decimal
from app.calculation import Calculation
from app.calculator.calculator_memento import CalculatorMemento


class TestCalculatorMemento:
    """Test cases for CalculatorMemento class."""

    def test_to_dict_empty_history(self):
        """Test to_dict method with empty history."""
        # Create memento with empty history
        timestamp = datetime.datetime(2024, 1, 1, 12, 0, 0)
        memento = CalculatorMemento(history=[], timestamp=timestamp)
        
        # Convert to dictionary
        result = memento.to_dict()
        
        # Verify structure
        assert 'history' in result
        assert 'timestamp' in result
        assert result['history'] == []
        assert result['timestamp'] == timestamp.isoformat()

    def test_to_dict_with_calculations(self):
        """Test to_dict method with multiple calculations."""
        # Create calculations
        calc1 = Calculation("Addition", Decimal('5'), Decimal('3'))
        calc2 = Calculation("Addition", Decimal('10'), Decimal('2'))
        
        # Create memento with calculations
        timestamp = datetime.datetime(2024, 1, 1, 12, 0, 0)
        memento = CalculatorMemento(history=[calc1, calc2], timestamp=timestamp)
        
        # Convert to dictionary
        result = memento.to_dict()
        
        # Verify structure
        assert 'history' in result
        assert 'timestamp' in result
        assert len(result['history']) == 2
        assert result['timestamp'] == timestamp.isoformat()
        
        # Verify calculation data is serialized
        assert isinstance(result['history'][0], dict)
        assert isinstance(result['history'][1], dict)

    def test_from_dict_empty_history(self):
        """Test from_dict method with empty history."""
        # Test data
        timestamp_str = "2024-01-01T12:00:00"
        data = {
            'history': [],
            'timestamp': timestamp_str
        }
        
        # Create memento from dictionary
        memento = CalculatorMemento.from_dict(data)
        
        # Verify reconstruction
        assert isinstance(memento, CalculatorMemento)
        assert memento.history == []
        assert memento.timestamp == datetime.datetime.fromisoformat(timestamp_str)

    def test_from_dict_with_calculations(self):
        """Test from_dict method with calculations."""
        # Create test calculations and convert to dict format
        calc1 = Calculation("Addition", Decimal('5'), Decimal('3'))
        calc2 = Calculation("Addition", Decimal('10'), Decimal('2'))
        
        timestamp_str = "2024-01-01T12:00:00"
        data = {
            'history': [calc1.to_dict(), calc2.to_dict()],
            'timestamp': timestamp_str
        }
        
        # Create memento from dictionary
        memento = CalculatorMemento.from_dict(data)
        
        # Verify reconstruction
        assert isinstance(memento, CalculatorMemento)
        assert len(memento.history) == 2
        assert isinstance(memento.history[0], Calculation)
        assert isinstance(memento.history[1], Calculation)
        assert memento.timestamp == datetime.datetime.fromisoformat(timestamp_str)

    def test_roundtrip_serialization(self):
        """Test complete roundtrip: to_dict followed by from_dict."""
        # Create original memento with calculations
        calc1 = Calculation("Addition", Decimal('7'), Decimal('4'))
        calc2 = Calculation("Addition", Decimal('15'), Decimal('5'))
        
        original_timestamp = datetime.datetime(2024, 2, 15, 10, 30, 45)
        original_memento = CalculatorMemento(
            history=[calc1, calc2], 
            timestamp=original_timestamp
        )
        
        # Serialize to dict and back
        data = original_memento.to_dict()
        restored_memento = CalculatorMemento.from_dict(data)
        
        # Verify complete preservation
        assert len(restored_memento.history) == len(original_memento.history)
        assert restored_memento.timestamp == original_memento.timestamp
        
        # Verify calculations are equivalent
        for original_calc, restored_calc in zip(original_memento.history, restored_memento.history):
            assert restored_calc.operand1 == original_calc.operand1
            assert restored_calc.operand2 == original_calc.operand2
            assert restored_calc.operation == original_calc.operation

    def test_timestamp_default_factory(self):
        """Test that default timestamp is created when not provided."""
        # Create memento without explicit timestamp
        before = datetime.datetime.now()
        memento = CalculatorMemento(history=[])
        after = datetime.datetime.now()
        
        # Verify timestamp is between before and after
        assert before <= memento.timestamp <= after

    def test_to_dict_preserves_calculation_data(self):
        """Test that to_dict preserves all calculation data correctly."""
        # Create calculation with specific values
        calc = Calculation("Addition", Decimal('123.45'), Decimal('67.89'))
        memento = CalculatorMemento(history=[calc])
        
        # Serialize
        result = memento.to_dict()
        
        # Verify calculation data is preserved in serialized form
        calc_dict = result['history'][0]
        assert 'operand1' in calc_dict
        assert 'operand2' in calc_dict
        assert 'operation' in calc_dict

    def test_from_dict_handles_complex_timestamps(self):
        """Test from_dict with microsecond precision timestamps."""
        # Test with microsecond precision
        timestamp_str = "2024-03-15T14:25:30.123456"
        data = {
            'history': [],
            'timestamp': timestamp_str
        }
        
        memento = CalculatorMemento.from_dict(data)
        
        # Verify microsecond precision is preserved
        expected_timestamp = datetime.datetime.fromisoformat(timestamp_str)
        assert memento.timestamp == expected_timestamp
        assert memento.timestamp.microsecond == 123456