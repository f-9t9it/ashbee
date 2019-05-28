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


def get_all_material_issues(project, filters):
    fields = ['sum(total_outgoing_value) as sum_total_outgoing_value']
    record_filters = {
        'project': project,
        'purpose': 'Material Issue',
        'docstatus': 1
    }

    material_issues = frappe.get_all('Stock Entry', filters=record_filters, fields=fields)

    return material_issues


def get_all_timesheets(project, filters):
    fields = ['sum(costing_amount) as sum_costing_amount']
    record_filters = {
        'project': project,
        'docstatus': 1
    }

    timesheets = frappe.get_all('Timesheet Detail', filters=record_filters, fields=fields)

    return timesheets


def get_all_direct_cost(project, filters):
    fields = ['sum(direct_cost) as sum_direct_cost']
    record_filters = {
        'job_no': project
    }

    direct_costs = frappe.get_all('Direct Cost Item', filters=record_filters, fields=fields)

    return direct_costs
