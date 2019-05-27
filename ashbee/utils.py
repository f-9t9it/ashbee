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
