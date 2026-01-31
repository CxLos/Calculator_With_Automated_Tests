import pytest
from app.operations import addition, subtraction, multiplication, division

def test_addition():
    assert addition(1,1) == 2 # type: ignore

def test_subtraction():
    assert subtraction(1,1) == 0

def test_multiplication():
    assert multiplication(2,2) == 4

def test_division_positive():
    assert division(9,3) == 3

def test_division_negative():
    assert division(4, -2) == -2

def test_division_by_zero():
    """Test division by zero."""
    with pytest.raises(ValueError, match="Division by zero is not allowed."):
        division(1, 0)

# def test_division_negative():
#     with pytest.raises(ZeroDivisionError): # Expecting divide by 0 error
#         division(1,0)