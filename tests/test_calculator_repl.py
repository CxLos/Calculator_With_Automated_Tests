"""
This package contains unit tests for the calculator REPL functionality, ensuring that the interactive command-line interface operates correctly and handles user input as expected.
"""

# ======= Imports ======= #
from decimal import Decimal
import logging
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from app.calculator import Calculator
from app.other.exceptions import OperationError, ValidationError
from app.other.history import AutoSaveObserver, LoggingObserver
from app.operation.operation import OperationFactory
from app.calculator.calculator_repl import calculator_repl

class TestCalculatorREPL:
    """Test cases for Calculator REPL functionality."""

    @patch('builtins.input')
    @patch('builtins.print')
    def test_help_command(self, mock_print, mock_input):
        """Test the help command displays all available commands."""
        mock_input.side_effect = ['help', 'exit']
        
        calculator_repl()
        
        # Verify help content was printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        help_text = ''.join(print_calls)
        assert 'Available commands:' in help_text
        assert 'add, subtract, multiply, divide, power, root' in help_text
        assert 'history - Show calculation history' in help_text
        assert 'exit - Exit the calculator' in help_text

    @patch('builtins.input')
    @patch('builtins.print')
    def test_exit_command_successful_save(self, mock_print, mock_input):
        """Test exit command with successful history save."""
        mock_input.side_effect = ['exit']
        
        with patch.object(Calculator, 'save_history') as mock_save:
            mock_save.return_value = None  # Successful save
            
            calculator_repl()
            
            # Verify save was attempted and success message printed
            mock_save.assert_called_once()
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("History saved successfully." in call for call in print_calls)
            assert any("Goodbye!" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_exit_command_save_failure(self, mock_print, mock_input):
        """Test exit command with failed history save."""
        mock_input.side_effect = ['exit']
        
        with patch.object(Calculator, 'save_history') as mock_save:
            mock_save.side_effect = Exception("Save failed")
            
            calculator_repl()
            
            # Verify warning message was printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Warning: Could not save history: Save failed" in call for call in print_calls)
            assert any("Goodbye!" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_history_command_empty_history(self, mock_print, mock_input):
        """Test history command with empty history."""
        mock_input.side_effect = ['history', 'exit']
        
        with patch.object(Calculator, 'show_history', return_value=[]):
            calculator_repl()
            
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("No calculations in history" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_history_command_with_calculations(self, mock_print, mock_input):
        """Test history command with existing calculations."""
        mock_input.side_effect = ['history', 'exit']
        
        mock_history = ["5 + 3 = 8", "10 - 4 = 6"]
        with patch.object(Calculator, 'show_history', return_value=mock_history):
            calculator_repl()
            
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Calculation History:" in call for call in print_calls)
            assert any("1. 5 + 3 = 8" in call for call in print_calls)
            assert any("2. 10 - 4 = 6" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_clear_command(self, mock_print, mock_input):
        """Test clear command."""
        mock_input.side_effect = ['clear', 'exit']
        
        with patch.object(Calculator, 'clear_history') as mock_clear:
            calculator_repl()
            
            mock_clear.assert_called_once()
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("History cleared" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_undo_command_successful(self, mock_print, mock_input):
        """Test undo command with successful undo."""
        mock_input.side_effect = ['undo', 'exit']
        
        with patch.object(Calculator, 'undo', return_value=True):
            calculator_repl()
            
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Operation undone" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_undo_command_nothing_to_undo(self, mock_print, mock_input):
        """Test undo command with nothing to undo."""
        mock_input.side_effect = ['undo', 'exit']
        
        with patch.object(Calculator, 'undo', return_value=False):
            calculator_repl()
            
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Nothing to undo" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_redo_command_successful(self, mock_print, mock_input):
        """Test redo command with successful redo."""
        mock_input.side_effect = ['redo', 'exit']
        
        with patch.object(Calculator, 'redo', return_value=True):
            calculator_repl()
            
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Operation redone" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_redo_command_nothing_to_redo(self, mock_print, mock_input):
        """Test redo command with nothing to redo."""
        mock_input.side_effect = ['redo', 'exit']
        
        with patch.object(Calculator, 'redo', return_value=False):
            calculator_repl()
            
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Nothing to redo" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_save_command_successful(self, mock_print, mock_input):
        """Test save command with successful save."""
        mock_input.side_effect = ['save', 'exit']
        
        with patch.object(Calculator, 'save_history') as mock_save:
            mock_save.return_value = None  # Successful save
            
            calculator_repl()
            
            # Verify save was called at least once for the save command
            # (it will be called again during exit)
            assert mock_save.call_count >= 2
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("History saved successfully" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_save_command_failure(self, mock_print, mock_input):
        """Test save command with save failure."""
        mock_input.side_effect = ['save', 'exit']
        
        with patch.object(Calculator, 'save_history') as mock_save:
            mock_save.side_effect = Exception("Save error")
            
            calculator_repl()
            
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Error saving history: Save error" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_load_command_successful(self, mock_print, mock_input):
        """Test load command with successful load."""
        mock_input.side_effect = ['load', 'exit']
        
        with patch.object(Calculator, 'load_history') as mock_load:
            mock_load.return_value = None  # Successful load
            
            calculator_repl()
            
            # Verify load was called at least once
            mock_load.assert_called()
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("History loaded successfully" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_load_command_failure(self, mock_print, mock_input):
        """Test load command with load failure."""
        mock_input.side_effect = ['load', 'exit']
        
        with patch.object(Calculator, 'load_history') as mock_load:
            mock_load.side_effect = Exception("Load error")
            
            calculator_repl()
            
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Error loading history: Load error" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_arithmetic_operation_successful(self, mock_print, mock_input):
        """Test successful arithmetic operation."""
        mock_input.side_effect = ['add', '5', '3', 'exit']
        
        mock_operation = Mock()
        mock_calculator = Mock()
        mock_calculator.perform_operation.return_value = Decimal('8')
        
        with patch('app.calculator.calculator_repl.Calculator', return_value=mock_calculator), \
             patch('app.calculator.calculator_repl.OperationFactory.create_operation', return_value=mock_operation):
            
            calculator_repl()
            
            mock_calculator.set_operation.assert_called_once_with(mock_operation)
            mock_calculator.perform_operation.assert_called_once_with('5', '3')
            
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Result: 8" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_arithmetic_operation_non_decimal_result(self, mock_print, mock_input):
        """Test arithmetic operation with non-Decimal result."""
        mock_input.side_effect = ['add', '5', '3', 'exit']
        
        mock_operation = Mock()
        mock_calculator = Mock()
        mock_calculator.perform_operation.return_value = 8  
        
        with patch('app.calculator.calculator_repl.Calculator', return_value=mock_calculator), \
             patch('app.calculator.calculator_repl.OperationFactory.create_operation', return_value=mock_operation):
            
            calculator_repl()
            
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Result: 8" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_arithmetic_operation_cancel_first_number(self, mock_print, mock_input):
        """Test arithmetic operation cancelled at first number."""
        mock_input.side_effect = ['add', 'cancel', 'exit']
        
        calculator_repl()
        
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Operation cancelled" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_arithmetic_operation_cancel_second_number(self, mock_print, mock_input):
        """Test arithmetic operation cancelled at second number."""
        mock_input.side_effect = ['add', '5', 'cancel', 'exit']
        
        calculator_repl()
        
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Operation cancelled" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_arithmetic_operation_validation_error(self, mock_print, mock_input):
        """Test arithmetic operation with validation error."""
        mock_input.side_effect = ['divide', '5', '0', 'exit']
        
        mock_operation = Mock()
        mock_calculator = Mock()
        mock_calculator.perform_operation.side_effect = ValidationError("Division by zero")
        
        with patch('app.calculator.calculator_repl.Calculator', return_value=mock_calculator), \
             patch('app.calculator.calculator_repl.OperationFactory.create_operation', return_value=mock_operation):
            
            calculator_repl()
            
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Error: Division by zero" in call for call in print_calls)

    @patch('builtins.input') 
    @patch('builtins.print')
    def test_arithmetic_operation_operation_error(self, mock_print, mock_input):
        """Test arithmetic operation with operation error."""
        mock_input.side_effect = ['power', '5', '-1', 'exit']
        
        mock_operation = Mock()
        mock_calculator = Mock()
        mock_calculator.perform_operation.side_effect = OperationError("Negative power")
        
        with patch('app.calculator.calculator_repl.Calculator', return_value=mock_calculator), \
             patch('app.calculator.calculator_repl.OperationFactory.create_operation', return_value=mock_operation):
            
            calculator_repl()
            
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Error: Negative power" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_arithmetic_operation_unexpected_error(self, mock_print, mock_input):
        """Test arithmetic operation with unexpected error."""
        mock_input.side_effect = ['add', '5', '3', 'exit']
        
        mock_operation = Mock()
        mock_calculator = Mock()
        mock_calculator.perform_operation.side_effect = RuntimeError("Unexpected error")
        
        with patch('app.calculator.calculator_repl.Calculator', return_value=mock_calculator), \
             patch('app.calculator.calculator_repl.OperationFactory.create_operation', return_value=mock_operation):
            
            calculator_repl()
            
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Unexpected error: Unexpected error" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_unknown_command(self, mock_print, mock_input):
        """Test handling of unknown command."""
        mock_input.side_effect = ['invalid_command', 'exit']
        
        calculator_repl()
        
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Unknown command: 'invalid_command'. Type 'help' for available commands." in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_keyboard_interrupt_handling(self, mock_print, mock_input):
        """Test handling of keyboard interrupt (Ctrl+C)."""
        mock_input.side_effect = [KeyboardInterrupt(), 'exit']
        
        calculator_repl()
        
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Operation cancelled" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_eof_error_handling(self, mock_print, mock_input):
        """Test handling of EOF error (Ctrl+D)."""
        mock_input.side_effect = EOFError()
        
        calculator_repl()
        
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Input terminated. Exiting..." in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_general_exception_handling(self, mock_print, mock_input):
        """Test handling of general exceptions during command processing."""
        mock_input.side_effect = [Exception("General error"), 'exit']
        
        calculator_repl()
        
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Error: General error" in call for call in print_calls)

    @patch('builtins.input')
    @patch('builtins.print')
    @patch('logging.error')
    def test_fatal_initialization_error(self, mock_log_error, mock_print, mock_input):
        """Test handling of fatal error during calculator initialization."""
        with patch('app.calculator.calculator_repl.Calculator', side_effect=Exception("Fatal init error")):
            
            with pytest.raises(Exception, match="Fatal init error"):
                calculator_repl()
            
            mock_log_error.assert_called_once()
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Fatal error: Fatal init error" in call for call in print_calls)