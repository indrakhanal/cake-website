
$(document).ready(function(){
  $('#checkout-form ul.delpick li:first a').addClass(' active');
  $('#checkout-form input[type="radio"]').click(function(){
    $(this).parent().parent().tab('show');  
  });
  $('.nav-tabs a').on('shown.bs.tab', function(event){
    var x = $(event.target).text();         // active tab
    var y = $(event.relatedTarget).text();  // previous tab
    $(".act span").text(x);
    $(".prev span").text(y);
  });
});

$(document).ready(function(){
  $('#checkoutModalMobile ul.delpick li:first a').addClass(' active');
  $('#checkoutModalMobile input[type="radio"]').click(function(){
    $(this).parent().parent().tab('show');  
  });
  $('.nav-tabs a').on('shown.bs.tab', function(event){
    var x = $(event.target).text();         // active tab
    var y = $(event.relatedTarget).text();  // previous tab
    $(".act span").text(x);
    $(".prev span").text(y);
  });
});

// $(document).ready(function(){
//   $('li.nav-item').click(function(){
//     $(this).find('input[type="radio"]').attr("checked", "checked");
//     $(this).children().tab('show');
//     var button = $(this).find('input[type="radio"]');  
//     console.log(this);
//     console.log(button);
//   });
//   $('.nav-tabs a').on('shown.bs.tab', function(event){
//     var x = $(event.target).text();         // active tab
//     var y = $(event.relatedTarget).text();  // previous tab
//     $(".act span").text(x);
//     $(".prev span").text(y);
//   });
// });

