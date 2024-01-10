// Copyright (c) 2017, ESS LLP and contributors
// For license information, please see license.txt

let COMPANY = null;
let HEALTHCARE_SETTINGS = null;

frappe.ui.form.on('Clinical Procedure', {
	refresh: function (frm) {
		if (!COMPANY) {
			// get_company
			frappe.call({
				method: 'sabaa.sabaa.utils.get_company',
				args: {
					'company_name': frm.doc.company
				},
				callback: function (data) {
					if (data.message) {
						COMPANY = data.message.company;
						HEALTHCARE_SETTINGS = data.message.healthcare_settings;
						console.log("COMPANY: ", COMPANY);
						console.log("HEALTHCARE_SETTINGS: ", HEALTHCARE_SETTINGS);
					}
				}
			});
		}

		let btn_label = 'Set doctor fees entries';

		frm.add_custom_button(__(btn_label), function () {
			// add_doctor_fees(frm);
		}).addClass("btn-primaryy");

		frm.set_value('consume_stock', 1);
		frm.set_df_property("consume_stock", "read_only", 1);

		// if( frm.doc.docstatus == 1 ) frm.set_df_property("items", "read_only", 0);
		frm.set_df_property("items", "read_only", 0);

		const getConsumables = () => {
			frappe.call({
				'method': 'frappe.client.get',
				args: {
					doctype: 'Clinical Procedure Template',
					name: frm.doc.procedure_template
				},
				callback: function (data) {
					frm.set_value('medical_department', data.message.medical_department);
					frm.set_value('consume_stock', data.message.consume_stock);
					frm.events.set_warehouse(frm);
					frm.events.set_procedure_consumables(frm);
				}
			});

			// if (frm.doc.procedure_template) {
			// 	frappe.call({
			// 		method: 'sabaa.sabaa.utils.get_procedure_template_items',
			// 		args: {
			// 			'procedure_template': frm.doc.procedure_template
			// 		},
			// 		callback: function (data) {
			// 			if(data.message) {
			// 				frm.set_value('items', [...frm.doc.items, ...data.message]);
			// 			}
			// 		}
			// 	});
			// }
		}

		// if( frm.doc.docstatus == 0 ) getConsumables();

		if (frm.doc.status != "Completed") {
			frm.add_custom_button(__('Get Consumables List'), function () {
				getConsumables();
			}, __("Consumables"));
		}

		frm.set_query('patient', function () {
			return {
				filters: { 'status': ['!=', 'Disabled'] }
			};
		});

		frm.set_query('appointment', function () {
			return {
				filters: {
					'procedure_template': ['not in', null],
					'status': ['in', 'Open, Scheduled']
				}
			};
		});

		frm.set_query('service_unit', function () {
			return {
				filters: {
					'is_group': false,
					'allow_appointments': true,
					'company': frm.doc.company
				}
			};
		});

		frm.set_query('practitioner', function () {
			return {
				filters: {
					'department': frm.doc.medical_department
				}
			};
		});

		frm.set_query("medical_code", "codification_table", function (doc, cdt, cdn) {
			let row = frappe.get_doc(cdt, cdn);
			if (row.medical_code_standard) {
				return {
					filters: {
						medical_code_standard: row.medical_code_standard
					}
				};
			}
		});

		if (frm.doc.consume_stock) {
			frm.set_indicator_formatter('item_code',
				function (doc) { return (doc.qty <= doc.actual_qty) ? 'green' : 'orange'; });
		}

		if (frm.doc.docstatus == 1) {
			if (frm.doc.status == 'In Progress') {
				let btn_label = '';
				let msg = '';
				if (frm.doc.consume_stock) {
					btn_label = __('Complete and Consume');
					msg = __('Complete {0} and Consume Stock?', [frm.doc.name]);
				} else {
					btn_label = 'Complete';
					msg = __('Complete {0}?', [frm.doc.name]);
				}

				frm.add_custom_button(__(btn_label), function () {
					frappe.confirm(
						msg,
						function () {
							frappe.call({
								method: 'complete_procedure',
								doc: frm.doc,
								freeze: true,
								callback: function (r) {
									if (r.message) {
										frappe.show_alert({
											message: __('Stock Entry {0} created', ['<a class="bold" href="/app/stock-entry/' + r.message + '">' + r.message + '</a>']),
											indicator: 'green'
										});
									}
									frm.reload_doc();
								}
							});
						}
					);
				}).addClass("btn-primary");

			} else if (frm.doc.status == 'Pending') {
				frm.add_custom_button(__('Start'), function () {
					frappe.call({
						doc: frm.doc,
						method: 'start_procedure',
						callback: function (r) {
							if (!r.exc) {
								if (r.message == 'insufficient stock') {
									let msg = __('Stock quantity to start the Procedure is not available in the Warehouse {0}. Do you want to record a Stock Entry?', [frm.doc.warehouse]);
									frappe.confirm(
										msg,
										function () {
											frappe.call({
												doc: frm.doc,
												method: 'make_material_receipt',
												freeze: true,
												callback: function (r) {
													if (!r.exc) {
														frm.reload_doc();
														let doclist = frappe.model.sync(r.message);
														frappe.set_route('Form', doclist[0].doctype, doclist[0].name);
													}
												}
											});
										}
									);
								} else {
									frm.reload_doc();
								}
							}
						}
					});
				}).addClass("btn-primary");
			}
		}
	},

	procedure_template: function (frm) {
		if (frm.doc.procedure_template) {
			frappe.call({
				'method': 'frappe.client.get',
				args: {
					doctype: 'Clinical Procedure Template',
					name: frm.doc.procedure_template
				},
				callback: function (data) {
					frm.set_value('medical_department', data.message.medical_department);
					frm.set_value('consume_stock', data.message.consume_stock);
					frm.events.set_warehouse(frm);
					frm.events.set_procedure_consumables(frm);
				}
			});
		}
	},

	custom_calculate_fees: function (frm) {
		// custom_medical_team_members
		// محمد عبد الرحمن

		frappe.call({
			method: 'sabaa.sabaa.utils.get_doctor_fees',
			args: {
				patient: frm.doc.patient
			},
			callback: function (data) {
				if (data.message) {

					if (!frm.doc.custom_medical_team_members) return;

					for (let medical_team_member of frm.doc.custom_medical_team_members) {
						// healthcare_practitioner
						// role - fees_item - fees - journal_entry

						// {
						// 	"item_prices": [
						// 	  {
						// 		"price_list": "Standard Buying",
						// 		"item_code": "أجر طبيب التخدير",
						// 		"price_list_rate": 2500
						// 	  },
						// 	  {
						// 		"price_list": "Standard Buying",
						// 		"item_code": "أجر طبيب التخدير المساعد",
						// 		"price_list_rate": 2000
						// 	  },
						// 	  {
						// 		"price_list": "Standard Buying",
						// 		"item_code": "أجر الطبيب المساعد",
						// 		"price_list_rate": 2250
						// 	  }
						// 	],
						// 	"insurance_plan": null,
						// 	"price_list": null
						//   }

						let price = null;

						if (medical_team_member.role == "Anesthesiologist") {

							price = data.message.item_prices.find(x =>
								x.price_list == data.message.price_list && x.item_code == HEALTHCARE_SETTINGS.anaesthesiologist_fees_item);
							if (!price) price = data.message.item_prices.find(x => x.item_code == HEALTHCARE_SETTINGS.anaesthesiologist_fees_item);

						} else if (medical_team_member.role == "Assistant Doctor") {

							price = data.message.item_prices.find(x =>
								x.price_list == data.message.price_list && x.item_code == HEALTHCARE_SETTINGS.assistant_doctor_fees_item);
							if (!price) price = data.message.item_prices.find(x => x.item_code == HEALTHCARE_SETTINGS.assistant_doctor_fees_item);

						} else if (medical_team_member.role == "Assistant Anesthesiologist") {

							price = data.message.item_prices.find(x =>
								x.price_list == data.message.price_list && x.item_code == HEALTHCARE_SETTINGS.assistant_anaesthesiologist_fees_item);
							if (!price) price = data.message.item_prices.find(x => x.item_code == HEALTHCARE_SETTINGS.assistant_anaesthesiologist_fees_item);

						}

						if (price) medical_team_member.fees = price.price_list_rate;


						// HEALTHCARE_SETTINGS
						// anaesthesiologist_fees_item
						// assistant_anaesthesiologist_fees_item
						// assistant_doctor_fees_item
						// clinical_procedure_consumable_item
						// medical_team_fees_item
					}

				}
			}
		});
	},
});

frappe.ui.form.on('Medical Team Member', {
	custom_medical_team_members_add: function(frm, cdt, cdn) {
		// 
	},

	role: function(frm, cdt, cdn) {
		calculate_doctor_fees(frm);
	},

	healthcare_practitioner: function(frm, cdt, cdn) {
		calculate_doctor_fees(frm);
	},

	custom_medical_team_members_remove: function(frm, cdt, cdn) {
		// 
	}
})

var calculate_doctor_fees = (frm) => {
	frappe.call({
		method: 'sabaa.sabaa.utils.get_doctor_fees',
		args: {
			patient: frm.doc.patient
		},
		callback: function (data) {
			if (data.message) {

				if (!frm.doc.custom_medical_team_members) return;

				for (let medical_team_member of frm.doc.custom_medical_team_members) {
					// healthcare_practitioner
					// role - fees_item - fees - journal_entry

					// {
					// 	"item_prices": [
					// 	  {
					// 		"price_list": "Standard Buying",
					// 		"item_code": "أجر طبيب التخدير",
					// 		"price_list_rate": 2500
					// 	  },
					// 	  {
					// 		"price_list": "Standard Buying",
					// 		"item_code": "أجر طبيب التخدير المساعد",
					// 		"price_list_rate": 2000
					// 	  },
					// 	  {
					// 		"price_list": "Standard Buying",
					// 		"item_code": "أجر الطبيب المساعد",
					// 		"price_list_rate": 2250
					// 	  }
					// 	],
					// 	"insurance_plan": null,
					// 	"price_list": null
					//   }

					let price = null;

					if (medical_team_member.role == "Anesthesiologist") {

						price = data.message.item_prices.find(x =>
							x.price_list == data.message.price_list && x.item_code == HEALTHCARE_SETTINGS.anaesthesiologist_fees_item);
						if (!price) price = data.message.item_prices.find(x => x.item_code == HEALTHCARE_SETTINGS.anaesthesiologist_fees_item);

					} else if (medical_team_member.role == "Assistant Doctor") {

						price = data.message.item_prices.find(x =>
							x.price_list == data.message.price_list && x.item_code == HEALTHCARE_SETTINGS.assistant_doctor_fees_item);
						if (!price) price = data.message.item_prices.find(x => x.item_code == HEALTHCARE_SETTINGS.assistant_doctor_fees_item);

					} else if (medical_team_member.role == "Assistant Anesthesiologist") {

						price = data.message.item_prices.find(x =>
							x.price_list == data.message.price_list && x.item_code == HEALTHCARE_SETTINGS.assistant_anaesthesiologist_fees_item);
						if (!price) price = data.message.item_prices.find(x => x.item_code == HEALTHCARE_SETTINGS.assistant_anaesthesiologist_fees_item);

					}

					if (price) medical_team_member.fees = price.price_list_rate;


					// HEALTHCARE_SETTINGS
					// anaesthesiologist_fees_item
					// assistant_anaesthesiologist_fees_item
					// assistant_doctor_fees_item
					// clinical_procedure_consumable_item
					// medical_team_fees_item
				}

			}
		}
	})
};

var add_doctor_fees = (frm) => {
	if (frm.doc.procedure_template) {
		frappe.call({
			method: 'sabaa.sabaa.utils.get_supplier_data',
			args: {
				'practitioner_name': frm.doc.practitioner_name,
				'item_code': frm.doc.procedure_template
			},
			callback: function (data) {
				if (data.message) {
					// default_payable_account
					// default_income_account
					let journal_entry = {
						"is_system_generated": 1,
						"voucher_type": "Doctor Fees Entry",
						"custom_claimed": 0,
						"cheque_no": "",
						"posting_date": new Date().toISOString().split('T')[0],
						"total_debit": data.message.price_list_rate,
						"total_credit": data.message.price_list_rate,
						"difference": 0.0,
						"multi_currency": 0,
						"total_amount_currency": COMPANY.default_currency,
						"total_amount": data.message.price_list_rate,
						"is_opening": "No",
						"doctype": "Journal Entry",
						"custom_clinical_procedure": frm.doc.name,
						"accounts": [
							{
								"account": COMPANY.default_payable_account,
								"party_type": "Supplier",
								"party": data.message.supplier_name,
								"account_currency": COMPANY.default_currency,
								"exchange_rate": 1.0,
								"debit_in_account_currency": 0.0,
								"debit": 0.0,
								"credit_in_account_currency": data.message.price_list_rate,
								"credit": data.message.price_list_rate,
								"is_advance": "No",
								"against_account": COMPANY.default_income_account,
								"reference_type": "Clinical Procedure",
								"reference_name": frm.doc.name
							},
							{
								"account": COMPANY.default_income_account,
								"account_currency": COMPANY.default_currency,
								"exchange_rate": 1.0,
								"debit_in_account_currency": data.message.price_list_rate,
								"debit": data.message.price_list_rate,
								"credit_in_account_currency": 0.0,
								"credit": 0.0,
								"is_advance": "No",
								"against_account": data.message.supplier_name
							}
						]

					};

					// custom_doctor_fees_journal_entry

					console.log(journal_entry);
					frappe.call({
						method: "sabaa.sabaa.utils.insert_doctor_fees_journal_entry",
						args: {
							journal_entry,
							invoice: frm.doc.name
						},
						callback: function (data) {
							console.log(data);
							frm.refresh();
						}
					});

				}
			}
		});
	}
}

// refresh(frm) {

// 	frm.set_query('service_unit', erpnext.queries.address_query);
// 	erpnext.utils.get_address_display(frm, 'shipping_address_name', 'shipping_address', false);

