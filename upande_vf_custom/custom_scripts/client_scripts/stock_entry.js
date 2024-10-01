frappe.ui.form.on('Stock Entry', {
    stock_entry_type(frm){
        frappe.call({
            method: 'upande_vf_custom.custom_scripts.server_scripts.stock_entry.add_hcf',
            args: {
                message: {
                    doc: frm.doc
                }
            },
            btn: $('.primary-action'),
            freeze: true,
            callback: (r) => {
                if(r.message){
                    data = r.message
                    frm.doc.s_warehouse = data[0].s_warehouse
                    frm.refresh_field("s_warehouse")

                    processData(frm, data);
                }
                               
            }
        })
    }
})

function processData(frm, data) {
    const childTableField = 'items';

    const existing = new Set(frm.doc[childTableField].map(row => row.item_code)); 
    data.forEach(d => {
         if (!existing.has(d.item_code)) {
            let newRow = frm.add_child(childTableField);
            newRow.custom_hcf = d.custom_hcf; 
            newRow.item_code = d.item_code;
            newRow.s_warehouse = d.s_warehouse;

            existing.add(data.item_code);
        }
    });
    
    frm.refresh_field(childTableField); 
}