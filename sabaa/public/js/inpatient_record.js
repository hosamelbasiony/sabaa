// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
alert();
frappe.ui.form.on('Inpatient Record', {
	setup: function(frm) {
		// frm.get_field('drug_prescription').grid.editable_fields = [
		// 	{fieldname: 'drug_code', columns: 2},
		// 	{fieldname: 'drug_name', columns: 2},
		// 	{fieldname: 'dosage', columns: 2},
		// 	{fieldname: 'period', columns: 2}
		// ];
	},
	refresh: function(frm) {
		// frm.set_query('admission_service_unit_type', function() {
		// 	return {
		// 		filters: {
		// 			'inpatient_occupancy': 1,
		// 			'allow_appointments': 0
		// 		}
		// 	};
		// });

		// frm.set_query('primary_practitioner', function() {
		// 	return {
		// 		filters: {
		// 			'department': frm.doc.medical_department
		// 		}
		// 	};
		// });        
        
        alert("insurance_policy: " + frm.doc.insurance_policy);

		if (!frm.doc.__islocal || true) {
			if (frm.doc.status == 'Admitted') {
				// frm.add_custom_button(__('Schedule Discharge'), function() {
				// 	schedule_discharge(frm);
				// });
			} else if (frm.doc.status == 'Admission Scheduled') {
				// frm.add_custom_button(__('Cancel Admission'), function() {
				// 	cancel_ip_order(frm)
				// })
				// frm.add_custom_button(__('Admit'), function() {
				// 	admit_patient_dialog(frm);
				// } );
			} else if (frm.doc.status == 'Discharge Scheduled') {
				// frm.add_custom_button(__('Discharge'), function() {
				// 	discharge_patient(frm);
				// } );
				if (frm.doc.insurance_policy) {
					frm.add_custom_button(__('Create Insurance Coverage'), function() {
						create_insurance_coverage(frm);
					});
				}
			}
		}

        frm.set_query('insurance_policy', function() {
            alert("ffffffffff");
			return {
				filters: {
					'patient': frm.doc.patient,
					'docstatus': 1
				}
			};
		});
    }
});