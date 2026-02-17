"""
This module provides a professional-grade calculator that can add, subtract,
multiply, and divide numbers based on user input. It leverages the Calculation
classes for operations and includes additional features like help commands and
history tracking to enhance user experience.

This code also demonstrates two common programming paradigms in Python:
- LBYL (Look Before You Leap)
- EAFP (Easier to Ask Forgiveness than Permission)

Throughout the code, comments explain where and why these paradigms are used,
providing a comprehensive learning experience for students.
"""

import sys
try:  # pragma: no cover
    import readline  # Unix-like systems: enables command history and line editing
except ImportError:  # pragma: no cover
    try:  # pragma: no cover
        import pyreadline as readline 
    except ImportError:  # pragma: no cover
        readline = None

from typing import List
from app.calculation import Calculation, CalculationFactory


def display_help() -> None:
    """
    Displays the help message with usage instructions and supported operations.
    """
    help_message = """
            Calculator REPL Help
            --------------------
            Usage:
                <operation> <number1> <number2>
                - Perform a calculation with the specified operation and two numbers.
                - Supported operations:
                    add       : Adds two numbers.
                    subtract  : Subtracts the second number from the first.
                    multiply  : Multiplies two numbers.
                    divide    : Divides the first number by the second.
                    power     : Raises the first number to the power of the second.
                    modulus   : Returns the remainder of the division of the first number by the second.
                    sqrt      : Returns the square root of a number.

            Special Commands:
                help      : Display this help message.
                history   : Show the history of calculations.
                exit      : Exit the calculator.

            Examples:
                add 10 5
                subtract 15.5 3.2
                multiply 7 8
                divide 20 4
                power 2 3
                modulus 10 3
                sqrt 16
                """
    print(help_message)

def display_history(history: List[Calculation]) -> None:
    """
    Displays the history of calculations performed during the session.

    Parameters:
        history (List[Calculation]): A list of Calculation objects representing past calculations.
    """
    if not history:
        print("No calculations performed yet.")
    else:
        print("Calculation History:")
        for idx, calculation in enumerate(history, start=1):
            print(f"{idx}. {calculation}")


def calculator() -> None:
    """
    Professional REPL calculator that performs addition, subtraction,
    multiplication, and division using Calculation classes.

    This function demonstrates both LBYL and EAFP programming paradigms.
    """
    history: List[Calculation] = []

    print("Welcome to the Professional Calculator REPL!")
    print("Type 'help' for instructions or 'exit' to quit.\n")

    while True:
        try:
            user_input: str = input(">> ").strip()

            if not user_input:
                print("No input detected. Please enter a command or type 'help' for instructions.\n") # pragma: no cover
                continue # pragma: no cover

            command = user_input.lower()

            if command == "help":
                display_help()
                continue
            elif command == "history":
                display_history(history)
                continue
            elif command == "exit":
                print("Exiting calculator. Goodbye!\n")
                sys.exit(0)  # Exit the program gracefully

            try:
                operation, num1_str, num2_str = user_input.split()
                num1: float = float(num1_str)
                num2: float = float(num2_str)
            except ValueError:
                print("Invalid input. Please follow the format: <operation> <num1> <num2>")
                print("Type 'help' for more information.\n")
                continue  

            try:
                calculation = CalculationFactory.create_calculation(operation, num1, num2)
            except ValueError as ve:

                print(ve)
                print("Type 'help' to see the list of supported operations.\n")
                continue  # Prompt the user again

            try:
                result = calculation.execute()
            except ZeroDivisionError:
                print("Cannot divide by zero.")
                print("Please enter a non-zero divisor.\n")
                continue  
            except Exception as e:
                print(f"An error occurred during calculation: {e}")
                print("Please try again.\n")
                continue  

            result_str: str = f"{calculation}"
            print(f"Result: {result_str}\n")

            history.append(calculation)

        except KeyboardInterrupt:
            print("\nKeyboard interrupt detected. Exiting calculator. Goodbye!")
            sys.exit(0)
        except EOFError:
            print("\nEOF detected. Exiting calculator. Goodbye!")
            sys.exit(0)

if __name__ == "__main__":
    calculator() # pragma: no cover