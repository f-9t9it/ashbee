import frappe
from pprint import pprint


def patch_trailing_space():
    colours = frappe.get_all('Item Attribute Value', filters={'parent': 'Colour'}, fields=['attribute_value', 'name'])

    trailing_attributes = []

    for colour in colours:
        colour_value = colour.get('attribute_value')
        if colour_value[-1] == ' ':
            colour['attribute_value'] = colour_value.strip()
            trailing_attributes.append(colour)

    pprint(trailing_attributes)

    for attribute in trailing_attributes:
        frappe.db.sql("""
            UPDATE `tabItem Attribute Value`
            SET attribute_value = %(attribute_value)s
            WHERE name = %(name)s
        """, attribute)

    frappe.db.commit()
