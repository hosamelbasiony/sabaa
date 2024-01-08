// Healthcare
frappe.ui.form.on('Sales Invoice', {
	refresh(frm) {
		if ((frm.doc.docstatus === 0 || frm.doc.docstatus === 1) && !frm.doc.is_return) {

			if (frm.doc.custom_claim_generated == 0 || true) {
				frm.add_custom_button(__('Show Insurance Coverage'), async () => {
					await calculate_insurance(frm);
				}, __('Insurance'));

				frm.add_custom_button(__('Apply Insurance Claims'), async () => {
					insert_claim_jornal_entry(frm);
				}, __('Insurance'));
			}
		}
	},

	on_submit(frm) {
		// frappe.throw(__("You can only redeem max {0} points in this order.", [" hhhhhhhhhh "]));
		calculate_insurance(frm)
		.then( ret => {
			alert("on_submit => insert_claim_jornal_entry")
			insert_claim_jornal_entry(frm);
		});

	},

	validate(frm) {
		// calculate_insurance(frm);
	},
});

// frappe.throw(__("You can only redeem max {0} points in this order.",[redeemable_points]));

var insert_claim_jornal_entry = async(frm) => {
	// frm.doc.custom_insurance_coverage_amount = 10
	let journal_entry = {
		"is_system_generated": 1,
		"voucher_type": "Insurance Claim Entry",
		"custom_claimed": 0,
		"cheque_no": "",
		"posting_date": new Date().toISOString().split('T')[0],
		"total_debit": frm.doc.custom_insurance_coverage_amount,
		"total_credit": frm.doc.custom_insurance_coverage_amount,
		"difference": 0.0,
		"multi_currency": 0,
		"total_amount_currency": "EGP",
		"total_amount": frm.doc.custom_insurance_coverage_amount,
		"is_opening": "No",
		"doctype": "Journal Entry",
		// "docstatus": 1,
		"accounts": [
			{
				// "docstatus": 1,
				"account": "Debtors - SH",
				"account_type": "Receivable",
				"party_type": "Customer",
				"party": frm.doc.customer, //"تقى علي حميد",
				"cost_center": "Main - SH",
				"account_currency": "EGP",
				"exchange_rate": 1.0,
				"debit_in_account_currency": 0.0,
				"debit": 0.0,
				"credit_in_account_currency": frm.doc.custom_insurance_coverage_amount,
				"credit": frm.doc.custom_insurance_coverage_amount,
				"is_advance": "No",
				"against_account": frm.doc.custom_insurance_payor,
				"reference_type": "Sales Invoice",
				"reference_name": frm.doc.name
			},
			{
				// "docstatus": 1,
				"account": "Debtors - SH",
				"account_type": "",
				"party_type": "Customer",
				"party": frm.doc.custom_insurance_payor,
				"cost_center": "Main - SH",
				"account_currency": "EGP",
				"exchange_rate": 1.0,
				"debit_in_account_currency": frm.doc.custom_insurance_coverage_amount,
				"debit": frm.doc.custom_insurance_coverage_amount,
				"credit_in_account_currency": 0.0,
				"credit": 0.0,
				"is_advance": "No",
				"against_account": frm.doc.customer
			}
		]

	};

	// insert_insurance_journal_entry
	frappe.call({
		method: "sabaa.sabaa.utils.insert_insurance_journal_entry",
		args: {
			journal_entry,
			invoice: frm.doc.name
		},
		callback: function (data) {
			console.log(data);
			frm.refresh();
		}
	});

	console.log(journal_entry);
};

var calculate_insurance = async (frm) => {
	await frappe.call({
		method: "sabaa.sabaa.utils.calculate_patient_insurance_coverage",
		args: {
			invoice: frm.doc
		},
		callback: function (data) {
			if (data.message) {
				let doc = data.message;
				// frm.set_value("items", doc.items);
				frm.set_value("custom_insurance_coverage_amount", doc.custom_insurance_coverage_amount);
				frm.set_value("custom_patient_payable_amount", doc.custom_patient_payable_amount + frm.doc.rounding_adjustment);

				// custom_insurance_eligibility_plan
				frm.set_value("custom_insurance_eligibility_plan", doc.custom_insurance_eligibility_plan);
				frm.set_value("custom_insurance_payor", doc.custom_insurance_payor);
				frm.set_value("custom_patient_insurance_policy", doc.custom_patient_insurance_policy);

				frm.trigger("validate");
				frm.refresh_fields();
				
			} else {
				// TODO
			}
		}
	});
};