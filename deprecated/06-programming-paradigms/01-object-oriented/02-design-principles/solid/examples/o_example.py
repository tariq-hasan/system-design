"""
o_example.py

🔍 Example demonstrating the Open/Closed Principle (OCP)

The Open/Closed Principle states:
> "Software entities (classes, modules, functions, etc.) should be open for extension, but closed for modification."

This means we should be able to add new functionality without changing existing code.
"""

# --- ❌ OCP Violation Example ---

class Invoice:
    def __init__(self, amount):
        self.amount = amount

class InvoicePrinter:
    def print_invoice(self, invoice: Invoice, format: str):
        if format == "PDF":
            print(f"Printing PDF Invoice: ${invoice.amount}")
        elif format == "HTML":
            print(f"<html><body><h1>Invoice: ${invoice.amount}</h1></body></html>")
        else:
            raise ValueError("Unsupported format")

# Problem:
# - Every time a new format is added (e.g., CSV, XML), `InvoicePrinter` must be modified.
# - Violates OCP: The class is not closed to modification.

# --- ✅ OCP-Compliant Refactored Version ---

from abc import ABC, abstractmethod

class InvoiceFormatter(ABC):
    """Abstract base class for formatting invoices."""
    @abstractmethod
    def format(self, invoice: Invoice) -> str:
        pass

class PDFInvoiceFormatter(InvoiceFormatter):
    def format(self, invoice: Invoice) -> str:
        return f"Printing PDF Invoice: ${invoice.amount}"

class HTMLInvoiceFormatter(InvoiceFormatter):
    def format(self, invoice: Invoice) -> str:
        return f"<html><body><h1>Invoice: ${invoice.amount}</h1></body></html>"

class CSVInvoiceFormatter(InvoiceFormatter):
    def format(self, invoice: Invoice) -> str:
        return f"amount\n{invoice.amount}"

class InvoicePrinterOCP:
    """Open/Closed version: accepts any formatter that implements InvoiceFormatter."""
    def print_invoice(self, invoice: Invoice, formatter: InvoiceFormatter):
        output = formatter.format(invoice)
        print(output)

# --- ✅ Test Scenario ---

def main():
    invoice = Invoice(199.99)

    printer = InvoicePrinterOCP()

    # Print in different formats without modifying the printer logic
    printer.print_invoice(invoice, PDFInvoiceFormatter())
    printer.print_invoice(invoice, HTMLInvoiceFormatter())
    printer.print_invoice(invoice, CSVInvoiceFormatter())  # Easily added

if __name__ == "__main__":
    main()
