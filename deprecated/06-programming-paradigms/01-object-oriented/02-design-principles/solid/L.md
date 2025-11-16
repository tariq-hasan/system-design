# 🧱 Liskov Substitution Principle (LSP)

> "Objects of a superclass should be replaceable with objects of a subclass without affecting the correctness of the program."  
> — Barbara Liskov (1987)

---

## 📖 Definition

The **Liskov Substitution Principle** (LSP) states that:

> If class `S` is a subclass of class `T`, then objects of type `T` may be replaced with objects of type `S` **without altering any desirable properties of the program** (correctness, task performed, etc.).

In other words, **subtypes must be substitutable for their base types** without introducing bugs or changing expected behavior.

LSP ensures that inheritance hierarchies model true "is-a" relationships, where derived classes truly represent specialized versions of their base classes.

---

## 🧵 Key Concepts

- Subclasses must **honor the contract** established by the base class
- Do **not override methods in ways that break expectations**
- LSP ensures that **inheritance models "is-a" relationships accurately**
- A subclass should only **strengthen preconditions** and **weaken postconditions**
- The behavior of a subclass should be **predictable** to users of the base class
- LSP violations often indicate that **composition** might be more appropriate than **inheritance**

---

## 🔄 Design by Contract

LSP is closely tied to the concept of "Design by Contract" which specifies:

1. **Preconditions**: Conditions that must be true before a method executes
2. **Postconditions**: Conditions that must be true after a method executes
3. **Invariants**: Conditions that must remain true throughout an object's lifecycle

When extending a class, a subclass must:
- **Not strengthen postconditions** (promise less than the parent)
- **Not weaken preconditions** (require more than the parent)
- **Maintain all invariants** of the parent class

### Example:

```java
// Base class contract
class BankAccount {
    protected double balance;
    
    /**
     * Precondition: amount > 0
     * Postcondition: balance is increased by amount
     */
    public void deposit(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Amount must be positive");
        }
        this.balance += amount;
    }
    
    /**
     * Precondition: amount > 0 and amount <= balance
     * Postcondition: balance is decreased by amount
     */
    public void withdraw(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Amount must be positive");
        }
        if (amount > balance) {
            throw new IllegalArgumentException("Insufficient funds");
        }
        this.balance -= amount;
    }
}

// Compliant subclass
class SavingsAccount extends BankAccount {
    private double interestRate;
    
    // Additional functionality without changing the contract
    public void addInterest() {
        double interest = balance * interestRate;
        deposit(interest);
    }
}

// LSP-violating subclass
class OverdraftAccount extends BankAccount {
    private double overdraftLimit;
    
    /**
     * Violates LSP by weakening precondition:
     * Original required amount <= balance
     * Now allows amount <= balance + overdraftLimit
     */
    @Override
    public void withdraw(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Amount must be positive");
        }
        if (amount > balance + overdraftLimit) {
            throw new IllegalArgumentException("Exceeds overdraft limit");
        }
        this.balance -= amount;
    }
}
```

The `OverdraftAccount` violates LSP because it changes the contract of `withdraw()`. Client code written to work with `BankAccount` might break when given an `OverdraftAccount` if it assumes that after withdrawal, balance will never be negative.

---

## ❌ Common Violations

| Violation Scenario               | Description                                                                 | Real-world Example |
|----------------------------------|-----------------------------------------------------------------------------|-------------------|
| Violating postconditions         | Subclass returns more or less than what the base class promises.           | A `SavingsAccount` subclass that doesn't add interest when `calculateBalance()` is called |
| Violating invariants             | Subclass breaks internal assumptions made by base class users.             | A `Square` subclass of `Rectangle` where changing width also changes height |
| Throwing unexpected exceptions   | Subclass introduces new error paths.                                       | An `ElectricCar` subclass throws an error on `refuel()` rather than handling it appropriately |
| Changing method behavior         | Subclass behaves differently in a way that surprises the caller.           | A `PremiumUser` that ignores usage limits specified in the base `User` class |
| Restricting functionality        | Subclass removes or disables functionality promised by the parent.         | A read-only `RestrictedList` subclass of `ArrayList` that throws on `add()` |
| Method hiding                    | Subclass implementation obscures or contradicts parent behavior.           | A `Logger` subclass that silently drops specific log entries |
| Contravariant method arguments   | Subclass method requires more specific arguments than the parent.         | A `DataProcessor` subclass that only accepts certain data formats when the parent accepts all |
| Covariant return types misuse    | Subclass returns a type that can't be processed as the parent's return type. | An API client returning a subclass with additional required setup steps |

---

## 🔍 How to Identify LSP Violations

1. **Type Checking**: If client code needs to check object types using `instanceof` (Java), `isinstance` (Python), or similar, it's likely dealing with LSP violations

2. **Null or Empty Implementations**: Methods that throw exceptions like `UnsupportedOperationException` or do nothing when they should do something

3. **Commented-out Code**: Methods with comments like "not applicable for this subclass"

4. **Inconsistent Documentation**: Subclass documentation that contradicts parent class documentation

5. **Method Overrides That Reduce Functionality**: Methods that do less than their parent methods

6. **"Is-a" Relationship Doubts**: If you're unsure whether the subclass truly "is-a" base class

7. **Client Code Exceptions**: Runtime errors in client code when using subclasses polymorphically

### Example of Detection:

```java
// Client code needs to check types before use
public void processShape(Shape shape) {
    if (shape instanceof Circle) {
        // Special case for circles
        Circle circle = (Circle) shape;
        // ...
    } else if (shape instanceof Square) {
        // Special case for squares
        Square square = (Square) shape;
        // ...
    } else {
        // Default case
        // ...
    }
}
```

This code suggests an LSP violation because it needs to handle different shape types differently. A better design would have polymorphic behavior that works correctly for all subclasses without checking types.

---

## ✅ Best Practices for LSP Compliance

- Prefer **composition over inheritance** when behavior varies significantly
- Use **interfaces/abstract base classes** to enforce contracts
- Subclasses should follow the **principle of least astonishment**
- Don't override a method just to make it do something completely different
- Consider **behavioral subtyping** in your design (subclass preserves behavior)
- Document contract expectations explicitly in your interfaces
- Write **tests at the base class level** that verify contract compliance
- **Use assertion checking** in parent class methods to protect invariants
- Consider **design patterns** like Strategy or Decorator instead of inheritance
- When inheriting, think about **whether every instance of subclass truly "is-a" instance of parent class**

---

## 💻 Before & After Code Examples

### 🛑 Before: LSP Violation

```python
class Bird:
    def fly(self):
        print("Flies in the sky")

class Ostrich(Bird):
    def fly(self):
        raise Exception("Ostriches can't fly!")  # Violates LSP

# Client code that would break:
def make_bird_fly(bird: Bird):
    bird.fly()  # This will crash for Ostrich!
    
birds = [Bird(), Ostrich()]
for bird in birds:
    make_bird_fly(bird)  # 💥 Exception for Ostrich
```

> Although `Ostrich` is a subclass of `Bird`, it **violates LSP** because it breaks the expectation that all birds can fly.

---

### ✅ After: LSP-Compliant Design

```python
from abc import ABC, abstractmethod

class Bird(ABC):
    @abstractmethod
    def move(self):
        pass

class FlyingBird(Bird):
    def move(self):
        print("Flies in the sky")
        
    def fly(self):
        print("Flies in the sky")
        
class Sparrow(FlyingBird):
    pass

class Ostrich(Bird):
    def move(self):
        print("Runs on the ground")
        
# Client code works with all subtypes:
def make_bird_move(bird: Bird):
    bird.move()  # Works for any Bird subtype
    
birds = [Sparrow(), Ostrich()]
for bird in birds:
    make_bird_move(bird)  # ✅ Works consistently
```

> Now both `Sparrow` and `Ostrich` follow the **same interface** without violating expectations. `Bird` promises only that the animal can "move", not "fly".

---

### 🛑 Before: LSP Violation in File Access

```java
class FileProcessor {
    public void processFile(File file) {
        if (!file.canWrite()) {
            throw new IllegalArgumentException("File must be writable");
        }
        // Process and modify the file...
        writeToFile(file, "Processed content");
    }
    
    private void writeToFile(File file, String content) {
        // Write implementation
    }
}

// This violates LSP because it changes behavior unexpectedly
class ReadOnlyFileProcessor extends FileProcessor {
    @Override
    public void processFile(File file) {
        // Skip write check and never actually write
        System.out.println("Processing file: " + file.getName());
    }
}
```

---

### ✅ After: LSP-Compliant Design with Composition

```java
interface FileProcessor {
    void processFile(File file);
}

class WritableFileProcessor implements FileProcessor {
    public void processFile(File file) {
        if (!file.canWrite()) {
            throw new IllegalArgumentException("File must be writable");
        }
        // Process and modify the file...
        writeToFile(file, "Processed content");
    }
    
    private void writeToFile(File file, String content) {
        // Write implementation
    }
}

class ReadOnlyFileProcessor implements FileProcessor {
    public void processFile(File file) {
        // Only read the file, never write
        System.out.println("Processing file: " + file.getName());
    }
}
```

> Using composition with interfaces instead of inheritance provides the right behavior without violating LSP. Each processor fulfills the contract it establishes.

---

## 📊 The Square-Rectangle Problem

A classic LSP violation example is the Square-Rectangle problem:

```java
class Rectangle {
    protected int width;
    protected int height;
    
    public Rectangle(int width, int height) {
        this.width = width;
        this.height = height;
    }
    
    public void setWidth(int width) {
        this.width = width;
    }
    
    public void setHeight(int height) {
        this.height = height;
    }
    
    public int getArea() {
        return width * height;
    }
}

class Square extends Rectangle {  // LSP Violation
    public Square(int side) {
        super(side, side);
    }
    
    @Override
    public void setWidth(int width) {
        super.setWidth(width);
        super.setHeight(width);  // Changing width also changes height!
    }
    
    @Override
    public void setHeight(int height) {
        super.setHeight(height);
        super.setWidth(height);  // Changing height also changes width!
    }
}

// Client code that breaks with Square
void clientCode(Rectangle rectangle) {
    rectangle.setWidth(5);
    rectangle.setHeight(4);
    assert rectangle.getArea() == 20;  // Fails for Square where area would be 16
}
```

This violates LSP because client code expecting to work with a `Rectangle` would be surprised by a `Square`'s behavior when setting only width or height.

### LSP-Compliant Solution:

```java
interface Shape {
    int getArea();
}

class Rectangle implements Shape {
    private int width;
    private int height;
    
    public Rectangle(int width, int height) {
        this.width = width;
        this.height = height;
    }
    
    public void setWidth(int width) {
        this.width = width;
    }
    
    public void setHeight(int height) {
        this.height = height;
    }
    
    @Override
    public int getArea() {
        return width * height;
    }
}

class Square implements Shape {
    private int side;
    
    public Square(int side) {
        this.side = side;
    }
    
    public void setSide(int side) {
        this.side = side;
    }
    
    @Override
    public int getArea() {
        return side * side;
    }
}

// Client code now must be explicit about shape type
void clientCode(Shape shape) {
    // Only uses common behavior
    int area = shape.getArea();
    // ...
}
```

In the LSP-compliant solution, there's no inheritance relationship between `Rectangle` and `Square`. Instead, both implement a common interface, and client code doesn't make assumptions about behavior that differs between them.

---

## 🚨 Practical Examples of LSP Violations

### 1. Collections Framework Violations

```java
// Example from Java's Collections Framework (fixed in later versions)
public class Stack<E> extends Vector<E> {
    // add() methods inherited from Vector allowed direct insertion
    // at any position, violating Stack's LIFO invariant
    
    public E push(E item) {
        addElement(item);
        return item;
    }
    
    public E pop() {
        // ...
    }
}
```

The early Java `Stack` class extended `Vector`, but a stack has a stricter "last-in, first-out" contract that `Vector` methods like `add(int index, E element)` could violate.

### 2. Exception Hierarchy Misuse

```java
try {
    // Code that might throw various exceptions
    doSomethingRisky();
} catch (Exception e) {
    // Generic handling for all exceptions
    logger.error("An error occurred", e);
    showUserFriendlyMessage();
}
```

When subclasses of `Exception` introduce critical errors that should NOT be caught by generic exception handlers, they violate LSP. This is why Java distinguishes between checked and unchecked exceptions.

### 3. UI Components

```java
class Button {
    public void setEnabled(boolean enabled) {
        // Enable or disable the button
    }
    
    public void click() {
        if (!isEnabled()) {
            throw new IllegalStateException("Cannot click disabled button");
        }
        // Perform click action
    }
}

class ToggleButton extends Button {
    private boolean toggled = false;
    
    @Override
    public void click() {
        if (!isEnabled()) {
            throw new IllegalStateException("Cannot click disabled button");
        }
        toggled = !toggled;
        // Different behavior than Button
    }
}
```

If client code expects all `Button` clicks to perform an action, but `ToggleButton` sometimes just toggles state without performing the action, it might violate LSP.

---

## 🔍 Real-World Analogies

### Universal Remote Analogy

Imagine you have a universal TV remote control. When you press the "Volume Up" button, you expect the volume to increase, regardless of the TV brand. This is like LSP - any TV that works with this remote should respond to its buttons in the expected way.

If you buy a new "SmartTV" that claims to work with your remote, but pressing "Volume Up" actually changes the channel instead, that's an LSP violation. The new TV doesn't follow the "contract" of how TVs should respond to remote controls.

### Vehicle Rental Analogy

When you rent a car, you expect it to have standard controls: steering wheel, brake pedal, gas pedal, turn signals, etc. This creates a "contract" for how cars should behave.

If you were given a motorcycle instead (which technically is still a "vehicle"), you couldn't operate it as expected - it violates the substitution principle. Even though a motorcycle is a type of vehicle, it's not substitutable for a car without breaking the expectations of the car driver.

If you were given an electric car instead of a gasoline car, this would generally satisfy LSP as long as all the important behaviors (steering, accelerating, braking) work as expected, even if the underlying mechanism is different.

---

## 🧪 Testability Benefits

- LSP-compliant code is **predictable** and **modular**
- Makes it easier to **mock and test subclasses**
- Reduces risk of **polymorphic bugs** in production
- Enables **behavior-based testing** rather than implementation-based testing
- Allows for **better test reuse** between parent classes and subclasses
- Simplifies **parameterized testing** across different implementations

### Testing for LSP Compliance:

```java
// Base class test suite that can be reused for all subclasses
public abstract class SortAlgorithmTest {
    
    protected abstract SortAlgorithm createAlgorithm();
    
    @Test
    public void sortsEmptyArray() {
        SortAlgorithm algorithm = createAlgorithm();
        int[] empty = {};
        algorithm.sort(empty);
        assertArrayEquals(empty, new int[]{});
    }
    
    @Test
    public void sortsSingleElementArray() {
        SortAlgorithm algorithm = createAlgorithm();
        int[] array = {1};
        algorithm.sort(array);
        assertArrayEquals(array, new int[]{1});
    }
    
    @Test
    public void sortsMultipleElements() {
        SortAlgorithm algorithm = createAlgorithm();
        int[] array = {3, 1, 4, 1, 5, 9};
        algorithm.sort(array);
        assertArrayEquals(array, new int[]{1, 1, 3, 4, 5, 9});
    }
    
    // More tests for edge cases...
}

// Each implementation just needs to extend the base test
public class QuickSortTest extends SortAlgorithmTest {
    @Override
    protected SortAlgorithm createAlgorithm() {
        return new QuickSort();
    }
}

public class MergeSortTest extends SortAlgorithmTest {
    @Override
    protected SortAlgorithm createAlgorithm() {
        return new MergeSort();
    }
}
```

This pattern ensures that all sorting algorithms pass the same behavioral tests, confirming LSP compliance.

---

## 📈 Benefits of LSP

Adhering to the Liskov Substitution Principle delivers multiple significant benefits:

✅ **Reliable Polymorphism**: Enables code to work correctly with objects through their base class references

✅ **Modular Design**: Creates cleaner, more modular systems with proper abstraction boundaries

✅ **Improved Reusability**: Correctly designed subclasses can be used wherever base classes are expected

✅ **Reduced Debugging**: Fewer unexpected behaviors when substituting objects

✅ **Better Testability**: Base class tests can verify behavior for all subclasses

✅ **Increased Maintainability**: Changes in implementation don't break expected behavior

✅ **Clearer Abstractions**: Forces clearer thinking about what behaviors truly belong together

✅ **API Stability**: Clients can rely on consistent behavior even as implementations change

---

## ⚠️ When LSP Is Misunderstood

- Developers might rely on inheritance **without validating behavioral substitutability**
- Inheritance is **not always the best tool** — often, **composition is better** when behavior varies
- Over-generalizing classes can lead to **forced inheritance relationships** that don't make semantic sense
- Using **type checking** (`instanceof`, `type()`) often indicates LSP violations
- Sometimes developers think "historical compatibility" is the only requirement, ignoring behavioral compatibility
- A common misconception is that LSP only applies to method signatures, not to behavior

### Common Refactoring Patterns for LSP Violations:

1. **Extract Interface/Base Class**: Create a more abstract base with only common behavior

2. **Composition Over Inheritance**: Replace inheritance with composition where appropriate

3. **Template Method Pattern**: Define the algorithm skeleton in a base class and let subclasses override specific steps

4. **Strategy Pattern**: Extract varying behavior into separate strategy classes

5. **State Pattern**: When behavior varies based on object state, use state objects instead of inheritance

---

## 🔄 Relationship to Other SOLID Principles

| Principle | Relationship to LSP |
|-----------|---------------------|
| **Single Responsibility (SRP)** | Classes with clear responsibilities are easier to extend while maintaining LSP |
| **Open/Closed (OCP)** | LSP enables extension without modification by ensuring subclasses work correctly |
| **Interface Segregation (ISP)** | Smaller interfaces make it easier to follow LSP since there's less to conform to |
| **Dependency Inversion (DIP)** | Depending on abstractions rather than concretions relies on LSP for correct behavior |

### How They Work Together:

```java
// SRP: Each class has a single responsibility
// ISP: Interfaces are segregated by functionality
interface Payable {
    void pay(double amount);
}

interface Reportable {
    Report generateReport();
}

// OCP/LSP: System is open for extension, behaviors are substitutable
class Invoice implements Payable, Reportable {
    // Implementation
}

class Salary implements Payable, Reportable {
    // Implementation
}

// DIP: High-level code depends on abstractions
class PaymentProcessor {
    public void processPayments(List<Payable> payables) {
        for (Payable item : payables) {
            item.pay(calculateAmount(item));
        }
    }
    
    // ...
}
```

In this example, all SOLID principles work together: SRP keeps classes focused, ISP provides focused interfaces, LSP ensures substitutability, OCP allows for extension without modification, and DIP makes it all work together through abstractions.

---

## 🧠 Design Patterns that Support LSP

| Pattern | How It Supports LSP |
|---------|---------------------|
| **Template Method** | Defines a skeleton algorithm with hooks for variation, ensuring core behavior remains consistent |
| **Strategy** | Encapsulates varying behavior in interchangeable strategies, removing need for LSP-violating inheritance |
| **Decorator** | Extends functionality without subclassing, avoiding inheritance problems |
| **Adapter** | Makes incompatible interfaces compatible without inheritance |
| **Composite** | Treats individual objects and compositions uniformly, maintaining substitutability |
| **Bridge** | Separates abstraction from implementation, allowing both to vary independently |
| **Command** | Encapsulates requests as objects, making them substitutable |

### Strategy Pattern Example:

```typescript
// Instead of problematic inheritance, use Strategy pattern
interface SortStrategy {
    sort(data: number[]): number[];
}

class QuickSort implements SortStrategy {
    sort(data: number[]): number[] {
        console.log("Sorting using QuickSort");
        // Implementation
        return [...data].sort((a, b) => a - b);
    }
}

class MergeSort implements SortStrategy {
    sort(data: number[]): number[] {
        console.log("Sorting using MergeSort");
        // Implementation
        return [...data].sort((a, b) => a - b);
    }
}

class Sorter {
    private strategy: SortStrategy;
    
    constructor(strategy: SortStrategy) {
        this.strategy = strategy;
    }
    
    setStrategy(strategy: SortStrategy): void {
        this.strategy = strategy;
    }
    
    sort(data: number[]): number[] {
        return this.strategy.sort(data);
    }
}

// Usage
const sorter = new Sorter(new QuickSort());
const sorted = sorter.sort([3, 1, 4, 1, 5, 9]);

// Change strategy at runtime
sorter.setStrategy(new MergeSort());
const alsoSorted = sorter.sort([3, 1, 4, 1, 5, 9]);
```

This pattern allows behavior to vary without violating LSP, since we're using composition rather than inheritance.

---

## 📚 Further Reading

- **Original Papers**
  - [Barbara Liskov's original paper: "Data Abstraction and Hierarchy" (PDF)](https://dl.acm.org/doi/pdf/10.1145/62139.62141)
  - [Behavioral Subtyping Using Invariants and Constraints](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf)

- **Books**
  - [Clean Architecture by Robert C. Martin](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164)
  - [Effective Java by Joshua Bloch](https://www.amazon.com/Effective-Java-Joshua-Bloch/dp/0134685997)
  - [Design Patterns: Elements of Reusable Object-Oriented Software](https://www.amazon.com/Design-Patterns-Elements-Reusable-Object-Oriented/dp/0201633612)

- **Online Resources**
  - [Refactoring Guru – Liskov Substitution Principle](https://refactoring.guru/design-patterns/liskov-substitution-principle)
  - [Martin Fowler on Liskov Substitution Principle](https://martinfowler.com/bliki/LiskovSubstitutionPrinciple.html)
  - [Uncle Bob on LSP](https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html)
  - [Design by Contract by Bertrand Meyer](https://en.wikipedia.org/wiki/Design_by_contract)

- **Videos**
  - [SOLID Design Principles Explained - The Liskov Substitution Principle](https://www.youtube.com/watch?v=dJQMqNOC4Pc)
  - [Liskov Substitution Principle in Practice](https://www.youtube.com/watch?v=ObHQHszbIcE)
  - [SOLID Architecture in Python](https://www.youtube.com/watch?v=Qjywrq2gM8o)

---

## 📝 Summary

> 🔑 **Key Takeaways:**
> 
> - Subclasses should be **completely substitutable** for their base classes
> - Inheritance should model true **"is-a"** relationships
> - When behavior differs significantly, prefer **composition over inheritance**
> - LSP violations often appear as **type checking** or **conditional logic** based on object type
> - **Contract violations** in subclasses lead to **unexpected behavior** in client code
> - **Test suite inheritance** can help verify LSP compliance

The Liskov Substitution Principle is fundamentally about ensuring that inheritance hierarchies are designed correctly, maintaining consistent behavior so that client code can rely on the contract established by the base class or interface.
