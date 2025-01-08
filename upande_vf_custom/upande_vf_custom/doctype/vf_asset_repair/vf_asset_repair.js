frappe.ui.form.on('VF Asset Repair', {
    setup: function(frm) {
        frm.fields_dict.cost_center.get_query = function(doc) {
            return {
                filters: {
                    'is_group': 0,
                    'company': doc.company
                }
            };
        };

        frm.fields_dict.project.get_query = function(doc) {
            return {
                filters: {
                    'company': doc.company
                }
            };
        };
    },

    stock_items_on_form_rendered() {
        erpnext.setup_serial_or_batch_no();
    },

    // Function to calculate the repair cost, including purchase invoices and stock items
    update_repair_cost: function(frm) {
        var repair_cost = 0;
        var total_stock_value = 0;

        // Loop through purchase invoices to sum the amounts (Repair Cost)
        $.each(frm.doc.purchase_invoices || [], function(index, row) {
            if (row.amount) {
                repair_cost += row.amount;
            }
        });

        // Set the repair cost field
        frm.set_value('repair_cost', repair_cost);

        // Loop through stock items to sum their total values (Total Stock Value)
        $.each(frm.doc.stock_items || [], function(index, row) {
            if (row.valuation_rate && row.consumed_quantity) {
                var item_total = row.valuation_rate * row.consumed_quantity;
                total_stock_value += item_total;
            }
        });

        // Set the total repair cost as the sum of both (Repair Cost + Total Stock Value)
        var total_repair_cost = repair_cost + total_stock_value;
        frm.set_value('total_repair_cost', total_repair_cost);
    }
});

frappe.ui.form.on('VF Asset Repair Consumed Item', {
    item_code: function(frm, cdt, cdn) {
        var item = locals[cdt][cdn];

        let item_args = {
            'item_code': item.item_code,
            'warehouse': frm.doc.warehouse,
            'qty': item.consumed_quantity,
            'serial_no': item.serial_no,
            'company': frm.doc.company
        };

        frappe.call({
            method: 'erpnext.stock.utils.get_incoming_rate',
            args: {
                args: item_args
            },
            callback: function(r) {
                frappe.model.set_value(cdt, cdn, 'valuation_rate', r.message);
                frappe.model.set_value(cdt, cdn, 'total_value', item.consumed_quantity * r.message);
                frm.trigger('update_repair_cost'); 
            }
        });
    },

    consumed_quantity: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var total_value = row.consumed_quantity * row.valuation_rate;
        frappe.model.set_value(cdt, cdn, 'total_value', total_value);

        frm.trigger('update_repair_cost'); 
    },
});

frappe.ui.form.on('VF AR Purchase Invoices', {
    accepted_qty: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.accepted_qty && row.rate) {
            var amount = row.accepted_qty * row.rate;
            frappe.model.set_value(cdt, cdn, 'amount', amount);
        }
        frm.trigger('update_repair_cost'); 
    },

    rate: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.accepted_qty && row.rate) {
            var amount = row.accepted_qty * row.rate;
            frappe.model.set_value(cdt, cdn, 'amount', amount);
        }
        frm.trigger('update_repair_cost'); 
    },

    purchased_quantity: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', row.accepted_qty * row.rate);
        frm.trigger('update_repair_cost'); 
    },

repair_status: (frm) => {
    if (frm.doc.completion_date && frm.doc.repair_status == "Completed") {
        frappe.call({
            method: "upande_vf_custom.upande_vf_custom.doctype.vf_asset_repair.vf_asset_repair.get_downtime",
            args: {
                "failure_date": frm.doc.failure_date,
                "completion_date": frm.doc.completion_date
            },
            callback: function(r) {
                if (r.message) {
                    frm.set_value("downtime", r.message + "Hrs");
                }
            }
        });
    }

    if (frm.doc.repair_status == "Completed") {
        frm.set_value('completion_date', frappe.datetime.now_datetime());
    }
},
});