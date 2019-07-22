import frappe
from frappe.utils.data import get_first_day, get_last_day


def calculate_overhead_charges(project):
    """
    Sum labor cost (Timesheets),
    direct cost (Direct Cost),
    material issue (Stock Entry)
    indirect cost (Indirect Cost)

    :param project: Project doctype
    :return:
    """
    costing_sum = sum([
        project.total_costing_amount,
        project.ashbee_total_direct_cost,
        project.total_consumed_material_cost,
        project.ashbee_total_indirect_cost
    ])

    return costing_sum * 0.20


def get_all_material_issues(filters):
    filters.update({'project': frappe.db.get_single_value('Ashbee Settings', 'central_project')})
    return frappe.db.sql("""
        SELECT project, SUM(total_outgoing_value) AS sum_total_outgoing_value
        FROM `tabStock Entry`
        WHERE docstatus = 1
        AND (project != %(project)s AND project<>'')
        AND purpose = 'Material Issue'
        AND ashbee_is_return = 0
        AND ashbee_production_issue = 0
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY project
    """, filters, as_dict=1)


def get_all_timesheet_details(filters):
    filters.update({'project': frappe.db.get_single_value('Ashbee Settings', 'central_project')})
    return frappe.db.sql("""
        SELECT project, SUM(costing_amount) AS sum_costing_amount
        FROM `tabTimesheet Detail`
        WHERE docstatus = 1
        AND (project != %(project)s AND project<>'')
        AND DATE(from_time) <= %(to_date)s
        AND DATE(to_time) >= %(from_date)s
        GROUP BY project
    """, filters, as_dict=1)


def get_all_direct_costs(filters):
    filters.update({'project': frappe.db.get_single_value('Ashbee Settings', 'central_project')})
    return frappe.db.sql("""
        SELECT job_no as project, SUM(direct_cost) AS sum_direct_cost
        FROM `tabDirect Cost Item`
        WHERE docstatus = 1
        AND job_no != %(project)s
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY job_no
    """, filters, as_dict=1)


def get_all_indirect_costs(filters):
    return frappe.db.sql("""
        SELECT project, SUM(allocated) AS sum_allocated
        FROM `tabIndirect Cost Item`
        INNER JOIN `tabIndirect Cost`
        ON `tabIndirect Cost Item`.parent = `tabIndirect Cost`.name
        WHERE `tabIndirect Cost`.docstatus = 1
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY project
    """, filters, as_dict=1)


def get_central_expenses(filters):
    filters.update({'project': frappe.db.get_single_value('Ashbee Settings', 'central_project')})
    res = frappe.db.sql("""
            SELECT SUM(total_outgoing_value)
            FROM `tabStock Entry`
            WHERE docstatus = 1
            AND purpose = 'Material Issue'
            AND project = %(project)s
            AND ashbee_is_return = 0
            AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        """, filters)
    return res[0][0] if res else 0.00


def get_central_labour(filters):
    filters.update({'project': frappe.db.get_single_value('Ashbee Settings', 'central_project')})
    res = frappe.db.sql("""
            SELECT SUM(costing_amount)
            FROM `tabTimesheet Detail`
            WHERE docstatus = 1
            AND project = %(project)s
            AND DATE(from_time) <= %(to_date)s
            AND DATE(to_time) >= %(from_date)s
        """, filters)
    return res[0][0] if res else 0.00


def get_all_material_returns(filters):
    filters.update({'project': frappe.db.get_single_value('Ashbee Settings', 'central_project')})
    return frappe.db.sql("""
        SELECT project, SUM(qty) AS material_return
        FROM `tabStock Entry Detail`
        INNER JOIN `tabStock Entry`
        ON `tabStock Entry Detail`.parent = `tabStock Entry`.name
        WHERE `tabStock Entry`.docstatus = 1
        AND `tabStock Entry`.ashbee_is_return = 1
        AND `tabStock Entry`.project != %(project)s
        AND `tabStock Entry`.purpose = 'Material Issue'
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY project
    """, filters, as_dict=1)


def get_costs_by_projects(filters):
    direct_costs = get_all_direct_costs(filters)
    material_issues = get_all_material_issues(filters)
    timesheet_details = get_all_timesheet_details(filters)

    projects = _sum_costs_by_projects(
        direct_costs,
        material_issues,
        timesheet_details
    )

    excluded_projects = get_excluded_projects()

    for excluded_project in excluded_projects:
        projects.pop(excluded_project, None)

    return projects


def get_month_date_range(posting_date):
    return {
        'from_date': get_first_day(posting_date),
        'to_date': get_last_day(posting_date)
    }


def get_central_entry(voucher_no, voucher_detail_no=None):
    filters = {'voucher_no': voucher_no, 'docstatus': 1}

    if voucher_detail_no:
        filters.update({'voucher_detail_no': voucher_detail_no})

    central_entry_doc = None
    central_entry = frappe.get_all('Central Entry', filters=filters)

    if central_entry:
        name = central_entry[0]['name']
        central_entry_doc = frappe.get_doc('Central Entry', name)

    return central_entry_doc


def get_color_variants():
    variants = frappe.get_all(
        'Item Variant Attribute',
        filters={'attribute': 'Colour'},
        fields=['parent', 'attribute_value']
    )
    return {variant['parent']: variant['attribute_value'] for variant in variants}


def create_central_entry(stock_entry):
    return frappe.get_doc({
        'doctype': 'Central Entry',
        'voucher_type': 'Stock Entry',
        'voucher_no': stock_entry.get('name'),
        'posting_date': stock_entry.get('posting_date'),
        'allocation': stock_entry.get('total_amount')
    }).insert()


def get_central_costs(filters):
    res = frappe.db.sql("""
        SELECT cep.project, cep.allocation, cep.labor_allocation
        FROM `tabCentral Expense Project` AS cep
        INNER JOIN `tabCentral Expense` AS ce
        ON cep.parent = ce.name
        WHERE ce.docstatus = 1
        AND ce.from_date <= %(to_date)s
        AND ce.to_date >= %(from_date)s
    """, filters, as_dict=True)
    return res


def get_excluded_projects():
    projects = frappe.get_all('Ashbee Settings Project', fields=['project'])
    return [project.get('project') for project in projects]


def _sum_costs_by_projects(direct_costs, material_issues, timesheet_details):
    projects = {}

    _set_summed_dict(direct_costs, 'project', 'sum_direct_cost', projects)
    _set_summed_dict(material_issues, 'project', 'sum_total_outgoing_value', projects)
    _set_summed_dict(timesheet_details, 'project', 'sum_costing_amount', projects)

    return projects


def _set_summed_dict(sum_list, field_key, field_value, _):
    for sum_element in sum_list:
        key = sum_element[field_key]
        value = sum_element[field_value]

        if key in _:
            value = value + _[key]

        _[key] = value

    return _


def test():
    filters = {
        'from_date': '2019-04-24',
        'to_date': '2019-05-31'
    }

    print(get_all_timesheet_details(filters))
    print(get_all_direct_costs(filters))
    print(get_all_indirect_costs(filters))
    print(get_all_material_issues(filters))
    print(get_all_material_returns(filters))
    print(get_central_entry('MTSOUT-19-00007'))
