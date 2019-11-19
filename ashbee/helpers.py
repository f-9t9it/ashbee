import frappe
from frappe import _
from toolz import pluck


def new_column(label, fieldname, fieldtype, width, options=None):
    """
    Create a report column
    :param label:
    :param fieldname:
    :param fieldtype:
    :param width:
    :param options:
    :return:
    """
    column = {"label": _(label), "fieldname": fieldname, "fieldtype": fieldtype, "width": width}

    print(column)

    if options:
        column.update({'options': options})
    return column


def round_off_rows(data, fields, decimals=3):
    for row in data:
        for field in fields:
            rounded = round(row.get(field), decimals)
            row[field] = rounded


def fill_item_name(func):
    """
    Accepts any function that have an array of data with description
    Outputs together with item and item name
    :param func:
    :return:
    """
    def inner(*args):
        data = func(*args)

        items = list(pluck('description', data))
        items_sql = list(map(lambda x: "'{}'".format(x), items))
        in_items = ', '.join(items_sql)
        item_names = frappe.db.sql("""
            SELECT name, item_name
            FROM `tabItem`
            WHERE name IN ({})
        """.format(in_items), as_dict=True)

        items_dict = {item['name']: item['item_name'] for item in item_names}
        for row in data:
            name = row.get('description')
            row['description'] = '{} ({})'.format(name, items_dict[name])

        return data
    return inner


def total_to_column(column):
    """
    Accepts any function that have an array of data with `rate` and `qty` columns and computes it to specific column
    :param column: Column total
    :return: decorator function
    """
    def total_to_column_decorator(func):
        def total(row):
            row_with_total = row
            row_with_total[column] = row.get('rate') * abs(row.get('qty'))
            return row_with_total

        def inner(*args):
            return list(map(total, func(*args)))

        return inner

    return total_to_column_decorator


def exclude_items(items):
    """
    Accepts any function that have an array of data and excludes the items
    :param items: Excluded items
    :return:
    """
    def exclude_items_decorator(func):
        def filter_item(row):
            return row['description'] not in items

        def inner(*args):
            return list(filter(filter_item, func(*args)))

        return inner

    return exclude_items_decorator
