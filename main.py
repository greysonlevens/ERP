import json
import os
import uuid
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

DATA_DIR = "erp_data"
os.makedirs(DATA_DIR, exist_ok=True)

# Utility functions
def load_data(file_name):
    path = os.path.join(DATA_DIR, file_name)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return []

def save_data(file_name, data):
    path = os.path.join(DATA_DIR, file_name)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# Placeholder function for deciphering the command using a local LLM.
def local_llm_decipher(command):
    command_lower = command.lower()
    if "customer" in command_lower:
        return {"action": "add_customer", "details": command}
    elif "vendor" in command_lower:
        return {"action": "add_vendor", "details": command}
    elif "product" in command_lower:
        return {"action": "add_product", "details": command}
    elif "order" in command_lower:
        return {"action": "add_order", "details": command}
    else:
        return {"action": "unknown", "details": command}

class NapkinERP:
    def __init__(self):
        self.customers = load_data("customers.json")
        self.products = load_data("products.json")
        self.vendors = load_data("vendors.json")
        self.orders = load_data("orders.json")

    def add_customer(self, name, email):
        customer_id = str(uuid.uuid4())
        customer = {"id": customer_id, "name": name, "email": email}
        self.customers.append(customer)
        save_data("customers.json", self.customers)

    def add_vendor(self, name, contact):
        vendor_id = str(uuid.uuid4())
        vendor = {"id": vendor_id, "name": name, "contact": contact}
        self.vendors.append(vendor)
        save_data("vendors.json", self.vendors)

    def add_product(self, name, vendor_id):
        product_id = str(uuid.uuid4())
        product = {"id": product_id, "name": name, "vendor_id": vendor_id}
        self.products.append(product)
        save_data("products.json", self.products)

    def add_order(self, customer_id, product_id):
        order_id = str(uuid.uuid4())
        order = {"id": order_id, "customer_id": customer_id, "product_id": product_id,
                 "timestamp": datetime.now().isoformat()}
        self.orders.append(order)
        save_data("orders.json", self.orders)

class ERPApp:
    def __init__(self, root):
        self.erp = NapkinERP()
        self.root = root
        root.title("Napkin ERP")

        self.build_customer_section()
        self.build_vendor_section()
        self.build_product_section()
        self.build_order_section()
        self.build_llm_section()  # New LLM command section added.
        self.refresh_lists()

    def build_customer_section(self):
        frame = tk.LabelFrame(self.root, text="Customers", padx=5, pady=5, bd=2)
        frame.pack(padx=10, pady=5, fill="x")

        tk.Label(frame, text="Name").pack()
        self.customer_name = tk.Entry(frame)
        self.customer_name.pack()

        tk.Label(frame, text="Email").pack()
        self.customer_email = tk.Entry(frame)
        self.customer_email.pack()

        tk.Button(frame, text="Add Customer", command=self.add_customer).pack()

    def build_vendor_section(self):
        frame = tk.LabelFrame(self.root, text="Vendors", padx=5, pady=5, bd=2)
        frame.pack(padx=10, pady=5, fill="x")

        tk.Label(frame, text="Name").pack()
        self.vendor_name = tk.Entry(frame)
        self.vendor_name.pack()

        tk.Label(frame, text="Contact").pack()
        self.vendor_contact = tk.Entry(frame)
        self.vendor_contact.pack()

        tk.Button(frame, text="Add Vendor", command=self.add_vendor).pack()

    def build_product_section(self):
        frame = tk.LabelFrame(self.root, text="Products", padx=5, pady=5, bd=2)
        frame.pack(padx=10, pady=5, fill="x")

        tk.Label(frame, text="Name").pack()
        self.product_name = tk.Entry(frame)
        self.product_name.pack()

        tk.Label(frame, text="Vendor").pack()
        self.vendor_select = ttk.Combobox(frame)
        self.vendor_select.pack()

        tk.Button(frame, text="Add Product", command=self.add_product).pack()

    def build_order_section(self):
        frame = tk.LabelFrame(self.root, text="Orders", padx=5, pady=5, bd=2)
        frame.pack(padx=10, pady=5, fill="x")

        tk.Label(frame, text="Customer").pack()
        self.order_customer = ttk.Combobox(frame)
        self.order_customer.pack()

        tk.Label(frame, text="Product").pack()
        self.order_product = ttk.Combobox(frame)
        self.order_product.pack()

        tk.Button(frame, text="Add Order", command=self.add_order).pack()

    # New section for LLM command input.
    def build_llm_section(self):
        frame = tk.LabelFrame(self.root, text="LLM Command", padx=5, pady=5, bd=2)
        frame.pack(padx=10, pady=5, fill="x")

        tk.Label(frame, text="Enter command").pack()
        self.llm_input = tk.Entry(frame)
        self.llm_input.pack()

        tk.Button(frame, text="Process Command", command=self.process_llm_command).pack()

    def refresh_lists(self):
        self.vendor_select['values'] = [v["name"] for v in self.erp.vendors]
        self.order_customer['values'] = [c["name"] for c in self.erp.customers]
        self.order_product['values'] = [p["name"] for p in self.erp.products]

    def add_customer(self):
        self.erp.add_customer(self.customer_name.get(), self.customer_email.get())
        self.customer_name.delete(0, tk.END)
        self.customer_email.delete(0, tk.END)
        self.refresh_lists()

    def add_vendor(self):
        self.erp.add_vendor(self.vendor_name.get(), self.vendor_contact.get())
        self.vendor_name.delete(0, tk.END)
        self.vendor_contact.delete(0, tk.END)
        self.refresh_lists()

    def add_product(self):
        vendor_name = self.vendor_select.get()
        vendor = next((v for v in self.erp.vendors if v["name"] == vendor_name), None)
        if vendor:
            self.erp.add_product(self.product_name.get(), vendor["id"])
            self.product_name.delete(0, tk.END)
            self.vendor_select.set('')
            self.refresh_lists()

    def add_order(self):
        customer = next((c for c in self.erp.customers if c["name"] == self.order_customer.get()), None)
        product = next((p for p in self.erp.products if p["name"] == self.order_product.get()), None)
        if customer and product:
            self.erp.add_order(customer["id"], product["id"])
            self.order_customer.set('')
            self.order_product.set('')
            self.refresh_lists()

    # New function to process the command entered in the LLM section.
    def process_llm_command(self):
        command_text = self.llm_input.get().strip()
        if not command_text:
            messagebox.showerror("Error", "Please enter a command.")
            return
        result = local_llm_decipher(command_text)
        messagebox.showinfo("LLM Command Result", f"Action: {result['action']}\nDetails: {result['details']}")
        self.llm_input.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ERPApp(root)
    root.mainloop()
