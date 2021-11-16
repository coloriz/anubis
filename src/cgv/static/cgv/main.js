$('#form').submit(function(event) {
   $('#btn-submit').prop('disabled', true).children().addClass('visually-hidden');
   $('#spinner').removeClass('visually-hidden');
});