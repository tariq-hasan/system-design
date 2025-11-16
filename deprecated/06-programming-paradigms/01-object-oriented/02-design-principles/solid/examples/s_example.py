"""
s_example.py

🔍 Example demonstrating the Single Responsibility Principle (SRP)

The Single Responsibility Principle states:
> "A class should have one, and only one, reason to change."

This means that a class should only have one job or responsibility.
"""

# --- ❌ SRP Violation Example ---

class Report:
    def __init__(self, title, content):
        self.title = title
        self.content = content

    def format_report(self):
        # formatting responsibility
        return f"*** {self.title} ***\n\n{self.content}"

    def save_to_file(self, filename):
        # file I/O responsibility
        with open(filename, "w") as f:
            f.write(self.format_report())
        print(f"Saved report to {filename}")

# Problem:
# - The `Report` class is doing too much:
#     ➤ Storing data
#     ➤ Formatting content
#     ➤ Handling file output
# - Violates SRP: Changes in formatting or saving would require changes in the same class.

# --- ✅ SRP-Compliant Refactored Version ---

class ReportData:
    """Responsible only for storing report data."""
    def __init__(self, title, content):
        self.title = title
        self.content = content


class ReportFormatter:
    """Responsible only for formatting the report."""
    def format(self, report_data: ReportData):
        return f"=== {report_data.title} ===\n\n{report_data.content}"


class ReportSaver:
    """Responsible only for saving the report to a file."""
    def save(self, formatted_report: str, filename: str):
        with open(filename, "w") as f:
            f.write(formatted_report)
        print(f"Saved formatted report to {filename}")


# --- ✅ Test Scenario ---

def main():
    # Step 1: Create report data
    report = ReportData("Monthly Sales", "Sales increased by 20% in March.")

    # Step 2: Format the report
    formatter = ReportFormatter()
    formatted_report = formatter.format(report)

    # Step 3: Save the formatted report
    saver = ReportSaver()
    saver.save(formatted_report, "march_report.txt")


if __name__ == "__main__":
    main()
