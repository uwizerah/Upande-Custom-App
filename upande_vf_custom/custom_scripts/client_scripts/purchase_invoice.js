frappe.ui.form.on('Purchase Invoice', {
    // before_save(frm){
    //     console.log("frm.doc.taxes")
    //     if(frm.doc.taxes){
    //         console.log(frm.doc.taxes)
    //         frm.doc.taxes.forEach((x) => {
    //             if(x.charge_type == "On Net Total"){
    //                 frappe.call({
    //                     method: 'upande_vf_custom.custom_scripts.server_scripts.purchase_invoice.update_taxes',
    //                     args: {
    //                         message: {
    //                             doc_name: frm.doc.name
    //                         }
    //                     },
    //                     btn: $('.primary-action'),
    //                     freeze: true,
    //                     callback: (r) => {
    //                         // if(r.message){
    //                         //     console.log(r.message)
    //                         //     frm.doc.reference_no = r.message
    //                             console.log(frm.doc.taxes)
    //                             // frm.refresh_field("taxes")
    //                         //     frm.save()
    //                         // }
                            
    //                     }
    //                 })
    //             }
    //         })
    //     }
    // }
    after_save(frm){
        frappe.call({
            method: 'upande_vf_custom.custom_scripts.server_scripts.purchase_invoice.update_taxes',
            args: {
                message: {
                    doc_name: frm.doc.name
                }
            },
            btn: $('.primary-action'),
            freeze: true,
            callback: (r) => {
                // if(r.message){
                //     console.log(r.message)
                //     frm.doc.reference_no = r.message
                    console.log(frm.doc.taxes)
                    frm.refresh_field("taxes")
                    // frm.save()
                // }
                
            }
        })
    
    }
})

