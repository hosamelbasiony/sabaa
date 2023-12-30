# override_doctype_class = {
# 	"Bank": "sabaa.overrides.bank.MyBank",
#   "Patient": "sabaa.overrides.patient.MyPatient",
#   "InpatientRecord": "sabaa.overrides.inpatient_record.InpatientRecord",
#   "Sales Invoice": "sabaa.sabaa.custom_doctype.sales_invoice.HealthcareSalesInvoice",
# }

# doc_events = {
# 	"Sales Invoice": {
# 		"on_submit": "sabaa.sabaa.utils.manage_invoice_submit_cancel",
# 		"on_cancel": "sabaa.sabaa.utils.manage_invoice_submit_cancel", # ????
# 	}
# }