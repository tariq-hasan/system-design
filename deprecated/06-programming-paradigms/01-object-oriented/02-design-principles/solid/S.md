# 🧱 Single Responsibility Principle (SRP)

> "A class should have only one reason to change."  
> — Robert C. Martin (Uncle Bob)

---

## 📖 Definition

The **Single Responsibility Principle** (SRP) states that a class, module, or function should have **only one responsibility** — in other words, **only one reason to change**.

In essence:
- Each unit of code should focus on **one thing only**.
- A "responsibility" is defined as a **reason for change**, often connected to a specific stakeholder or business concern.
- SRP applies at multiple levels: methods, classes, modules, and even services.

---

## 🧵 Key Concepts

- SRP is about **cohesion** — keeping related behavior in the same place and unrelated behavior elsewhere.
- Responsibilities can come from **business rules**, **UI needs**, **data persistence**, **logging**, **security**, etc.
- Violating SRP often leads to **tight coupling**, **low reusability**, and **hard-to-test** code.
- SRP is the foundation for many other design patterns and architectural principles.
- A "stakeholder" is anyone who requires a change in the system (business users, administrators, regulators, etc.)

---

## ❌ Common Violations

Here are some examples where SRP is violated:

| Violation Type         | Example                                               | Problems Caused                                       |
|------------------------|-------------------------------------------------------|-------------------------------------------------------|
| Mixed concerns         | A class that handles both data storage and business logic | Changes to database structure affect business rules |
| UI + Business Logic    | A view/controller that makes network calls and renders UI | UI changes require modifying business logic      |
| Logging + Core Logic   | A class that logs its actions while doing its main job | Changing log format affects core functionality     |
| Email + Formatting     | A class that sends emails and builds HTML templates    | Template changes require modifying sending logic   |
| God Classes            | Classes that try to do everything related to a business entity | Brittle code with high risk of regression bugs |
| Utility Classes        | Classes with unrelated utility methods grouped by convenience | Unpredictable growth and conflict in functionality |
| Data + Validation      | A class that both represents data and validates it     | Changes to validation rules affect data structure  |
| Authentication + Authorization | Mixing who you are with what you can do        | Security rule changes affect identity management   |

---

## 🔍 How to Identify SRP Violations

Look for these warning signs:

1. **Large classes** with many methods and properties
2. **Methods with side effects** that do more than their name suggests
3. **Classes that change frequently** for different reasons
4. **Low cohesion** between methods in the same class
5. **Comments explaining different sections** of a class or method
6. **Difficulty naming** a class or method concisely
7. **Multiple import categories** (UI, database, networking, etc.) in the same file
8. **Complex test setups** required to test a single feature

---

## ✅ Best Practices

- **Split responsibilities** across multiple smaller classes or functions
- Use **composition** to assemble behavior
- Apply **"separation of concerns"** as a guiding philosophy
- Keep methods short and focused — one task per method
- Name classes and methods to clearly reflect their single responsibility
- Create **cohesive** classes where methods are related to each other
- Use **dependency injection** to provide services that handle other responsibilities
- Analyze classes by **stakeholder** to identify potential splits
- Seek **balance** between excessive fragmentation and monolithic classes

---

## 💻 Before & After Code Examples

### 🛑 Before: SRP Violation

```python
class Invoice:
    def __init__(self, customer, items):
        self.customer = customer
        self.items = items

    def calculate_total(self):
        return sum(item.price for item in self.items)

    def save_to_database(self):
        # Database connection logic
        db = Database.connect("invoice_db")
        
        # SQL generation and execution
        sql = f"INSERT INTO invoices (customer, amount) VALUES ({self.customer.id}, {self.calculate_total()})"
        db.execute(sql)
        
        # Error handling
        db.close()

    def print_invoice(self):
        # Generate formatting
        output = f"INVOICE\n"
        output += f"Customer: {self.customer.name}\n"
        output += f"Amount: ${self.calculate_total()}\n"
        output += f"Items:\n"
        
        for item in self.items:
            output += f"  - {item.name}: ${item.price}\n"
            
        # Print handling
        printer = Printer.get_default_printer()
        printer.print_document(output)
```

> This class has **three reasons to change**:
> - Change in business logic (calculations)
> - Change in data storage (database operations)
> - Change in output formatting (printing)

---

### ✅ After: SRP-Compliant Design

```python
class Invoice:
    def __init__(self, customer, items):
        self.customer = customer
        self.items = items

    def calculate_total(self):
        return sum(item.price for item in self.items)
    
    def get_item_count(self):
        return len(self.items)


class InvoicePrinter:
    def print(self, invoice: Invoice):
        output = f"INVOICE\n"
        output += f"Customer: {invoice.customer.name}\n"
        output += f"Amount: ${invoice.calculate_total()}\n"
        output += f"Items:\n"
        
        for item in invoice.items:
            output += f"  - {item.name}: ${item.price}\n"
            
        printer = Printer.get_default_printer()
        printer.print_document(output)


class InvoiceRepository:
    def __init__(self, database_connection):
        self.db = database_connection
    
    def save(self, invoice: Invoice):
        try:
            sql = f"INSERT INTO invoices (customer_id, amount, item_count) VALUES (?, ?, ?)"
            self.db.execute(sql, [
                invoice.customer.id, 
                invoice.calculate_total(),
                invoice.get_item_count()
            ])
        except DatabaseError as e:
            # Handle database errors
            raise InvoiceSaveError(f"Failed to save invoice: {str(e)}")
```

> Now, each class has **one reason to change**:
> - `Invoice`: business logic and calculations
> - `InvoicePrinter`: formatting and printing concerns
> - `InvoiceRepository`: persistence and database operations

---

### 🛑 Before: SRP Violation in a Web Context

```javascript
class UserController {
    constructor() {
        this.database = new Database();
    }
    
    async createUser(req, res) {
        // Extract and validate user data
        const { username, email, password } = req.body;
        
        if (!username || !email || !password) {
            return res.status(400).json({ error: 'Missing required fields' });
        }
        
        if (!email.includes('@')) {
            return res.status(400).json({ error: 'Invalid email format' });
        }
        
        if (password.length < 8) {
            return res.status(400).json({ error: 'Password too short' });
        }
        
        // Hash password
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);
        
        // Save to database
        try {
            const sql = `INSERT INTO users (username, email, password) 
                         VALUES ('${username}', '${email}', '${hashedPassword}')`;
            await this.database.execute(sql);
            
            // Send welcome email
            const emailContent = `Welcome to our platform, ${username}!`;
            const emailService = new EmailService();
            await emailService.sendEmail(email, 'Welcome!', emailContent);
            
            // Generate JWT token
            const token = jwt.sign({ username }, 'secret_key', { expiresIn: '1h' });
            
            // Return response
            return res.status(201).json({ 
                message: 'User created successfully',
                token 
            });
        } catch (error) {
            console.error('User creation failed:', error);
            return res.status(500).json({ error: 'Internal server error' });
        }
    }
}
```

---

### ✅ After: SRP-Compliant Web Design

```javascript
// User model handles data structure and basic validations
class User {
    constructor(username, email, password) {
        this.username = username;
        this.email = email;
        this.password = password;
    }
    
    validate() {
        const errors = [];
        
        if (!this.username) errors.push('Username is required');
        if (!this.email) errors.push('Email is required');
        if (!this.email.includes('@')) errors.push('Invalid email format');
        if (!this.password) errors.push('Password is required');
        if (this.password && this.password.length < 8) errors.push('Password too short');
        
        return errors;
    }
}

// UserService handles business logic
class UserService {
    constructor(userRepository, emailService, tokenService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
        this.tokenService = tokenService;
    }
    
    async createUser(userData) {
        const user = new User(userData.username, userData.email, userData.password);
        const validationErrors = user.validate();
        
        if (validationErrors.length > 0) {
            throw new ValidationError(validationErrors);
        }
        
        const hashedPassword = await this.hashPassword(userData.password);
        user.password = hashedPassword;
        
        const savedUser = await this.userRepository.save(user);
        await this.emailService.sendWelcomeEmail(user.email, user.username);
        
        return {
            user: savedUser,
            token: this.tokenService.generateToken(user)
        };
    }
    
    async hashPassword(password) {
        const salt = await bcrypt.genSalt(10);
        return bcrypt.hash(password, salt);
    }
}

// UserRepository handles data persistence
class UserRepository {
    constructor(database) {
        this.database = database;
    }
    
    async save(user) {
        const query = 'INSERT INTO users (username, email, password) VALUES (?, ?, ?)';
        const params = [user.username, user.email, user.password];
        
        try {
            const result = await this.database.execute(query, params);
            user.id = result.insertId;
            return user;
        } catch (error) {
            throw new DatabaseError('Failed to save user', error);
        }
    }
}

// Controller only handles HTTP concerns
class UserController {
    constructor(userService) {
        this.userService = userService;
    }
    
    async createUser(req, res) {
        try {
            const result = await this.userService.createUser(req.body);
            
            return res.status(201).json({
                message: 'User created successfully',
                token: result.token
            });
        } catch (error) {
            if (error instanceof ValidationError) {
                return res.status(400).json({ errors: error.errors });
            }
            
            console.error('User creation failed:', error);
            return res.status(500).json({ error: 'Internal server error' });
        }
    }
}

// Usage with dependency injection
const setupUserRoutes = (app) => {
    const database = new Database();
    const userRepository = new UserRepository(database);
    const emailService = new EmailService();
    const tokenService = new TokenService('secret_key', '1h');
    
    const userService = new UserService(userRepository, emailService, tokenService);
    const userController = new UserController(userService);
    
    app.post('/users', userController.createUser.bind(userController));
};
```

Each class now has a single responsibility:
- `User`: Data structure and validation
- `UserService`: Business logic and orchestration
- `UserRepository`: Data persistence
- `UserController`: HTTP request/response handling

---

## 🔍 Real-World Analogies

### Restaurant Analogy
> A **chef** prepares food, a **waiter** serves it, and a **cashier** handles payment.

You wouldn't want the same person doing all three at once in a busy restaurant — not efficient, not scalable, and certainly not maintainable.

### Publication Analogy
In publishing a book:
- **Authors** write content (business logic)
- **Editors** review and refine it (validation)
- **Designers** format and layout the book (presentation)
- **Publishers** distribute it (delivery mechanism)

Each role has a distinct responsibility that would be compromised if combined.

### Manufacturing Analogy
An assembly line works because each station focuses on a specific task:
- One station attaches the wheels
- Another installs the engine
- A third adds the interior components

This specialization increases efficiency and quality compared to having one person build the entire car.

---

## 🧪 Testability Benefits

- Easier to **mock dependencies** (e.g., database or printer)
- **Unit tests** focus on a single piece of behavior
- Promotes **predictable and isolated** test cases
- Reduces setup complexity in tests
- Enables **parallel test development** by different team members
- Simplifies **test maintenance** when requirements change
- Improves **test coverage** by making edge cases easier to simulate
- Creates more **readable tests** that clearly express intent

### Example: Testing SRP-Compliant Code

```javascript
// Testing business logic in isolation
describe('Invoice', () => {
    it('calculates the correct total', () => {
        const customer = { id: 1, name: 'Test Customer' };
        const items = [
            { name: 'Item 1', price: 10 },
            { name: 'Item 2', price: 20 }
        ];
        
        const invoice = new Invoice(customer, items);
        
        expect(invoice.calculate_total()).toBe(30);
    });
});

// Testing persistence separately with mocks
describe('InvoiceRepository', () => {
    it('saves invoice to database', () => {
        // Mock database
        const mockDb = {
            execute: jest.fn().mockResolvedValue({ insertId: 1 })
        };
        
        const repository = new InvoiceRepository(mockDb);
        const invoice = {
            customer: { id: 1 },
            calculate_total: () => 30,
            get_item_count: () => 2
        };
        
        return repository.save(invoice)
            .then(() => {
                // Verify the correct SQL was executed with proper parameters
                expect(mockDb.execute).toHaveBeenCalledWith(
                    expect.any(String),
                    [1, 30, 2]
                );
            });
    });
});
```

---

## 📈 Benefits of SRP

The Single Responsibility Principle delivers numerous advantages to your codebase:

✅ **Improved Maintainability**: Changes are localized to specific components

✅ **Better Testability**: Clear boundaries make testing focused and simpler

✅ **Enhanced Reusability**: Components can be used in different contexts

✅ **Reduced Side Effects**: Changes in one area don't unexpectedly affect others

✅ **Easier Understanding**: Code is more focused and readable

✅ **Simplified Debugging**: Problems are isolated to specific components

✅ **Better Team Collaboration**: Different team members can work on different responsibilities

✅ **More Flexible Architecture**: Components can evolve independently

✅ **Natural Fit for Microservices**: Single-responsibility classes easily translate to microservices

---

## ⚠️ Implementation Challenges

- **Finding the right granularity**: Too fine-grained classes can lead to excessive complexity
- **Managing relationships**: When responsibilities are separated, you need to carefully design how components interact
- **Refactoring legacy code**: Applying SRP to existing monolithic classes requires careful extraction
- **Balancing cohesion and coupling**: Sometimes splitting responsibilities increases coupling
- **Overhead in small applications**: May introduce unnecessary complexity in very simple applications
- **Discovering true responsibilities**: It can be difficult to correctly identify separate concerns
- **Package structure**: Organizing growing numbers of smaller classes into meaningful packages

### Strategies for Overcoming Challenges

1. **Start with larger chunks**: Begin with broader responsibilities, then refine as needed
2. **Use packaging by feature**: Group related classes by feature instead of by layer
3. **Apply facade pattern**: Provide simple interfaces to complex subsystems
4. **Incremental refactoring**: Improve code gradually rather than all at once
5. **Follow domain boundaries**: Let your domain model guide class responsibilities
6. **Evaluate each split**: Consider if the benefit outweighs the added complexity

---

## 🤔 When SRP Is Misunderstood

- **Too many tiny classes**: Creating a separate class for every minor function
  - **Example**: Making `InvoiceItemPriceCalculator`, `InvoiceTaxCalculator`, and `InvoiceTotalCalculator` when they could all logically belong together

- **Artificial separations**: Dividing naturally cohesive functionality
  - **Example**: Separating a simple data validation method into its own class when it's tightly coupled with the data it validates

- **Confusing SRP with "one method per class"**: SRP is about responsibility, not method count
  - **Example**: Thinking that a class with 10 methods violates SRP, when all methods are related to the same responsibility

- **Overly abstract naming**: Creating vague class names that hide their actual purpose
  - **Example**: Creating a class called `Manager` or `Processor` without clear indication of what it manages or processes

---

## 🔄 SRP at Different Levels

SRP applies at multiple levels of your architecture:

### Method Level
Methods should do one thing and do it well:

```javascript
// Bad: Mixed responsibilities
function validateAndSaveUser(user) {
    // Validation logic
    if (!user.email.includes('@')) {
        throw new Error('Invalid email');
    }
    
    // Persistence logic
    database.save(user);
}

// Good: Separated responsibilities
function validateUser(user) {
    if (!user.email.includes('@')) {
        throw new Error('Invalid email');
    }
}

function saveUser(user) {
    database.save(user);
}
```

### Class Level
As we've seen in examples above.

### Module/Package Level
Groups of classes should also have a single cohesive purpose:

```
// Bad: Mixed module responsibilities
/auth/
  - UserController.js
  - PaymentProcessor.js
  - EmailSender.js

// Good: Module with single responsibility
/auth/
  - UserController.js
  - AuthService.js
  - UserRepository.js
```

### Service/Application Level
In microservices architecture, each service should have a clear, bounded responsibility:

- **Authentication Service**: Handles user identity
- **Payment Service**: Processes payments
- **Notification Service**: Sends notifications
- **Inventory Service**: Manages product inventory

---

## 🔄 Relationship to Other SOLID Principles

| Principle | Relationship to SRP |
|-----------|---------------------|
| **Open/Closed (OCP)** | SRP creates modular components that are easier to extend without modification |
| **Liskov Substitution (LSP)** | Classes with single responsibilities are easier to substitute without breaking behavior |
| **Interface Segregation (ISP)** | Both principles promote focused, cohesive units (classes vs interfaces) |
| **Dependency Inversion (DIP)** | Single-responsibility classes are more easily injected as dependencies |

---

## 🧠 Design Patterns that Support SRP

| Pattern | How It Supports SRP |
|---------|---------------------|
| **Decorator** | Adds responsibilities to objects without modifying them |
| **Strategy** | Encapsulates algorithms in their own classes |
| **Command** | Encapsulates requests as objects with single responsibilities |
| **Observer** | Separates the subject from objects interested in its state |
| **Factory** | Separates object creation from its use |
| **Repository** | Isolates data access logic |
| **Service Layer** | Separates business logic from controllers/views |
| **Facade** | Provides a unified interface to a set of interfaces |

---

## 📝 Practical Tips for Applying SRP

1. **Ask the "reason to change" question**: "What would cause this class to change?"
2. **Look for "and" in class descriptions**: If you use "and" to describe a class, it likely has multiple responsibilities
3. **Consider stakeholders**: Different stakeholders often indicate different responsibilities
4. **Pay attention to coupling**: High coupling may indicate mixed responsibilities
5. **Watch for large classes**: Size often correlates with multiple responsibilities
6. **Extract till you drop**: Keep extracting responsibilities until each class has just one
7. **Use meaningful naming**: Class names should clearly indicate their responsibility
8. **Follow the refactoring workflow**:
   - Identify responsibilities
   - Extract each to its own class
   - Create appropriate relationships between classes

---

## 📚 Further Reading

- **Books**
  - [Clean Code by Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)
  - [Practical Object-Oriented Design by Sandi Metz](https://www.amazon.com/Practical-Object-Oriented-Design-Ruby-Addison-Wesley/dp/0321721330)
  - [Refactoring by Martin Fowler](https://www.amazon.com/Refactoring-Improving-Existing-Addison-Wesley-Signature/dp/0134757599)

- **Articles**
  - [SRP: The Single Responsibility Principle](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) - Robert C. Martin
  - [SRP on Refactoring Guru](https://refactoring.guru/design-patterns/single-responsibility-principle)
  - [Single Responsibility Principle in Depth](https://stackify.com/solid-design-principles/) - Comprehensive explanation

- **Videos**
  - [SOLID Design Principles Explained: The Single Responsibility Principle](https://www.youtube.com/watch?v=UQqY3_6Epbg)
  - [Uncle Bob's talk on SRP](https://www.youtube.com/watch?v=Gt0M_OHKhQE)
  - [Clean Code: SOLID](https://www.youtube.com/watch?v=TMuno5RZNeE) - Comprehensive SOLID principles

- **Online Resources**
  - [Domain-Driven Design and SRP](https://dzone.com/articles/solid-principles-by-example-single-responsibility) - Applying SRP to domain modeling
  - [Refactoring to SRP](https://www.baeldung.com/java-single-responsibility-principle) - Step-by-step guide
  - [SRP in React Applications](https://medium.com/the-non-traditional-developer/single-responsibility-principle-in-react-applications-cf44824dc56c)

---

## 📝 Summary

> 🔑 **Key Takeaways:**
> 
> - A class or module should have **one reason to change**
> - SRP helps improve **maintainability**, **testability**, and **reusability**
> - Look for **cohesion** within classes and proper **separation of concerns**
> - Apply SRP at **different levels**: methods, classes, modules, and services
> - Balance SRP with **practical considerations** - don't overdo it
> - Use **composition** to assemble complex behavior from single-responsibility components
> - Remember: "**Do one thing, and do it well**" is the essence of SRP

When each class does one thing and does it well, your code becomes flexible, maintainable, and beautiful. SRP is not about creating the smallest possible classes, but about organizing your code around well-defined responsibilities that can evolve independently.
