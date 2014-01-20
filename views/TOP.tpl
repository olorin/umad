<!DOCTYPE html>
<html>
<head>
	<title>UMAD?</title>
	<link rel="stylesheet" href="/static/umad.css">

	<script type="text/javascript">
		function fillInSearchBox(searchterm) {
			var box = document.getElementById("searchinput");
			box.value = searchterm;
			box.focus();
		}

		function refreshHitcount() {
			var hitcount = $("#hitcount");
			hitcount.text( $(".result-card").length );
		}

		function killResultsMatchingClass(resultClass) {
			var cardSelector = ".result-card." + resultClass;
			$( cardSelector ).fadeOut(1000, function() { $( cardSelector ).remove(); refreshHitcount(); });
		}

		function killResultsNotMatchingClass(resultClass) {
			var cardSelector = ".result-card:not(." + resultClass + ")";
			$( cardSelector ).fadeOut(1000, function() { $( cardSelector ).remove(); refreshHitcount(); });
		}

		function shareWithSysadmins(url, description) {
			var roomname = "robots";

			// XXX: This is probably hella vulnerable to injection, I haven't tested it properly yet.
			// The correct way to do this is to use JS to extract the URL and Description from the preceding <a> on the calling side,
			// instead of writing it into the document and jumping through these dumb hoops to avoid escaping issues.
			// Once fixed, we can ditch the jquery base64 module as well.
			// XXX: Can we fill in the user's name? The server side should have access to that and can write it in.
			var message = "Some sysadmin Liked this UMAD result\n(¬‿¬) " + $.base64.decode(description) + " - " + $.base64.decode(url);

			// http://api.jquery.com/jQuery.post/
			$.post("http://hubot.anchor.net.au:8080/message/room/" + roomname + "@conference.jabber.engineroom.anchor.net.au", "data="+encodeURIComponent(message) );
			alert("Done!\n\n(in future this'll be done as a nice in-page notification instead of a modal popup)");
		}
	</script>
	<script src="/static/jquery-1.10.2.min.js"></script>
	<script src="/static/jquery-base64.js"></script>
</head>

<body>
	<div id="container">
