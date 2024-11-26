$(function() {
    $( "#datepicker" ).datepicker({ 
      firstDay: 1,
      dateFormat: 'mm/dd/yy'
      });
      $("#datepicker").on("change",function(){
          var selected = $(this).val();
          console.log(selected);
      $('#datepicker-input').val(selected);    
    });   
}); 

$(function() {        
    $("input[name='time_radio']").on("change",function(){
        var selectedRadio = $("input[name='time_radio']:checked");
        var selectedParent = $(selectedRadio).parent(".custom-control.custom-radio");
        var selectedTime = $(selectedParent).find(".custom-control-label").text();
        console.log(selectedTime);
        $("#typetime-input").val(selectedTime);   
    });   
}); 