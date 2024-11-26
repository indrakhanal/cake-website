 /*Horizontal Stepper*/

 var currentTab = 0; // Current tab is set to be the first tab (0)
 showTab(currentTab); // Display the current tab
 
 function showTab(n) {
   // This function will display the specified tab of the form...
   var x = document.getElementsByClassName("tab");
   x[n].style.display = "block";
   //... and fix the Previous/Next buttons:
   if (n == 0) {
     document.getElementById("prevBtn").style.display = "none";
     document.getElementById("calendar-back").style.display = "none";
     document.getElementById("space").style.display = "inline";
     document.getElementById("exampleModalLabel2").style.display = "none";
     document.getElementById("exampleModalLabel1").style.display = "block";
   } 
   else {
     document.getElementById("prevBtn").style.display = "block";
     document.getElementById("calendar-back").style.display = "block";
     document.getElementById("space").style.display = "none";
     document.getElementById("exampleModalLabel1").style.display = "none";
     document.getElementById("exampleModalLabel2").style.display = "block"; 
   } 
    
    /* else {
     document.getElementById("prevBtn").style.display = "flex";
     document.getElementById("calendar-back").style.display = "block";
     document.getElementById("space").style.display = "none";
     document.getElementById("exampleModalLabel3").style.display = "block";
     document.getElementById("exampleModalLabel1").style.display = "none";
     document.getElementById("exampleModalLabel2").style.display = "none"; 
   } */ //needed if there are more than 2 tabs
   if (n == (x.length - 1)) {
     document.getElementById("nextBtn").innerHTML = "Submit";
   } else {
     document.getElementById("nextBtn").innerHTML = "Next";
   }
   //... and run a function that will display the correct step indicator:
   fixStepIndicator(n)
 }
 
 function nextPrev(n) {
   // This function will figure out which tab to display
   var x = document.getElementsByClassName("tab");
   // Exit the function if any field in the current tab is invalid:
   //if (n == 1 && !validateForm()) return false;
   // Hide the current tab:
   x[currentTab].style.display = "none";
   // Increase or decrease the current tab by 1:
   currentTab = currentTab + n;
   // if you have reached the end of the form...
   if (currentTab >= x.length) {
     // ... the form gets submitted:
     //document.getElementById("nextBtn").setAttribute("data-dismiss","modal");
     document.getElementById("nextBtn").setAttribute("type","submit");
     document.getElementById("regForm").submit();
   } else {
   // Otherwise, display the correct tab:
   showTab(currentTab);
   }
  }   

  


 
 /* function validateForm() {
   // This function deals with validation of the form fields
   var x, y, i, valid = true;
   x = document.getElementsByClassName("tab");
   y = x[currentTab].getElementsByTagName("div");
   // A loop that checks every input field in the current tab:
   for (i = 0; i < y.length; i++) {
     // If a field is empty...
     if (y[i].value == "") {
       // add an "invalid" class to the field:
       y[i].className += " invalid";
       // and set the current valid status to false
       valid = false;
     }
   }
   // If the valid status is true, mark the step as finished and valid:
   if (valid) {
     document.getElementsByClassName("step")[currentTab].className += " finish";
   }
   return valid; // return the valid status
 } */
 
 function fixStepIndicator(n) {
   // This function removes the "active" class of all steps...
   var i, x = document.getElementsByClassName("dot");
   for (i = 0; i < x.length; i++) {
     x[i].className = x[i].className.replace(" active", "");
   }
   //... and adds the "active" class on the current step:
   x[n].className += " active";
 }
 