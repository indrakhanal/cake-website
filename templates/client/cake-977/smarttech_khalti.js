function show_khalti_popup(product_name,product_identity,product_url,total_payable_amount,public_key){
   
var config = {

   "publicKey": public_key,
   "productIdentity": product_identity,
   "productName": product_name,
   "productUrl": product_url,
   "eventHandler": {
      onSuccess(payload) {
        return {status:"success", data:payload}
         
      },
      onError(error) {
        console.log("Khalti Error: ", error)
        return {status:"error", message:error}
      },
      onClose() {
        return {status:"closed"}
      }
   }
   };

   checkout = new KhaltiCheckout(config);
   checkout.show({ amount: total_payable_amount * 100 });

  }






