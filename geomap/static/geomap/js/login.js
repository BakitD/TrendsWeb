$(function () {
  $('#login').submit(function (e) {
    e.preventDefault();
    var data = $(this).serialize();
    $.ajax({
	type: "POST",
	url: "/login/",
	data: data,
	cache: false,
	success: function(data) {
		$(".authorized").show();
		$(".unauthorized").hide();
		$("#user_name").text(data.user_name);
		$("#login_errors").text(data.login_errors);
		
	}
    });
  });
});
