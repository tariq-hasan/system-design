"""
d_example.py

🔍 Example demonstrating the Dependency Inversion Principle (DIP)

The Dependency Inversion Principle states:
> "High-level modules should not depend on low-level modules. Both should depend on abstractions."
> "Abstractions should not depend on details. Details should depend on abstractions."

This principle helps reduce coupling between components and encourages dependency on interfaces rather than concrete implementations.
"""

# --- ❌ DIP Violation Example ---

class MySQLDatabase:
    def connect(self):
        print("Connecting to MySQL database...")

class ReportService:
    def __init__(self):
        self.database = MySQLDatabase()  # Direct dependency on a low-level class

    def generate_report(self):
        self.database.connect()
        print("Generating report from MySQL database...")

# Problem:
# - `ReportService` is tightly coupled to `MySQLDatabase`.
# - Can't easily switch to another database (e.g., PostgreSQL, MongoDB) without modifying `ReportService`.

# --- ✅ DIP-Compliant Refactored Version ---

from abc import ABC, abstractmethod

# High-level module depends on an abstraction
class Database(ABC):
    @abstractmethod
    def connect(self):
        pass

# Low-level modules implement the abstraction

class MySQLDatabaseDIP(Database):
    def connect(self):
        print("Connecting to MySQL database...")

class PostgreSQLDatabase(Database):
    def connect(self):
        print("Connecting to PostgreSQL database...")

class InMemoryDatabase(Database):
    def connect(self):
        print("Using in-memory database (for testing)...")

# High-level module depends on abstraction, not on concrete class

class ReportServiceDIP:
    def __init__(self, database: Database):
        self.database = database

    def generate_report(self):
        self.database.connect()
        print("Generating report using abstracted database...")

# --- ✅ Test Scenario ---

def main():
    print("=== Using MySQL ===")
    mysql_service = ReportServiceDIP(MySQLDatabaseDIP())
    mysql_service.generate_report()

    print("\n=== Using PostgreSQL ===")
    postgres_service = ReportServiceDIP(PostgreSQLDatabase())
    postgres_service.generate_report()

    print("\n=== Using In-Memory DB (for testing) ===")
    memory_service = ReportServiceDIP(InMemoryDatabase())
    memory_service.generate_report()

if __name__ == "__main__":
    main()
