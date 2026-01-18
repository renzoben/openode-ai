# Guide 01: Industrial Data Validation
### *From Raw Signals to Secure Data*

## 1. The Problem
In industrial environments (OT), sensors often fail or produce "noise". If we send a temperature of 5000°C to our database, we can crash our dashboards or confuse our AI models.

## 2. The Solution: Pydantic
We use **Pydantic** to create a "Contract". If the data doesn't fit the contract, it doesn't pass.

### Key Concepts for this module:
* **BaseModel**: It's like a template for our data.
* **Field**: Defines the rules (e.g., minimum and maximum temperature).
* **Asyncio**: Allows the program to wait for data without stopping the whole system.

## 3. How the code works
1. **The Schema**: We define that a `S7-1200` node must send `temperature`, `pressure`, and a `status`.
2. **The Simulator**: We generate random numbers to mimic a real PLC.
3. **The Validation**: The `try...except` block catches errors. If a number is out of range, it prints an ERROR instead of breaking the system.

---
*This is part of the OpeNode.ai "The Bridge" project.*
