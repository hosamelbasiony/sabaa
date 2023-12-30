(() => {
  var __create = Object.create;
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __getProtoOf = Object.getPrototypeOf;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __commonJS = (cb, mod) => function __require() {
    return mod || (0, cb[__getOwnPropNames(cb)[0]])((mod = { exports: {} }).exports, mod), mod.exports;
  };
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
    isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
    mod
  ));

  // ../sabaa/sabaa/public/js/taxes_and_totals.js
  var require_taxes_and_totals = __commonJS({
    "../sabaa/sabaa/public/js/taxes_and_totals.js"(exports) {
      erpnext.taxes_and_totals.calculate_outstanding_amount = () => {
        alert();
      };
      erpnext.taxes_and_totals.calculate_outstanding_amount2 = (update_paid_amount) => {
        if (in_list(["Sales Invoice", "POS Invoice"], exports.frm.doc.doctype) && exports.frm.doc.is_return) {
          exports.calculate_paid_amount();
        }
        if (exports.frm.doc.is_return || exports.frm.doc.docstatus > 0 || exports.is_internal_invoice())
          return;
        frappe.model.round_floats_in(exports.frm.doc, ["grand_total", "total_advance", "write_off_amount"]);
        if (in_list(["Sales Invoice", "POS Invoice", "Purchase Invoice"], exports.frm.doc.doctype)) {
          let grand_total = exports.frm.doc.rounded_total || exports.frm.doc.grand_total;
          let base_grand_total = exports.frm.doc.base_rounded_total || exports.frm.doc.base_grand_total;
          if (exports.frm.doc.party_account_currency == exports.frm.doc.currency) {
            var total_amount_to_pay = flt(grand_total - exports.frm.doc.total_advance - exports.frm.doc.write_off_amount, precision("grand_total"));
          } else {
            var total_amount_to_pay = flt(
              flt(base_grand_total, precision("base_grand_total")) - exports.frm.doc.total_advance - exports.frm.doc.base_write_off_amount,
              precision("base_grand_total")
            );
          }
          frappe.model.round_floats_in(exports.frm.doc, ["paid_amount"]);
          exports.set_in_company_currency(exports.frm.doc, ["paid_amount"]);
          if (exports.frm.refresh_field) {
            exports.frm.refresh_field("paid_amount");
            exports.frm.refresh_field("base_paid_amount");
          }
          if (in_list(["Sales Invoice", "POS Invoice"], exports.frm.doc.doctype)) {
            let total_amount_for_payment = exports.frm.doc.redeem_loyalty_points && exports.frm.doc.loyalty_amount ? flt(total_amount_to_pay - exports.frm.doc.loyalty_amount, precision("base_grand_total")) : total_amount_to_pay;
            exports.set_default_payment(total_amount_for_payment, update_paid_amount);
            exports.calculate_paid_amount();
          }
          exports.calculate_change_amount();
          var paid_amount = exports.frm.doc.party_account_currency == exports.frm.doc.currency ? exports.frm.doc.paid_amount : exports.frm.doc.base_paid_amount;
          exports.frm.doc.outstanding_amount = flt(total_amount_to_pay - flt(paid_amount) + flt(exports.frm.doc.change_amount * exports.frm.doc.conversion_rate), precision("outstanding_amount"));
        }
        if (exports.frm.doc.doctype == "Sales Invoice") {
          exports.frm.doc.custom_patient_payable_amount = 157.55;
        }
      };
    }
  });

  // ../sabaa/sabaa/public/js/sabaa.bundle.js
  var import_taxes_and_totals = __toESM(require_taxes_and_totals());
})();
//# sourceMappingURL=sabaa.bundle.IYFZG2NA.js.map
