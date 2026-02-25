import datetime
import logging
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator
from app.calculator.calculator_repl import calculator_repl
from app.calculator.calculator_config import CalculatorConfig
from app.other.exceptions import OperationError, ValidationError
from app.other.history import LoggingObserver, AutoSaveObserver
from app.operation.operation import OperationFactory

# Fixture to initialize Calculator with a temporary directory for file paths
@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        # Patch properties to use the temporary directory paths
        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            # Set return values to use paths within the temporary directory
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            # Return an instance of Calculator with the mocked config
            calc = Calculator(config=config)
            yield calc

            # Close all logging handlers to release log files on Windows
            for handler in logging.root.handlers[:]:
                handler.close()
                logging.root.removeHandler(handler)

# Test Calculator Initialization

def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None

# Test Logging Setup

@patch('app.calculator.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')
        
        # Instantiate calculator to trigger logging
        calculator = Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")

# Test Adding and Removing Observers

def test_add_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers

def test_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers

# Test Setting Operations

def test_set_operation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation

# Test Performing Operations

def test_perform_operation_addition(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    result = calculator.perform_operation(2, 3)
    assert result == Decimal('5')

def test_perform_operation_validation_error(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)

def test_perform_operation_operation_error(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(2, 3)

# Test Undo/Redo Functionality

def test_undo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.history == []

def test_redo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    calculator.redo()
    assert len(calculator.history) == 1

# Test History Management

@patch('app.calculator.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()

@patch('app.calculator.calculator.pd.read_csv')
@patch('app.calculator.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):
    # Mock CSV data to match the expected format in from_dict
    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['Addition'],
        'operand1': ['2'],
        'operand2': ['3'],
        'result': ['5'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })
    
    # Test the load_history functionality
    try:
        calculator.load_history()
        # Verify history length after loading
        assert len(calculator.history) == 1
        # Verify the loaded values
        assert calculator.history[0].operation == "Addition"
        assert calculator.history[0].operand1 == Decimal("2")
        assert calculator.history[0].operand2 == Decimal("3")
        assert calculator.history[0].result == Decimal("5")
    except OperationError:
        pytest.fail("Loading history failed due to OperationError")
        
            
# Test Clearing History

def test_clear_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

# Test REPL Commands (using patches for input/output handling)

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        mock_print.assert_any_call("History saved successfully.")
        mock_print.assert_any_call("Goodbye!")

@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nAvailable commands:")

@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 5")


# Additional tests to improve coverage

def test_load_history_exception():
    """Test exception handling when load_history fails (lines 77-79)."""
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            # Mock load_history to raise an exception during initialization
            with patch('app.calculator.calculator.Calculator.load_history', side_effect=Exception("Load error")):
                with patch('logging.warning') as mock_warning:
                    calc = Calculator(config=config)
                    mock_warning.assert_called_with("Could not load existing history: Load error")
                    
                    # Close logging handlers to prevent Windows permission errors
                    for handler in logging.root.handlers[:]:
                        handler.close()
                        logging.root.removeHandler(handler)


def test_logging_setup_exception():
    """Test exception handling when logging setup fails (lines 103-106)."""
    with patch('logging.basicConfig', side_effect=Exception("Logging setup failed")):
        with patch('builtins.print') as mock_print:
            with pytest.raises(Exception):
                calc = Calculator()
            mock_print.assert_called_with("Error setting up logging: Logging setup failed")


def test_history_max_size_limiting(calculator):
    """Test history size limiting (line 219).""" 
    # Set a very small max history size
    calculator.config.max_history_size = 2
    
    # Add more calculations than the limit
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(1, 1)  # First calc
    calculator.perform_operation(2, 2)  # Second calc
    calculator.perform_operation(3, 3)  # Third calc - should trim first
    
    # Should only keep the last 2 calculations
    assert len(calculator.history) == 2
    assert calculator.history[0].operand1 == Decimal('2')  # First was trimmed
    assert calculator.history[1].operand1 == Decimal('3')


def test_perform_operation_general_exception(calculator):
    """Test general exception handling in perform_operation (lines 230-233)."""
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    
    # Mock the operation strategy's execute method to raise a general exception  
    calculator.operation_strategy.execute = Mock(side_effect=RuntimeError("General error"))
    
    with pytest.raises(OperationError, match="Operation failed: General error"):
        calculator.perform_operation(2, 3)


def test_save_empty_history(calculator):
    """Test saving empty history (lines 268-275)."""
    # Ensure history is empty
    calculator.history = []
    
    # Mock pandas DataFrame to check the call
    with patch('app.calculator.calculator.pd.DataFrame') as mock_df:
        mock_df.return_value.to_csv = Mock()
        calculator.save_history()
        
        # Should create empty DataFrame with columns
        mock_df.assert_called_with(columns=['operation', 'operand1', 'operand2', 'result', 'timestamp'])


def test_save_history_exception(calculator):
    """Test exception handling when save_history fails."""
    with patch('app.calculator.calculator.pd.DataFrame.to_csv', side_effect=Exception("Save error")):
        with pytest.raises(OperationError, match="Failed to save history: Save error"):
            calculator.save_history()


def test_load_history_file_not_found(calculator):
    """Test load_history when file doesn't exist (lines 309-312)."""
    with patch.object(Path, 'exists', return_value=False):
        calculator.load_history()  # Should handle gracefully


def test_load_empty_history_file(calculator):
    """Test load_history with empty file (line 305)."""
    with patch.object(Path, 'exists', return_value=True):
        with patch('app.calculator.calculator.pd.read_csv', return_value=pd.DataFrame()):
            calculator.load_history()


def test_load_history_exception_handling(calculator):
    """Test exception in load_history."""
    with patch.object(Path, 'exists', return_value=True):
        with patch('app.calculator.calculator.pd.read_csv', side_effect=Exception("Load error")):
            with pytest.raises(OperationError, match="Failed to load history: Load error"):
                calculator.load_history()


def test_get_history_dataframe(calculator):
    """Test get_history_dataframe with calculations (lines 324-333)."""
    # Add a calculation to history
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    
    df = calculator.get_history_dataframe()
    assert len(df) == 1
    assert df.iloc[0]['operation'] == 'Addition'
    assert df.iloc[0]['operand1'] == '2'


def test_show_history(calculator):
    """Test show_history formatting (line 344)."""
    # Add calculations to history
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    
    history_list = calculator.show_history()
    assert len(history_list) == 1
    assert "Addition(2, 3) = 5" in history_list[0]


def test_undo_empty_stack(calculator):
    """Test undo when stack is empty (line 371)."""
    result = calculator.undo()
    assert result is False  # Should return False when nothing to undo


def test_redo_empty_stack(calculator):
    """Test redo when stack is empty (line 390).""" 
    result = calculator.redo()
    assert result is False  # Should return False when nothing to redo
