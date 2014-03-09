$(function () {
  var url = '/upload/';

  $('#fileupload').fileupload({
    url: url,
    dataType: 'json',
    done: function (e, data) {
      console.log(data.result[0].url);
      window.location = data.result[0].url;
    },
    progressall: function (e, data) {
      var progress = parseInt(data.loaded / data.total * 100, 10);
      $('#progress .bar').css('width', progress + '%');
      if (progress == 100) {
        $('#msg-analyzing').show();
      }
    }
  });

});
