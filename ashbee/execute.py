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


def patch_attribute_value():
    attrs = {
        '076': 'RAL-9003',
        '079': 'RAL-7004',
        '028': 'RAL-9005 Black'
    }

    for abbr, value in attrs.items():
        print('Processing {}...'.format(abbr))
        frappe.db.sql("""
            UPDATE `tabItem Attribute Value`
            SET attribute_value = %(attribute_value)s
            WHERE abbr = %(abbr)s
        """, {'abbr': abbr, 'attribute_value': value})

    frappe.db.commit()


def generate_central_entries_from_purchase_invoices():
    central_project = frappe.db.get_single_value('Ashbee Settings', 'central_project')

    purchase_invoice_items = frappe.db.sql("""
        SELECT pii.amount, pii.name, pi.posting_date
        FROM `tabPurchase Invoice Item` pii
        INNER JOIN `tabPurchase Invoice` pi
        ON pii.parent = pi.name
        WHERE pii.project = %s
        AND pii.docstatus = 1
        AND (pii.ashbee_central_entry IS NULL OR pii.ashbee_central_entry = '')
    """, central_project, as_dict=True)

    for item in purchase_invoice_items:
        name = item.get('name')
        amount = item.get('amount')
        posting_date = item.get('posting_date')

        central_entry = frappe.get_doc({
            'doctype': 'Central Entry',
            'posting_date': posting_date,
            'voucher_type': 'Purchase Invoice',
            'voucher_detail_no': name,
            'allocation': amount
        }).insert()

        central_entry.submit()

        frappe.db.set_value('Purchase Invoice Item', name, 'ashbee_central_entry', central_entry.name)

    frappe.db.commit()


def generate_central_entries_from_direct_costs():
    central_project = frappe.db.get_single_value('Ashbee Settings', 'central_project')

    filters = {
        'docstatus': 1,
        'central_entry': '',
        'job_no': central_project
    }

    fields = ['name', 'posting_date', 'direct_cost']

    direct_cost_items = frappe.db.get_all(
        'Direct Cost Item',
        filters=filters,
        fields=fields
    )

    for item in direct_cost_items:
        direct_cost_item = item.get('name')
        direct_cost = item.get('direct_cost')
        posting_date = item.get('posting_date')

        central_entry = frappe.get_doc({
            'doctype': 'Central Entry',
            'posting_date': posting_date,
            'voucher_type': 'Direct Cost',
            'voucher_detail_no': direct_cost_item,
            'allocation': direct_cost
        }).insert()

        central_entry.submit()

        frappe.db.set_value('Direct Cost Item', direct_cost_item, 'central_entry', central_entry.name)

    frappe.db.commit()


def cancel_central_entry_direct_cost():
    filters = {'voucher_type': 'Direct Cost'}

    central_entries = frappe.get_all('Central Entry', filters=filters)

    for central_entry in central_entries:
        name = central_entry.get('name')
        frappe.get_doc('Central Entry', name).cancel()


def unlink_central_entry_from_direct_cost():
    filters = {'central_entry': ['!=', '']}
    direct_cost_items = frappe.get_all('Direct Cost Item', filters=filters)

    for item in direct_cost_items:
        frappe.db.sql("""
            UPDATE `tabDirect Cost Item`
            SET central_entry = ''
            WHERE name=%s
        """, item.get('name'))

    frappe.db.commit()


def remove_trailing_space():
    corrections = []

    attributes = frappe.get_all('Item Variant Attribute', fields=['name', 'attribute_value'])
    for attribute in attributes:
        value = attribute.get('attribute_value')
        if value and value[-1] == ' ':
            corrections.append({
                'name': attribute.get('name'),
                'attribute_value': value.strip()
            })

    processed = 0
    total = len(corrections)

    for correction in corrections:
        frappe.db.sql("""
            UPDATE `tabItem Variant Attribute`
            SET attribute_value = %(attribute_value)s
            WHERE name = %(name)s
        """, correction)

        processed = processed + 1
        print("Processed {}/{}".format(processed, total))

    frappe.db.commit()


def set_total_direct_costs():
    direct_costs = frappe.db.sql("""
        SELECT sum(direct_cost) as total_direct_cost, parent
        FROM `tabDirect Cost Item`
        GROUP BY parent
    """, as_dict=1)

    computed = 0
    max_direct_cost = len(direct_costs)

    for direct_cost in direct_costs:
        name = direct_cost.get('parent')
        total_direct_cost = direct_cost.get('total_direct_cost')

        frappe.db.set_value('Direct Cost', name, 'total_direct_cost', total_direct_cost)
        computed = computed + 1

        print('Processed {}/{}'.format(computed, max_direct_cost))


def set_central_expense_company():
    """
    Set Central Expense company
    :return:
    """
    projects = list(map(lambda x: x['name'], frappe.get_all('Company')))

    print('Set Central Expenses company:')
    for i, project in enumerate(projects):
        print('({}) {}'.format(i, project))
    company_selected = int(input())

    confirm = input('Would you like to update Central Expenses with {} as company (y/n): '.format(projects[company_selected]))

    if confirm == 'y':
        frappe.db.sql("""
            UPDATE `tabCentral Expense`
            SET company = %s
        """, projects[company_selected])
        print('Updated all Central Expenses.')
    else:
        print('Aborted.')
