// var min = $('.qtyValue').attr('min');
// var max = $('.qtyValue').attr('max');
// console.log(min);
// console.log(max);


$(".increase").click(function() {
    var value = parseInt($(this).siblings('.qtyValue').attr('value'),10);
    var max = parseInt($(this).siblings('.qtyValue').attr('max'),10);
    console.log(value);
    value = isNaN(value) ? 0 : value;    
    if ( value < max ) {
        value++;
    } else if ( value >= max) {
        $(this).attr("disabled", "disabled").off('click');
    }
    $(this).siblings('.qtyValue').attr('value', value);
  });
  
  $(".decrease").click(function() {
    // var value = parseInt($('.qtyValue').attr('value'), 10);
    var value = parseInt($(this).siblings('.qtyValue').attr('value'),10);
    var min = parseInt($(this).siblings('.qtyValue').attr('min'),10);
    value = isNaN(value) ? 0 : value;
    value < 1 ? value = 1 : '';
    if ( value > min ) {
        value--;
    } else if ( value <= min ) {
        $(".decrease").attr("disabled", "disabled").off('click');
    }
    $(this).siblings('.qtyValue').attr('value', value);
  });