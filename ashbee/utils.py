import frappe


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
    return frappe.db.sql("""
        SELECT project, SUM(total_outgoing_value) AS sum_total_outgoing_value
        FROM `tabStock Entry`
        WHERE docstatus = 1
        AND purpose = 'Material Issue'
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY project
    """, filters, as_dict=1)


def get_all_timesheet_details(filters):
    return frappe.db.sql("""
        SELECT project, SUM(costing_amount) AS sum_costing_amount
        FROM `tabTimesheet Detail`
        WHERE docstatus = 1
        AND DATE(from_time) <= %(to_date)s
        AND DATE(to_time) >= %(from_date)s
        GROUP BY project
    """, filters, as_dict=1)


def get_all_direct_costs(filters):
    return frappe.db.sql("""
        SELECT job_no as project, SUM(direct_cost) AS sum_direct_cost
        FROM `tabDirect Cost Item`
        WHERE docstatus = 1
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


def test():
    filters = {
        'from_date': '2019-04-24',
        'to_date': '2019-05-26'
    }

    return get_all_timesheet_details(filters)
