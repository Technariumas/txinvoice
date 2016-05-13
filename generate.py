#!/usr/bin/env python3
import txinvoice
import yaml
from decimal import Decimal
import os
import datetime

def yaml_load_file(filename):
    with open(filename) as f:
        return yaml.load(f)

invoices = yaml_load_file("data/invoices.yaml")
parties = yaml_load_file("data/parties.yaml")

def party(value):
    if isinstance(value, str):
        return parties[value]
    else:
        return value

for invoice in invoices:
    id = invoice['id']
    filename = "invoices/{}.pdf".format(id)
    date = invoice['date']

    if os.path.exists(filename) and datetime.date.fromtimestamp(os.path.getmtime(filename)) > date:
        continue

    print(filename)
    series = id[:2]
    number = id[2:]
    template_data = {
        "date": "{:%F}".format(date),
        "series": series,
        "number": number,
        "seller": party(invoice["provider"]),
        "client": party(invoice["recipient"]),
        "items": []
    }

    sum = Decimal('0.00')
    for item in invoice["items"]:
        item = item.copy()
        if "quantity" in item:
            item["total"] = str(Decimal(item["quantity"]) * Decimal(item["price"]))
        template_data["items"].append(item)
        sum += Decimal(item["total"])
    template_data["sum"] = str(sum)
    template_data["vat"] = "0"
    template_data["total"] = str(sum)

    print(template_data)
    txinvoice.render_invoice(template_data, filename=filename)
