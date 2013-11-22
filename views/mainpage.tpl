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
	</script>
</head>

<body>
	<div id="container">

		<div id="searchbox">
			<a href="/?q=mad"><img src="/static/umad.png" style="border:0;" alt="UMAD logo"></a><br />

			<form name="q" method="get" action="/">
				<p id="searchform">
					<input type="search" id="searchinput" name="q" placeholder="What be ye lookin' for?" value="{{ searchterm }}" autofocus="autofocus">
					<input type="submit" value="Unearth Me A Document!">
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
					<span style="font-size: larger;">Displaying <strong>{{ len(hits) }} results</strong></span>
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
</body>
</html>
