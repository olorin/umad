<!DOCTYPE html>
<html>
<head>
	<title>UMAD?</title>
	<link rel="stylesheet" href="/static/umad.css">

	<script type="text/javascript">
		var evilAnalyticsSocket;
		var documentLoadTimestamp = new Date().getTime();

		var resultsUUID = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,function(c){r=Math.random()*16|0,v=c=='x'?r:r&0x3|0x8;return v.toString(16);})

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

			var doctypeSelector = ".doc-type." + resultClass;
			$( doctypeSelector ).fadeOut(1000, function() { $( doctypeSelector ).remove(); });
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


% if searchterm:
		//
		// Evil umad analytics!
		//
		// ❤❤❤❤❤❤❤❤❤ clickjacking because we love you ❤❤❤❤❤❤❤❤❤
		//
		function initEvilAnalytics() {
			// Try to connect to the analytics websockets server
			// This is to try and see if our results suck. It really doesn't
			// matter if this stuff doesn't get through at all, or even if the
			// client doesn't support websockets. We just need to not accidentally
			// the entire javascript
			//
			try {
				evilAnalyticsSocket = new WebSocket("wss://"+document.location.hostname+":9876");
			} catch(e) {
				console.log("Don't have websockets. Can't spy on ur clikz. DINOSAAAAAUR", e);
				evilAnalyticsSocket = null;
			}
		}
        	function umadEvilAnalytics(stuff) {
			// Send analytics log entry to the websocket server.
			//
			// Again, we really don't care if this fails as long as
			// it doesn't affect the end user. The awesome thing is this is
			// even async (hopefully)
			if (evilAnalyticsSocket == null) return 1;
			try {
				evilAnalyticsSocket.send(stuff);
			} catch(e) {
				console.log("umad totally loves your browser cause it has websockets but it couldn't send analytics. awwww man.", e);
			}
			1;
		}
		var userClickCount = 0;
		var userClickOrder = [];
		% import json
		function evilUserClick(hitObject) {
			try {
				now = new Date().getTime();
				userClickCount = userClickOrder.push( hitObject['result_number'] );
				umadEvilAnalytics(JSON.stringify({
					'event': 'clickHit',
					'resultPageUUID': resultsUUID,
					'searchTerm': {{ !json.dumps(searchterm) }},
					'hitObject': hitObject,
					'msFromLoadToClick': now - documentLoadTimestamp,
					'timestamp': now / 1000,
					'clickCountForPage': userClickCount,
					'userClickOrder': userClickOrder
				}));
			} catch(e) { console.log(e); }
			1;
		}
		function evilUserReindex(hitObject) {
			try {
				now = new Date().getTime();
				userClickCount = userClickOrder.push( hitObject['result_number'] );
				umadEvilAnalytics(JSON.stringify({
					'event': 'clickReindex',
					'resultPageUUID': resultsUUID,
					'searchTerm': {{ !json.dumps(searchterm) }},
					'hitObject': hitObject,
					'msFromLoadToClick': now - documentLoadTimestamp,
					'timestamp': now / 1000,
					'clickCountForPage': userClickCount,
					'userClickOrder': userClickOrder
				}));
			} catch(e) { console.log(e); }
			1;
		}
		function evilPageLeft(e) {
			try {
				now = new Date().getTime();
				umadEvilAnalytics(JSON.stringify({
					'event': 'userLeftPage',
					'resultPageUUID': resultsUUID,
					'searchTerm': {{ !json.dumps(searchterm) }},
					'hotOrNot': userClickCount ? 'HOT' : 'NOT',
					'msFromLoadToClose': now - documentLoadTimestamp,
					'timestamp': now / 1000,
					'clickCountForPage': userClickCount,
					'userClickOrder': userClickOrder
				}));
			} catch(e) { console.log(e); }
			1;
		}
		function evilSearchedAgain() {
			try {
				now = new Date().getTime();
				umadEvilAnalytics(JSON.stringify({
					'event': 'userSearchedAgain',
					'oldResultPageUUID': resultsUUID,
					'oldSearchTerm': {{ !json.dumps(searchterm) }},
					'newSearchTerm': $('#searchinput')[0].value,
					'msFromLoadToSearchAgain': now - documentLoadTimestamp,
					'timestamp': now / 1000,
					'clickCountForPage': userClickCount,
					'userClickOrder': userClickOrder
				}));
			} catch(e) { console.log(e); }
			1;
		}
		initEvilAnalytics();
		window.onbeforeunload = evilPageLeft;
% end
	</script>
	<script src="/static/jquery-1.10.2.min.js"></script>
	<script src="/static/jquery-base64.js"></script>

</head>

<body>
	<div id="container">
