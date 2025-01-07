// frappe.ui.form.on('Stock Entry', {
//     stock_entry_type(frm){
//         frappe.call({
//             method: 'upande_vf_custom.custom_scripts.server_scripts.stock_entry.add_hcf',
//             args: {
//                 message: {
//                     doc: frm.doc
//                 }
//             },
//             btn: $('.primary-action'),
//             freeze: true,
//             callback: (r) => {
//                 if(r.message){
//                     data = r.message

//                     frm.refresh_field("items")

//                 }
                               
//             }
//         })
//     }
// })
