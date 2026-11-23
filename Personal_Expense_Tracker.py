
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime

# Personal Expense Tracker
# COSC 4272 - Personal Project

DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "expenses.csv"
)


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")
        self.root.geometry("950x650")
        self.root.minsize(750, 550)
        self.root.configure(bg="#f4f7fb")

        self.records = []

        self.create_interface()
        self.load_records()
        self.update_summary()

    def create_interface(self):
        title = tk.Label(
            self.root,
            text="Personal Expense Tracker",
            font=("Arial", 24, "bold"),
            bg="#102a43",
            fg="white",
            pady=20
        )
        title.pack(fill="x")

        subtitle = tk.Label(
            self.root,
            text="Manage income, expenses, and your budget",
            font=("Arial", 11),
            bg="#f4f7fb",
            fg="#53657a",
            pady=10
        )
        subtitle.pack()

        summary = tk.Frame(self.root, bg="#f4f7fb")
        summary.pack(fill="x", padx=20, pady=10)

        self.income_label = tk.Label(
            summary,
            text="Total Income: $0.00",
            font=("Arial", 13, "bold"),
            fg="#16803c",
            bg="white",
            padx=15,
            pady=15
        )
        self.income_label.pack(
            side="left", expand=True, fill="x", padx=5
        )

        self.expense_label = tk.Label(
            summary,
            text="Total Expenses: $0.00",
            font=("Arial", 13, "bold"),
            fg="#c0392b",
            bg="white",
            padx=15,
            pady=15
        )
        self.expense_label.pack(
            side="left", expand=True, fill="x", padx=5
        )

        self.balance_label = tk.Label(
            summary,
            text="Balance: $0.00",
            font=("Arial", 13, "bold"),
            fg="#1261a0",
            bg="white",
            padx=15,
            pady=15
        )
        self.balance_label.pack(
            side="left", expand=True, fill="x", padx=5
        )

        form = tk.LabelFrame(
            self.root,
            text="Add New Transaction",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        form.pack(fill="x", padx=25, pady=10)

        tk.Label(
            form, text="Type:", bg="white"
        ).grid(row=0, column=0, sticky="w")

        self.type_var = tk.StringVar(value="Expense")

        self.type_box = ttk.Combobox(
            form,
            textvariable=self.type_var,
            values=["Income", "Expense"],
            state="readonly",
            width=15
        )
        self.type_box.grid(
            row=1, column=0, padx=5, pady=5
        )

        tk.Label(
            form, text="Category:", bg="white"
        ).grid(row=0, column=1, sticky="w")

        self.category_var = tk.StringVar()

        self.category_box = ttk.Combobox(
            form,
            textvariable=self.category_var,
            values=[
                "Salary",
                "Housing",
                "Food",
                "Transportation",
                "Utilities",
                "Education",
                "Entertainment",
                "Healthcare",
                "Savings",
                "Other"
            ],
            width=18
        )
        self.category_box.grid(
            row=1, column=1, padx=5, pady=5
        )

        tk.Label(
            form, text="Amount ($):", bg="white"
        ).grid(row=0, column=2, sticky="w")

        self.amount_entry = ttk.Entry(form, width=18)
        self.amount_entry.grid(
            row=1, column=2, padx=5, pady=5
        )

        tk.Label(
            form, text="Description:", bg="white"
        ).grid(row=0, column=3, sticky="w")

        self.description_entry = ttk.Entry(
            form, width=25
        )
        self.description_entry.grid(
            row=1, column=3, padx=5, pady=5
        )

        add_button = tk.Button(
            form,
            text="Add Transaction",
            command=self.add_transaction,
            bg="#1261a0",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=8
        )
        add_button.grid(
            row=1, column=4, padx=10, pady=5
        )

        table_frame = tk.Frame(
            self.root, bg="#f4f7fb"
        )
        table_frame.pack(
            fill="both", expand=True,
            padx=25, pady=10
        )

        columns = (
            "Date", "Type", "Category",
            "Amount", "Description"
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        for column in columns:
            self.table.heading(
                column, text=column
            )
            self.table.column(
                column, anchor="center", width=130
            )

        self.table.column(
            "Description", width=220
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )
        self.table.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right", fill="y"
        )
        self.table.pack(
            side="left", fill="both", expand=True
        )

        bottom = tk.Frame(
            self.root, bg="#f4f7fb"
        )
        bottom.pack(pady=15)

        delete_button = tk.Button(
            bottom,
            text="Delete Selected Transaction",
            command=self.delete_transaction,
            bg="#c0392b",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8
        )
        delete_button.pack(
            side="left", padx=10
        )

        save_button = tk.Button(
            bottom,
            text="Save Records",
            command=self.save_records,
            bg="#16803c",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8
        )
        save_button.pack(
            side="left", padx=10
        )

    def add_transaction(self):
        transaction_type = self.type_var.get()
        category = self.category_var.get().strip()
        amount_text = self.amount_entry.get().strip()
        description = self.description_entry.get().strip()

        if not category or not amount_text:
            messagebox.showwarning(
                "Missing Information",
                "Please enter a category and amount."
            )
            return

        try:
            amount = float(amount_text)
        except ValueError:
            messagebox.showerror(
                "Invalid Amount",
                "Please enter a valid number."
            )
            return

        if amount <= 0 or amount != amount or amount == float("inf"):
            messagebox.showerror(
                "Invalid Amount",
                "Amount must be a positive, finite number."
            )
            return

        date = datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )

        record = [
            date,
            transaction_type,
            category,
            f"{amount:.2f}",
            description
        ]

        self.records.append(record)

        self.table.insert(
            "", "end", values=record
        )

        self.update_summary()
        self.save_records(show_message=False)

        self.amount_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)

    def delete_transaction(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a transaction to delete."
            )
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            "Delete the selected transaction?"
        ):
            return

        item = selected[0]
        index = self.table.index(item)

        self.table.delete(item)
        del self.records[index]

        self.update_summary()
        self.save_records(show_message=False)

    def update_summary(self):
        income = 0.0
        expenses = 0.0

        for record in self.records:
            amount = float(record[3])

            if record[1] == "Income":
                income += amount
            elif record[1] == "Expense":
                expenses += amount

        balance = income - expenses

        self.income_label.config(
            text=f"Total Income: ${income:,.2f}"
        )
        self.expense_label.config(
            text=f"Total Expenses: ${expenses:,.2f}"
        )
        self.balance_label.config(
            text=f"Balance: ${balance:,.2f}"
        )

    def save_records(self, show_message=True):
        try:
            with open(
                DATA_FILE, "w", newline="",
                encoding="utf-8"
            ) as file:
                writer = csv.writer(file)
                writer.writerow([
                    "Date", "Type", "Category",
                    "Amount", "Description"
                ])
                writer.writerows(self.records)

            if show_message:
                messagebox.showinfo(
                    "Saved",
                    "Your records were saved successfully."
                )
        except OSError as error:
            messagebox.showerror(
                "Save Error",
                f"Unable to save records:\n{error}"
            )

    def load_records(self):
        if not os.path.exists(DATA_FILE):
            return

        try:
            with open(
                DATA_FILE, "r", newline="",
                encoding="utf-8"
            ) as file:
                reader = csv.reader(file)
                next(reader, None)

                for record in reader:
                    if len(record) != 5:
                        continue

                    try:
                        amount = float(record[3])
                    except ValueError:
                        continue

                    if (
                        record[1] not in ("Income", "Expense")
                        or not (0 < amount < float("inf"))
                    ):
                        continue

                    self.records.append(record)
                    self.table.insert(
                        "", "end", values=record
                    )

        except (OSError, csv.Error) as error:
            messagebox.showerror(
                "Load Error",
                f"Unable to load records:\n{error}"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
