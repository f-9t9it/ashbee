from frappe import _


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
