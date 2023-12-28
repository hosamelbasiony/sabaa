import frappe
from frappe import _
from frappe.utils import flt, money_in_words, round_based_on_smallest_currency_fraction

# doc.base_in_words = money_in_words(
# 	doc.base_grand_total, erpnext.get_company_currency(doc.company)
# )