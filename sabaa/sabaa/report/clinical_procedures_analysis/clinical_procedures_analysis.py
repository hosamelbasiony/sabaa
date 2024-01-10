# Copyright (c) 2024, Hosam and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = [
		{
			"fieldname": "count",
			"fieldtype": "Data",
			"label": "Count",
			"width": 250
		},
		{
			"fieldname": "procedure_template",
			"fieldtype": "Data",
			"label": "Procedure Type",
			"width": 450
		}
	]

	data = [
		{"count": 100, "procedure_template": "procedure_template 1"},
		{"count": 5, "procedure_template": "procedure_template 2"},
	]

	procs = frappe.get_all("Clinical Procedure", fields=["procedure_template", "creation"])

	frappe.errprint(filters)

	return columns, data
