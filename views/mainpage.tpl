<!DOCTYPE html>
<html>
<head>
	<title>UMAD?</title>
	<link rel="stylesheet" href="/static/umad.css">
</head>

<body>
	<div id="container">

		<div id="searchbox">
			<img src="/static/umad.png" style="border:0;" alt="UMAD logo"><br />

			<form name="q" method="get" action="/">
				<p id="searchform">
					<input type="search" id="searchinput" name="q" placeholder="What be ye lookin' for?" value="{{ searchterm }}">
					<input type="submit" value="Unearth Me A Document!">
				</p>
			</form>
		</div> <!-- END searchbox -->


		<div id="results">
		% if searchterm:
			% if hits:
				<ul>
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
		</div> <!-- END results -->

	</div> <!-- END container -->
</body>
</html>
