import math
from frappe.utils.data import getdate


def year_diff(string_ed_date, string_st_date):
    days_diff = (getdate(string_ed_date) - getdate(string_st_date)).days
    return math.floor(days_diff / 365.0), days_diff % 365
