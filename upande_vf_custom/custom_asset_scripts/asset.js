frappe.ui.form.on('Asset', {
    onload: function(frm) {
        // Remove 'Scrap Asset' button on form load
        frm.remove_custom_button('Scrap Asset', 'Manage');
    },
    
    custom_maintenance_schedule: function(frm) {
        // Check if custom_maintenance_schedule has a value
        if (frm.doc.custom_maintenance_schedule) {
            frappe.db.get_doc("VF Asset Maintenance Schedule Tasks", frm.doc.custom_maintenance_schedule)
                .then(am_doc => {
                    console.log(am_doc);

                    frappe.call({
                        method: "asset_maintenance_tasks2",
                        args: {
                            message: {
                                record: am_doc,
                                asset_name: frm.doc.name
                            }
                        },
                        callback: function(response) {
                            console.log(response.message);
                            var name = response.message;
                            // Route to the saved document form in draft mode
                            frappe.set_route('Form', 'VF Asset Maintenance Schedule', name);
                        }
                    });
                });
        }
    }
});
