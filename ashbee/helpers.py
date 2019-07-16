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
