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
        AND project != %(project)s
        AND purpose = 'Material Issue'
        AND ashbee_is_return = 0
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY project
    """, filters, as_dict=1)


def get_all_timesheet_details(filters):
    filters.update({'project': frappe.db.get_single_value('Ashbee Settings', 'central_project')})
    return frappe.db.sql("""
        SELECT project, SUM(costing_amount) AS sum_costing_amount
        FROM `tabTimesheet Detail`
        WHERE docstatus = 1
        AND project != %(project)s
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
    return res[0][0] if res else None


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
    return res[0][0] if res else None


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

    return _sum_costs_by_projects(
        direct_costs,
        material_issues,
        timesheet_details
    )


def get_month_date_range(posting_date):
    return {
        'from_date': get_first_day(posting_date),
        'to_date': get_last_day(posting_date)
    }


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
