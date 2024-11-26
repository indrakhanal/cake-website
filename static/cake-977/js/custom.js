//product-detail slider

var slideIndex = 1;
showSlides(slideIndex);

function plusSlides(n) {
  showSlides(slideIndex += n);
}

function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  var i;
  var slides = document.getElementsByClassName("mySlides");
  var dots = document.getElementsByClassName("demo");
  if (n > slides.length) {slideIndex = 1}
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
      slides[i].style.display = "none";
  }
  for (i = 0; i < dots.length; i++) {
      dots[i].className = dots[i].className.replace(" active", "");
  }
  slides[slideIndex-1].style.display = "block";
  dots[slideIndex-1].className += " active";
}


//select weight 

function chooseSize(n) {
  var i;
  var sizeIndex = 1; 
  var sizes = document.getElementsByClassName("weight");

  if (n > sizes.length) {sizeIndex = 1}
  if (n < 1) {sizeIndex = sizes.length}

  for (i = 0; i < sizes.length; i++) {
    sizes[i].className = sizes[i].className.replace("weight active", "weight");
  }
  sizeIndex = n;
  sizes[sizeIndex-1].className += " active";
  // var value = sizes[sizeIndex-1].innerHTML;
  // console.log(value);
}




