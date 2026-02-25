import pytest
from pathlib import Path
from decimal import Decimal  
from tempfile import TemporaryDirectory
from unittest.mock import patch
from app.calculator.calculator_config import CalculatorConfig, get_project_root
from app.other.exceptions import ConfigurationError


def test_calculator_config_default_values():
    """Test CalculatorConfig with default values."""
    config = CalculatorConfig()
    
    assert config.max_history_size >= 1  
    assert config.auto_save in [True, False]  
    assert config.precision >= 1  
    assert config.max_input_value > 0  
    assert config.default_encoding in ['utf-8', 'ascii', 'utf-16']  


def test_calculator_config_custom_values():
    """Test CalculatorConfig with custom values.""" 
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        config = CalculatorConfig(
            base_dir=temp_path,
            max_history_size=500,
            auto_save=False,
            precision=5,
            max_input_value=Decimal('1000'),
            default_encoding='ascii'
        )
        
        assert config.base_dir == temp_path
        assert config.max_history_size == 500
        assert config.auto_save is False
        assert config.precision == 5
        assert config.max_input_value == Decimal('1000')
        assert config.default_encoding == 'ascii'


def test_calculator_config_environment_variables():
    """Test CalculatorConfig reads from environment variables."""
    env_vars = {
        'CALCULATOR_MAX_HISTORY_SIZE': '2000',
        'CALCULATOR_AUTO_SAVE': 'false',
        'CALCULATOR_PRECISION': '15',
        'CALCULATOR_MAX_INPUT_VALUE': '1e500',
        'CALCULATOR_DEFAULT_ENCODING': 'utf-16'
    }
    
    with patch.dict('os.environ', env_vars):
        config = CalculatorConfig()
        
        assert config.max_history_size == 2000
        assert config.auto_save is False
        assert config.precision == 15
        assert config.max_input_value == Decimal('1e500')
        assert config.default_encoding == 'utf-16'


def test_get_project_root():
    """Test get_project_root function."""
    root = get_project_root()
    assert isinstance(root, Path)
    # Should be two levels up from calculator_config.py
    assert root.name in ["Projects", "Calculator_With_Automated_Tests"] or "Calculator" in str(root)


def test_config_properties():
    """Test configuration properties return correct paths."""
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)
        
        # Test default paths
        assert config.log_dir == temp_path / "logs"
        assert config.history_dir == temp_path / "history" 
        assert config.history_file == temp_path / "history/calculator_history.csv"
        assert config.log_file == temp_path / "logs/calculator.log"


def test_config_properties_with_environment():
    """Test configuration properties with environment variables."""
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)
        
        env_vars = {
            'CALCULATOR_LOG_DIR': str(temp_path / "custom_logs"),
            'CALCULATOR_HISTORY_DIR': str(temp_path / "custom_history"),
            'CALCULATOR_HISTORY_FILE': str(temp_path / "custom_history/custom.csv"),
            'CALCULATOR_LOG_FILE': str(temp_path / "custom_logs/custom.log")
        }
        
        with patch.dict('os.environ', env_vars):
            assert config.log_dir == temp_path / "custom_logs"
            assert config.history_dir == temp_path / "custom_history"
            assert config.history_file == temp_path / "custom_history/custom.csv"
            assert config.log_file == temp_path / "custom_logs/custom.log"


def test_validate_max_history_size_negative():
    """Test validation fails for negative max_history_size (line 172)."""
    config = CalculatorConfig(max_history_size=-1)
    
    with pytest.raises(ConfigurationError, match="max_history_size must be positive"):
        config.validate()


def test_validate_max_history_size_zero():
    """Test validation fails for zero max_history_size (line 172)."""
    config = CalculatorConfig()
    
    # Set the attribute directly to bypass the 'or' logic in __init__
    config.max_history_size = 0
    
    with pytest.raises(ConfigurationError, match="max_history_size must be positive"):
        config.validate()


def test_validate_precision_negative():
    """Test validation fails for negative precision (line 174)."""
    config = CalculatorConfig(precision=-5)
    
    with pytest.raises(ConfigurationError, match="precision must be positive"):
        config.validate()


def test_validate_precision_zero():
    """Test validation fails for zero precision (line 174)."""
    config = CalculatorConfig()
    
    # Set the attribute directly to bypass the 'or' logic in __init__
    config.precision = 0
    
    with pytest.raises(ConfigurationError, match="precision must be positive"):
        config.validate()


def test_validate_max_input_value_negative():
    """Test validation fails for negative max_input_value (line 176)."""
    config = CalculatorConfig(max_input_value=Decimal('-100'))
    
    with pytest.raises(ConfigurationError, match="max_input_value must be positive"):
        config.validate()


def test_validate_max_input_value_zero():
    """Test validation fails for zero max_input_value (line 176)."""
    config = CalculatorConfig()
    
    # Set the attribute directly to bypass the 'or' logic in __init__
    config.max_input_value = Decimal('0')
    
    with pytest.raises(ConfigurationError, match="max_input_value must be positive"):
        config.validate()


def test_validate_success():
    """Test validation passes with valid configuration."""
    config = CalculatorConfig(
        max_history_size=100,
        precision=5,
        max_input_value=Decimal('1000')
    )
    
    # Should not raise any exception
    config.validate()