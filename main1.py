#cafe Management System Enhanced 
#imports
import json
import os
import fitz  # PyMuPDF
from datetime import datetime

#menu
menu = {
    0: {"Espresso": 79},
    1: {"Latte": 59},
    2: {"Cappuccino": 99},
    3: {"MacAlooTiki Burger": 49},
    4: {"VegSurprise Burger": 79},
    5: {"Mac Cheese Burger": 69},
    6: {"Chicken Burger": 69},
    7: {"Hardcore Hazzlenut cone": 49},
    8: {"Creampie Vanilla cone": 39},
    9: {"Racist Chocolate": 29},
    10: {"Small fries": 39},
    11: {"Medium fries": 59},
    12: {"Large fries": 69},
    13: {"Cheesy fries": 79},
}

#order
order = {}
def take_order():
    while True:
        try:
            item_no = input("Enter the item no. user want to order (or 'done' to finish): ")
            if item_no == "done":
                break
            item_no = int(item_no)
            if item_no in menu.keys():
                quantity = int(input("Enter the quantity: "))
                if quantity < 0:
                    print("Please order in postive number")
                    quantity = int(input("Enter the quantity: "))
                item = list(menu[item_no])[0]
                order[item] = quantity
            else:
                print("Sorry, we don't have that item.")
        except ValueError:
            print("❌ Invalid input. Please enter numeric values for item number and quantity.")
        except Exception as e:
            print(f"⚠️ Unexpected error occurred: {e}")
    return order

take_order_1 = take_order()

# Calculating the bill
def calculate_bill(order):
    try:
        total = 0 
        for item, quantity in order.items():
            price = None
            for entry in menu.values():
                if item in entry:
                    price = entry[item]
                    break
            if price is None:
                raise ValueError(f"Price for item '{item}' not found in menu.")
            total += price * quantity
        return total
    except Exception as e:
        print(f"⚠️ Error calculating bill: {e}")
        return 0

bill = calculate_bill(order)

# customer data
def customer_data():
    try:
        name = input("Enter customer name: ")
        contact = int(input("Enter customer contact number: "))
        number_str = str(contact)
        if len(number_str) != 10 or contact < 0:
            print("Please enter a valid contact number")
            contact = int(input("Enter customer contact number: "))
        return name, contact
    except ValueError:
        print("❌ Invalid contact number! Please enter numbers only.")
        return customer_data()
    except Exception as e:
        print(f"⚠️ Error in customer data: {e}")
        return customer_data()

cust_name, cust_num = customer_data()

# order information
def order_information():
    try:
        type = input("Enter Order type(Dine-in,Take-away,Delivery): ")
        order_number = int(input("Enter Order Number: "))
        payment_mode = input("Mode of Payment[UPI/Card/Cash]: ")
        if payment_mode == 'Cash':
            cash_received = int(input("Enter Cash Received: "))
            change_given = int(input("Enter Change given: "))
            return type, order_number, payment_mode, cash_received, change_given
        elif payment_mode in ['UPI', 'Card']:
            amount_paid = int(input("Enter Amount Paid: "))
            amount_given_back = int(input("Enter Amount Given Back: "))
            return type, order_number, payment_mode, amount_paid, amount_given_back
        else:
            print("Invalid payment mode. Please enter UPI, Card, or Cash.")
            return order_information()
    except ValueError:
        print("❌ Please enter valid numeric values where required.")
        return order_information()
    except Exception as e:
        print(f"⚠️ Error in order information: {e}")
        return order_information()

ord_type, ord_num, ord_pay_mode, amt_received, change_given = order_information()

#data
now = datetime.now()
current_date = now.strftime("%d-%m-%Y")
current_time = now.strftime("%I:%M %p")
data = {'Name': cust_name, 'contact': cust_num, 'Order Type': ord_type, 'OrderID': ord_num, 'Payment Mode': ord_pay_mode,
        'Order': take_order_1, 'total': bill, 'amount_received': amt_received, 'change_given': change_given,
        "Date": current_date, "Time": current_time}

# Saving data to JSON
def save_data_to_json(data, filename='order_data.json'):
    try:
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
        else:
            existing_data = []

        if isinstance(existing_data, dict):
            existing_data = [existing_data]

        existing_data.append(data)

        with open(filename, 'w') as f:
            json.dump(existing_data, f, indent=4)

        print("✅ Data saved successfully!")
    except Exception as e:
        print(f"⚠️ Error saving data to JSON: {e}")

save_data_to_json(data)

# --- Step 1: Load your HTML template ---
try:
    with open("temp.html", "r") as f:
        template_html = f.read()
except FileNotFoundError:
    print("❌ Error: 'temp.html' file not found.")
    template_html = ""
except Exception as e:
    print(f"⚠️ Error loading HTML template: {e}")
    template_html = ""

# --- Step 2: Prepare placeholders for 3 rows ---
try:
    items = list(data['Order'].items())[:3]
    rows = []
    for i in range(3):
        if i < len(items):
            item_name = items[i][0]
            qty = items[i][1]
            price = menu[[k for k, v in menu.items() if item_name in v][0]][item_name]
            total = price * qty
        else:
            item_name, qty, price, total = "", 0, 0, 0
        rows.append({
            f"Item{i+1}": item_name,
            f"Qty{i+1}": qty,
            f"Price{i+1}": price,
            f"Total{i+1}": total
        })
except Exception as e:
    print(f"⚠️ Error preparing order rows: {e}")
    rows = []

# --- Step 3: Compute subtotal, tax, grand total ---
try:
    subtotal = sum(row[f"Total{i+1}"] for i, row in enumerate(rows))
    tax = round(subtotal * 0.05, 2)
    grand_total = round(subtotal + tax, 2)
except Exception as e:
    print(f"⚠️ Error calculating totals: {e}")
    subtotal = tax = grand_total = 0

# --- Step 4: Replace placeholders in HTML ---
try:
    filled_html = template_html
    for i, row in enumerate(rows):
        for key, value in row.items():
            filled_html = filled_html.replace(f"{{{{{key}}}}}", str(value))

    placeholders = {
        "OrderID": data['OrderID'],
        "Date": data['Date'],
        "Time": data['Time'],
        "Subtotal": subtotal,
        "Tax": tax,
        "GrandTotal": grand_total,
        "PaymentMode": data['Payment Mode'],
        "AmountReceived": data.get('amount_received', 0),
        "ChangeGiven": data.get('change_given', 0),
        "Name": data['Name'],
        "Contact": data['contact']
    }

    for key, value in placeholders.items():
        filled_html = filled_html.replace(f"{{{{{key}}}}}", str(value))

    with open("receipt_filled.html", "w") as f:
        f.write(filled_html)

    print("✅ Receipt generated: receipt_filled.html")
except Exception as e:
    print(f"⚠️ Error generating receipt: {e}")
