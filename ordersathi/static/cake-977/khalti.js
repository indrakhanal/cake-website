var script = document.createElement('script');
script.type = 'text/javascript';
script.src = 'https://khalti.com/static/khalti-checkout.js';
document.head.appendChild(script);

function open_khalti_popup(
  product_name,
  product_identity,
  product_url,
  total_payable_amount,
  public_key
) {
  var config = {
    publicKey: public_key,
    productIdentity: product_identity,
    productName: product_name,
    productUrl: product_url,
    eventHandler: {
      onSuccess(payload) {
        khalti_payment_success(payload);
      },
      onError(error) {
        khalti_payment_error(error);
      },
      onClose() {
        khalti_popup_closed();
      },
    },
  };

  checkout = new KhaltiCheckout(config);
  checkout.show({ amount: total_payable_amount * 100 });
}