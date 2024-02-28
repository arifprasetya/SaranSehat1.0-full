setTimeout(function() {
    var flashMessage = document.getElementById('flash-message');
    if (flashMessage) {
      flashMessage.style.display = 'none';
    }
}, 2000);
  
$(document).ready(function() {
    $('#resetButton').click(function() {
    location.reload();
    });
});

$(document).ready(function() {
  $('#scrollTop').click(function() {
      $('html, body').animate({ scrollTop: 0 }, 'slow');
  });
});