$(".checkout-success-btn").click(function() {
    var parent = $(this).parents(".checkout-first-form");
    var grandParent = $(parent).parents(".checkout-section");
    // console.log(parent);
    $(parent).css('display','none');
    $(grandParent).find('.cart__body').find('.small').css('display','none');
    $(grandParent).find(".signup-text-check").css('display','none');
    $(grandParent).find('.checkout-login-section').css('display','none');
    $(grandParent).find(".change_email").css('display','flex');
    $(grandParent).find(".shipping-delivery-section").css('display','block');
    
});

$(document).ready(function () {
  var form = $('#receiver-form');
  $(form).validate({
    rules: {
      senderfullname: {
      required: true,
      minlength: 3
      },
      senderaddress: {
      required: true
      },
      senderemail: {
      required: true,
      email: true
      },
      senderphone: {
        required: true,
        number: true
      },
      receipantfullname: {
        required: true,
        minlength: 3
      },
      receipantaddress: {
        required: true
      },
      receipantemail: {
        required: true,
        email: true
      },
      receipantphone: {
        required: true,
        number: true
      },
      number: true,
      min: 0
      },
      messages: {
        receipantphone: {
          required: "This field is required",
          maxlength: 10
        }
      }
  });  
});


$('#receiver-form').on('submit',function(e) {
  e.preventDefault();
  if ( $(this)[0].checkValidity() === true ) {
    jumpToPayment();
  };  
});

function jumpToPayment() {
    var parent = $('#submit-checkoutform').parents(".shipping-delivery-section");
    var grandParent = $(parent).parents(".checkout-section");  
    $(parent).css('display','none');
    $(grandParent).find(".change_address").css('display','flex');
    $(grandParent).find(".payment").css('display','block'); 
};

$("#change-address-button").click(function() {
    var parent = $(this).parents(".text-section-address");
    var grandParent = $(parent).parents(".change_address");
    var mainCheckoutSec = $(grandParent).parents(".checkout-section");
    // console.log(mainCheckoutSec);
    // console.log(grandParent);
    // console.log(parent);
    $(grandParent).css('display','none');
    $(mainCheckoutSec).find('.shipping-delivery-section').css('display','block');
    $(mainCheckoutSec).find('.payment').css('display','none');
});