"""
i_example.py

🔍 Example demonstrating the Interface Segregation Principle (ISP)

The Interface Segregation Principle states:
> "Clients should not be forced to depend on interfaces they do not use."

This means you should split large interfaces into smaller, more specific ones
so that implementing classes only need to concern themselves with the methods relevant to them.
"""

# --- ❌ ISP Violation Example ---

class Worker:
    def work(self):
        raise NotImplementedError()

    def eat(self):
        raise NotImplementedError()

    def sleep(self):
        raise NotImplementedError()

class HumanWorker(Worker):
    def work(self):
        print("Human is working.")

    def eat(self):
        print("Human is eating lunch.")

    def sleep(self):
        print("Human is sleeping.")

class RobotWorker(Worker):
    def work(self):
        print("Robot is working continuously.")

    def eat(self):
        # Robots don't eat!
        raise NotImplementedError("Robots do not eat.")

    def sleep(self):
        # Robots don't sleep!
        raise NotImplementedError("Robots do not sleep.")

# Problem:
# - `RobotWorker` is forced to implement irrelevant methods (`eat`, `sleep`)
# - Violates ISP because it depends on methods it does not use

# --- ✅ ISP-Compliant Refactored Version ---

from abc import ABC, abstractmethod

# Small, focused interfaces

class Workable(ABC):
    @abstractmethod
    def work(self):
        pass

class Eatable(ABC):
    @abstractmethod
    def eat(self):
        pass

class Sleepable(ABC):
    @abstractmethod
    def sleep(self):
        pass

# Only implement what's needed

class ISP_HumanWorker(Workable, Eatable, Sleepable):
    def work(self):
        print("Human is working.")

    def eat(self):
        print("Human is eating lunch.")

    def sleep(self):
        print("Human is sleeping.")

class ISP_RobotWorker(Workable):
    def work(self):
        print("Robot is working 24/7 without rest.")

# --- ✅ Test Scenario ---

def main():
    print("=== Human Worker ===")
    human = ISP_HumanWorker()
    human.work()
    human.eat()
    human.sleep()

    print("\n=== Robot Worker ===")
    robot = ISP_RobotWorker()
    robot.work()

    # The robot is not required to implement irrelevant methods like eat or sleep

if __name__ == "__main__":
    main()
