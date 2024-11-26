

$("#customCheck").click(function(){
    if($(this).is(":checked")) {
        $("#eggless").attr("src", "../img/veg-logo-png-6.svg");
    } else {
        $("#eggless").attr("src", "../img/veg-grey.svg");
    }
});

$("#customCheck1").click(function(){
    if($(this).is(":checked")) {
        $("#sugarfree").attr("src", "../img/sugarfree-icon.svg");
    } else {
        $("#sugarfree").attr("src", "../img/sugarfree-icon-grey.svg");
    }
});
