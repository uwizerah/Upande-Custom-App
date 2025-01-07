frappe.ui.form.on('VF AR Purchase Invoices', {

    accepted_qty: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.accepted_qty && row.rate) {
            var amount = row.accepted_qty * row.rate;
            frappe.model.set_value(cdt, cdn, 'amount', amount);
        }
        update_repair_cost(frm); // Call function to update repair cost
    },

    rate: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.accepted_qty && row.rate) {
            var amount = row.accepted_qty * row.rate;
            frappe.model.set_value(cdt, cdn, 'amount', amount);
        }
        update_repair_cost(frm); // Call function to update repair cost
    },

    purchased_quantity: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', row.accepted_qty * row.rate);
        update_repair_cost(frm); // Call function to update repair cost
    },

});

// Function to calculate the total repair cost from the 'amount' fields in the table
function update_repair_cost(frm) {
    var total_amount = 0;
    
    // Loop through all rows in the 'VF AR Purchase Invoices' table
    $.each(frm.doc.purchase_invoices || [], function(index, row) {
        total_amount += row.amount || 0; // Add the 'amount' from each row
    });

    // Set the total in the 'repair_cost' field
    frm.set_value('repair_cost', total_amount);
}
