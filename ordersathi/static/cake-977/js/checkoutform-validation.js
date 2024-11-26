
$("#receiver-form").submit(function(e){
    e.preventDefault;
    if($(this).isValid()){
        alert("done");     
    } 
});    

// $("#submit-checkoutform").on("submit", function(e){
//     var parent = $(this).parents(".shipping-delivery-section");
//     var grandParent = $(parent).parents(".checkout-section");
//     $(parent).css('display','none');
//     $(grandParent).find(".change_address").css('display','flex');
//     $(grandParent).find(".payment").css('display','block');
// });  

// $('#receiver-form').submit(function (e) {
//     e.preventDefault;
//     if (e.result == true) {
//         var parent = $(this).parents(".shipping-delivery-section");
//         var grandParent = $(parent).parents(".checkout-section");
//         $(parent).css('display','none');
//         $(grandParent).find(".change_address").css('display','flex');
//         $(grandParent).find(".payment").css('display','block');
//     }
//   });