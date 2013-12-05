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
			$( cardSelector ).fadeOut(500, function() { $( cardSelector ).remove(); refreshHitcount(); });
		}

		function killResultsNotMatchingClass(resultClass) {
			var cardSelector = ".result-card:not(." + resultClass + ")";
			$( cardSelector ).fadeOut(500, function() { $( cardSelector ).remove(); refreshHitcount(); });
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

		<div id="searchbox">
			<a href="/?q=mad"><img src="/static/umad.png" class="maxwidth90" style="border:0;" alt="UMAD logo"></a><br />

			<form name="q" method="get" action="/">
				<p id="searchform">
					<input type="search" id="searchinput" class="maxwidth90" name="q" placeholder="What be ye lookin' for?" value="{{ searchterm }}" autofocus="autofocus">
					<input type="submit" class="maxwidth90" value="Unearth Me A Document!">
				</p>
			</form>

		</div> <!-- END searchbox -->

	% if not searchterm:
		<div id="motd">
			% include motd.tpl
		</div>
	% else:
		<div id="motd" class="hidden">
			% include motd.tpl
		</div>
	% end


		<div id="output">
		% if searchterm:
			% if hits:
				<div id="hitstats">
					<span style="font-size: larger;">Displaying <strong><span id="hitcount">{{ len(hits) }}</span> results</strong></span>
					% if hit_limit > 0 and len(hits) >= hit_limit:
						<div class="hitstats-explanation">
							<em>Results may be truncated, hitlimit={{ hit_limit }}</em>
						</div>
					% end
				</div>
				<ul id="hits">
				% for hit in hits:
					% # This syntax is good for Bottle < 0.12, after that I think it should be:  include('result_hit.tpl', hit=hit)
					% include result_hit.tpl highlight_class=hit['highlight_class'], id=hit['id'], extract=hit['extract'], other_metadata=hit['other_metadata']
				% end
				</ul>
			% else:
					No results found.
			% end
		% else:
			<!-- No results here ^_^ -->
		% end
		</div> <!-- END output -->

	</div> <!-- END container -->

	<!-- Can't have a cool website without a Tweet button, lololol -->
	<!-- OPTIONAL FOR NOW
	<script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';fjs.parentNode.insertBefore(js,fjs);}}(document, 'script', 'twitter-wjs');</script>
	-->
</body>
</html>
