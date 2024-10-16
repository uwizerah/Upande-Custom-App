frappe.ui.form.on('Purchase Receipt', {
    on_submit: function(frm) {
        // Ensure custom_type is 'Feeds'
        // if (frm.doc.custom_type !== 'Feeds') {
        //     frappe.msgprint(__('Landed Cost Voucher can only be created for Purchase Receipts with custom type "Feeds".'));
        //     return;
        // }

        // Call the server-side method to create the LCV
        frappe.call({
            method: "upande_vf_custom.custom_scripts.server_scripts.purchase_receipt.create_landed_cost_voucher",
            args: {
                message:{
                    r_name: frm.doc.name
                }
            },
            callback: function(response) {
                if (response.message) {
                    console.log(response.message)
                    frappe.msgprint(`Landed Cost Voucher created: ${response.message}`);
                } else {
                    frappe.msgprint('Failed to create Landed Cost Voucher.');
                }
            }
        });
    }
});
