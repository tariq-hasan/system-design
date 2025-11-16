# 📝 SOLID Principles Cheatsheet

This cheatsheet provides a **quick reference** to the SOLID principles, including their definitions, examples, and tips for best practices.

---

## 🔑 SOLID Overview

SOLID is a set of five design principles that help software developers create more maintainable, flexible, and scalable code:

- **S**: **Single Responsibility Principle (SRP)**
- **O**: **Open/Closed Principle (OCP)**
- **L**: **Liskov Substitution Principle (LSP)**
- **I**: **Interface Segregation Principle (ISP)**
- **D**: **Dependency Inversion Principle (DIP)**

---

## 📏 Single Responsibility Principle (SRP)

> **A class should have only one reason to change.**

### Key Concept:
- A class should only have one job, or responsibility, and that responsibility should be encapsulated by the class.
  
### Example:
```python
# Violation of SRP - class does too many things
class Invoice:
    def calculate_total(self):
        # logic for total calculation
        pass
    
    def print_invoice(self):
        # logic for printing invoice
        pass

# Refactored - Single Responsibility
class Invoice:
    def calculate_total(self):
        # logic for total calculation
        pass

class InvoicePrinter:
    def print(self, invoice):
        # logic for printing invoice
        pass
```

### Best Practices:
- Break classes into smaller, more manageable units.
- Each class should focus on a single aspect of the business logic.

---

## 🔓 Open/Closed Principle (OCP)

> **Software entities should be open for extension but closed for modification.**

### Key Concept:
- You should be able to add new functionality to a system without altering existing code. Instead, extend existing behavior through inheritance or interfaces.

### Example:
```python
# Violation of OCP
class DiscountCalculator:
    def calculate(self, price, discount_type):
        if discount_type == "seasonal":
            return price * 0.9
        elif discount_type == "holiday":
            return price * 0.8
        else:
            return price

# Refactored - Open for extension, closed for modification
class DiscountCalculator:
    def calculate(self, price, discount):
        return discount.apply(price)

class SeasonalDiscount:
    def apply(self, price):
        return price * 0.9

class HolidayDiscount:
    def apply(self, price):
        return price * 0.8
```

### Best Practices:
- Use **polymorphism** and **inheritance** for new behavior.
- Avoid modifying existing code unless absolutely necessary.

---

## 🔄 Liskov Substitution Principle (LSP)

> **Objects of a superclass should be replaceable with objects of a subclass without affecting the correctness of the program.**

### Key Concept:
- Subtypes must be substitutable for their base types without altering the desired behavior of the program.

### Example:
```python
# Violation of LSP
class Bird:
    def fly(self):
        print("Flying")

class Penguin(Bird):  # Penguins can't fly!
    def fly(self):
        raise NotImplementedError("Penguins can't fly!")

# Refactored - Correct substitution
class Bird(ABC):
    @abstractmethod
    def move(self):
        pass

class Sparrow(Bird):
    def move(self):
        print("Flying")

class Penguin(Bird):
    def move(self):
        print("Swimming")
```

### Best Practices:
- Ensure derived classes truly follow the behavior expected of the base class.
- If a subclass can't adhere to the parent class contract, consider rethinking inheritance.

---

## 🔧 Interface Segregation Principle (ISP)

> **Clients should not be forced to implement interfaces they do not use.**

### Key Concept:
- Avoid large, monolithic interfaces. Instead, break them down into smaller, more specific interfaces.

### Example:
```python
# Violation of ISP
class Worker:
    def work(self):
        pass
    def eat(self):
        pass
    def sleep(self):
        pass

class RobotWorker(Worker):
    def work(self):
        pass
    def eat(self):  # Robots don't eat!
        pass
    def sleep(self):  # Robots don't sleep!
        pass

# Refactored - Correct usage of ISP
class Workable:
    def work(self):
        pass

class Eatable:
    def eat(self):
        pass

class Sleepable:
    def sleep(self):
        pass

class RobotWorker(Workable):
    def work(self):
        pass
```

### Best Practices:
- Split large interfaces into smaller, more specific ones.
- Ensure classes implement only the interfaces they need.

---

## 🔄 Dependency Inversion Principle (DIP)

> **High-level modules should not depend on low-level modules. Both should depend on abstractions.**

### Key Concept:
- High-level modules should rely on abstractions (interfaces or abstract classes), not concrete implementations.
- This ensures that changes in low-level modules don't affect high-level modules.

### Example:
```python
# Violation of DIP
class MySQLDatabase:
    def connect(self):
        print("Connecting to MySQL...")

class ReportService:
    def __init__(self):
        self.database = MySQLDatabase()  # Direct dependency

    def generate_report(self):
        self.database.connect()
        print("Generating report")

# Refactored - DIP Compliant
class Database(ABC):
    @abstractmethod
    def connect(self):
        pass

class MySQLDatabase(Database):
    def connect(self):
        print("Connecting to MySQL...")

class ReportService:
    def __init__(self, database: Database):
        self.database = database  # Dependency injection

    def generate_report(self):
        self.database.connect()
        print("Generating report")

# Usage
mysql_db = MySQLDatabase()
report_service = ReportService(mysql_db)
report_service.generate_report()
```

### Best Practices:
- Use **dependency injection** (constructor or setter injection).
- Rely on abstractions (interfaces or abstract classes) to decouple high and low-level modules.

---

## ⚠️ Common Pitfalls

- **Not adhering to SRP**: Having large, complex classes with too many responsibilities.
- **Forgetting OCP**: Modifying existing code instead of extending it.
- **Breaking LSP**: Using inheritance inappropriately where subclasses cannot replace parent classes.
- **Interface bloat (violating ISP)**: Having large interfaces with methods that are irrelevant to certain classes.
- **Tight coupling (violating DIP)**: Directly creating instances of classes within other classes rather than depending on abstractions.

---

## 🌟 Tips for Applying SOLID

1. **Start small**: Apply one principle at a time.
2. **Test-driven development (TDD)**: Helps in applying SOLID by enforcing good design.
3. **Refactor often**: Don’t be afraid to refactor code to improve adherence to SOLID principles.
4. **Use design patterns**: Patterns like Factory, Strategy, and Observer are often SOLID-friendly.
5. **Keep it simple**: SOLID is about improving maintainability, not complexity.

---

## ✨ Visual References

- **UML Diagrams**: Illustrate class hierarchies, interfaces, and dependencies.
- **Flowcharts**: Show decision-making processes for extending behavior (OCP).
- **Class Dependency Graphs**: Help visualize how different classes adhere to SOLID principles.

---

> "SOLID principles are like the rules of a game—learning and practicing them makes you a better software engineer."  
> — Robert C. Martin
