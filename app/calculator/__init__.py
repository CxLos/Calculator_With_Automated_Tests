
""" 
This file is the "app/calculator.py" file. It contains a simple calculator that can add, subtract, multiply, 
and divide numbers based on what the user types.
"""

from app.operations import Operations

def calculator():
    """Basic REPL calculator that performs addition, subtraction, multiplication, and division."""
    
    print("Welcome to the calculator REPL! Type 'exit' to quit")
    
    while True:

        user_input = input("Enter an operation (add, subtract, multiply, divide) and two numbers, or 'exit' to quit: ")

        if user_input.lower() == "exit":
            print("Exiting calculator...")
            break

        try:
            
            operation, num1, num2 = user_input.split()
            num1, num2 = float(num1), float(num2)
        except ValueError:
  
            print("Invalid input. Please follow the format: <operation> <num1> <num2>")
            continue 

        if operation == "add":
            result = Operations.addition(num1, num2)  

        elif operation == "subtract":
            result = Operations.subtraction(num1, num2)   

        elif operation == "multiply":
            result = Operations.multiplication(num1, num2)  

        elif operation == "divide":
            try:
                result = Operations.division(num1, num2) 
            except ValueError as e:
              
                print(e) 
                continue  
        else:
            print(f"Unknown operation '{operation}'. Supported operations: add, subtract, multiply, divide.")
            continue 

        print(f"Result: {result}")