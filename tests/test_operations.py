
""" 
tests/test_operations.py 

This portion of the code is responsible for testing the basic mathematical operations (addition, subtraction, multiplication, and division) that are defined in the "Operations" class.

"""

# ============== Imports ============== #
import pytest
from typing import Union
from app.operations import Operations  

Number = Union[int, float]

# ============== Addition Unit Tests ============== #

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (7, 13, 20),           
        (0, 0, 0),           
        (-4, 1, -3),          
        (2.1, 7.8, 9.9),     
        (-6.5, -3.5, -10.0),   
    ],
    ids=[
        "add_two_positive_integers",
        "add_two_zeros",
        "add_negative_and_positive_integer",
        "add_two_positive_floats",
        "add_negative_float_and_positive_float",
    ]
)

def test_addition(a: Number, b: Number, expected: Number) -> None:

    result = Operations.addition(a, b)

    assert result == expected, f"Expected addition({a}, {b}) to be {expected}, but got {result}"

# ============== Subtraction Unit Tests ============== #

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (7, 3, 4),           
        (0, 0, 0),           
        (-5, -1, -4),        
        (11.0, 5.0, 6.0),    
        (-10.0, -8.0, -2.0), 
    ],
    ids=[
        "subtract_smaller_positive_integer_from_larger",
        "subtract_two_zeros",
        "subtract_negative_integer_from_negative_integer",
        "subtract_two_positive_floats",
        "subtract_two_negative_floats",
    ]
)

def test_subtraction(a: Number, b: Number, expected: Number) -> None:

    
    result = Operations().subtraction(a, b)
    
    assert result == expected, f"Expected subtraction({a}, {b}) to be {expected}, but got {result}"

# ============== Multiplication Unit Tests ============== #

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (4, 5, 20),          
        (0, 9, 0),          
        (-2, -4, 8),         
        (2.7, 5.0, 13.5),    
        (-3.5, 4.0, -14.0),  
    ],
    ids=[
        "multiply_two_positive_integers",
        "multiply_zero_with_positive_integer",
        "multiply_two_negative_integers",
        "multiply_two_positive_floats",
        "multiply_negative_float_with_positive_float",
    ]
)

def test_multiplication(a: Number, b: Number, expected: Number) -> None:

    result = Operations.multiplication(a, b)

    assert result == expected, f"Expected multiplication({a}, {b}) to be {expected}, but got {result}"

# ============== Division Unit Tests ============== #

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (9, 3, 3.0),          
        (-12, -3, 4.0),        
        (7.0, 2.0, 3.5),       
        (-5.0, 2.0, -2.5),     
        (0, 5, 0.0),            
    ],
    ids=[
        "divide_two_positive_integers",
        "divide_two_negative_integers",
        "divide_two_positive_floats",
        "divide_negative_float_by_positive_float",
        "divide_zero_by_positive_integer",
    ]
)

def test_division(a: Number, b: Number, expected: float) -> None:

    result = Operations.division(a, b)
    
    assert result == expected, f"Expected division({a}, {b}) to be {expected}, but got {result}"

# ============== Negative Division Unit Tests ============== #

@pytest.mark.parametrize(
    "a, b",
    [
        (2, 0),   
        (-2, 0),   
        (0, 0),   
    ],
    ids=[
        "divide_positive_dividend_by_zero",
        "divide_negative_dividend_by_zero",
        "divide_zero_by_zero",
    ]
)

def test_division_by_zero(a: Number, b: Number) -> None:
    
    with pytest.raises(ValueError, match="Division by zero is not allowed.") as excinfo:
        Operations.division(a, b)
    
    assert "Division by zero is not allowed." in str(excinfo.value), \
        f"Expected error message 'Division by zero is not allowed.', but got '{excinfo.value}'"
    
# =============================================================================

# def test_division_negative():
#     with pytest.raises(ZeroDivisionError): # Expecting divide by 0 error
#         division(1,0)