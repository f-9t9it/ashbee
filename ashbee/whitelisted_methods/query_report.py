import frappe
import json
from frappe.desk.query_report import run, export_query, get_columns_dict, build_xlsx_data
from functools import wraps, partial
from itertools import repeat


@frappe.whitelist()
def export_query_override():
    data = frappe._dict(frappe.local.form_dict)

    report_name = data.get('report_name')

    if report_name == 'Ashbee Single Job Cost':
        _export_ashbee_single_job_cost(data)
    else:
        export_query()


def export_with_header(func):
    """
    A decorator function that you can have header rows
    :param func:
    :return:
    """
    def build_xlsx(filename, xlsx_data, header):
        from frappe.utils.xlsxutils import make_xlsx
        xlsx_file = make_xlsx(header + xlsx_data, 'Query Report')

        frappe.response['filename'] = filename + '.xlsx'
        frappe.response['filecontent'] = xlsx_file.getvalue()
        frappe.response['type'] = 'binary'

    def wrapper(data):
        report_name = data.get('report_name')
        include_indentation = data.get('include_indentation')

        filters = json.loads(data.get('filters'))
        visible_idx = json.loads(data.get('visible_idx'))

        report_data = frappe._dict(run(report_name, filters))
        columns = get_columns_dict(report_data.columns)

        xlsx_data = build_xlsx_data(
            columns,
            report_data,
            visible_idx,
            include_indentation
        )

        row_length = len(xlsx_data[0])

        build = partial(build_xlsx, report_name, xlsx_data)

        return func(build, filters, row_length)

    return wrapper


@export_with_header
def _export_ashbee_single_job_cost(build, filters, row_length):
    project = filters.get('project')
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')

    ashbee_project_code = frappe.db.get_value('Project', project, 'ashbee_project_code')

    header = [
        ['ASHBEE METAL CLADDING WLL'],
        ['Job Income Expense Report'],
        [],
        ['{} - {}'.format(ashbee_project_code, project)],
        ['From {} to {}'.format(from_date, to_date)],
        []
    ]

    build(header)
