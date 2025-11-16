# 🧱 SOLID Principles in Object-Oriented Design
> A well-crafted system starts with well-crafted principles.

SOLID is an acronym for five key design principles that help software developers design maintainable, scalable, and robust systems, especially within object-oriented programming (OOP).

These principles were introduced by Robert C. Martin (Uncle Bob) and have become foundational in clean code and agile software development.

---

## 📘 What are the SOLID Principles?
| Principle                          | Summary                                                                 | Link                                                                 |
|-----------------------------------|-------------------------------------------------------------------------|----------------------------------------------------------------------|
| **S** – Single Responsibility     | A class should have only one reason to change.                         | [Read More →](./S.md)                                                |
| **O** – Open/Closed               | Software entities should be open for extension but closed for modification. | [Read More →](./O.md)                                                |
| **L** – Liskov Substitution       | Subtypes must be substitutable for their base types without altering correctness. | [Read More →](./L.md)                                                |
| **I** – Interface Segregation     | No client should be forced to depend on interfaces it does not use.    | [Read More →](./I.md)                                                |
| **D** – Dependency Inversion      | Depend on abstractions, not concretions.                              | [Read More →](./D.md)                                                |

---

## 🎯 Why Use SOLID?
Applying the SOLID principles leads to:
- **Easier refactoring**
- **Better testability**
- **More flexible code**
- **Reduced coupling**
- **Improved readability and maintainability**

They are especially useful in larger systems and teams where the cost of change is high.

---

## 📋 Prerequisites
These notes assume:
- Basic understanding of object-oriented programming concepts
- Familiarity with Python (the language used in examples)
- Some experience with software design challenges

---

## 📂 Repository Structure

```
solid-principles/
├── README.md              # This file
├── S.md                   # Single Responsibility Principle
├── O.md                   # Open/Closed Principle
├── L.md                   # Liskov Substitution Principle
├── I.md                   # Interface Segregation Principle
├── D.md                   # Dependency Inversion Principle
├── cheatsheet.md          # Quick summary of all principles
├── resources.md           # Further reading and learning materials
└── examples/              # Code examples
    ├── s_example.py
    ├── o_example.py
    ├── l_example.py
    ├── i_example.py
    └── d_example.py
```

---

## 🧭 How to Navigate This Repository
- Start with this README for an overview
- Each principle has its own dedicated markdown file (S.md, O.md, etc.)
- Code examples are in the `/examples` directory with corresponding file names
- For quick revision, refer to the cheatsheet.md
- For further learning, check resources.md

---

## 🧠 How to Study These Principles
Each Markdown file includes:
- 📖 Definition
- 🧵 Key ideas and motivations
- ❌ Common violations
- ✅ Best practices
- 💻 Code examples
- 🔍 Real-world analogies
- 📚 Additional resources

---

## 🛠 Recommended Reading
You can find more resources in [resources.md](./resources.md), but here are some great starting points:
- **Clean Code** by Robert C. Martin
- **Agile Software Development, Principles, Patterns, and Practices**
- SOLID explanations on [Refactoring Guru](https://refactoring.guru)
- [Uncle Bob's original talks](https://www.youtube.com/watch?v=TMuno5RZNeE)

---

## 📌 Quick Reference (One-Liners)
> For a fast refresh or interview prep, check out the [cheatsheet.md](./cheatsheet.md)

---

## 🔗 Contributions & Feedback
These notes are a personal learning resource, but improvements, corrections, or additions are welcome.
Feel free to fork, clone, or open an issue/PR. 💬

---

*"The only way to go fast is to go well." – Robert C. Martin*
