"""
l_example.py

🔍 Example demonstrating the Liskov Substitution Principle (LSP)

The Liskov Substitution Principle states:
> "Objects of a superclass should be replaceable with objects of its subclasses without altering the correctness of the program."

In other words, derived classes must be substitutable for their base classes.
"""

# --- ❌ LSP Violation Example ---

class Bird:
    def fly(self):
        print("Flying in the sky!")

class Ostrich(Bird):
    def fly(self):
        raise NotImplementedError("Ostriches can't fly!")

def make_bird_fly(bird: Bird):
    bird.fly()

# Problem:
# - `Ostrich` inherits from `Bird`, but violates expected behavior.
# - Client code assumes all birds can fly — `Ostrich` breaks that assumption.
# - Violates LSP because it changes expected behavior of the base class.

# --- ✅ LSP-Compliant Refactored Version ---

from abc import ABC, abstractmethod

class BirdLSP(ABC):
    """Base class that separates flight-capable from non-flight-capable birds."""
    @abstractmethod
    def move(self):
        pass

class FlyingBird(BirdLSP):
    def move(self):
        print("Flying high!")

class NonFlyingBird(BirdLSP):
    def move(self):
        print("Walking on land.")

class Eagle(FlyingBird):
    def move(self):
        print("Eagle soars through the skies.")

class Penguin(NonFlyingBird):
    def move(self):
        print("Penguin waddles adorably.")

class Ostrich(NonFlyingBird):
    def move(self):
        print("Ostrich sprints across the savanna.")

# Now all subclasses fulfill the contract of `BirdLSP`
# and behave consistently with client expectations.

# --- ✅ Test Scenario ---

def make_bird_move(bird: BirdLSP):
    bird.move()

def main():
    birds = [
        Eagle(),
        Penguin(),
        Ostrich()
    ]
    for bird in birds:
        make_bird_move(bird)

if __name__ == "__main__":
    main()
