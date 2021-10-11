// side nav functionality
$(document).ready(function(){
    $('.sidenav').sidenav({edge: "right"});
    $('.slider').slider();
    $('.collapsible').collapsible();
    $('.tooltipped').tooltip();
    $('.datepicker').datepicker({
        format: "mmm dd yyyy",
        yearRange: 3,
        showClearBtn: true,
        i18n:{
          done: "Select"
        }
    });
  });
