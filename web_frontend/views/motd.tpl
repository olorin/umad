% if not searchterm:
		<div id="motd">
% else:
		<div id="motd" class="hidden">
% end
			<h2>Don't panic.</h2>

			<p>Pop your search term in, Elasticsearch (that's <em>ES</em> for particularly hoopy froods) will do the rest. Try searching for ticket numbers, customer names, people's names, phone numbers, anything you can think of.</p>

			<p>ES joins multiple search terms with <em>AND</em> by default (ie. the document must contain all the terms you specify).</p>

			<p>Different types of documents have different associated metadata that you can search on. Try it out:</p>

			<ul>
				<li>Search for tickets that have <a href="javascript:fillInSearchBox('_type:rt email:matt.palmer@anchor.com.au');">been womble'd</a>
					<pre class="search-example">_type:rt email:matt.palmer@anchor.com.au</pre></li>
				<li>Or a particular ticket number, <a href="javascript:fillInSearchBox('rt:376603');">376603</a>
					<pre class="search-example">rt:376603</pre></li>
				<li>Perhaps a <a href="javascript:fillInSearchBox('map:SSL');">wiki result for SSL</a>
					<pre class="search-example">map:SSL</pre></li>
				<li>Or a server <a href="javascript:fillInSearchBox('customer:roosters');">belonging to the Roosters</a>
					<pre class="search-example">customer:roosters</pre>
				</li>
				<li>Tickets that <a href="javascript:fillInSearchBox('realname:&quot;Matthias Oertli&quot; dell');">Matthias has had a hand in, with Dell</a>
					<pre class="search-example">realname:&quot;Matthias Oertli&quot; dell</pre>
				</li>
				<li>...but only the <a href="javascript:fillInSearchBox('realname:&quot;Matthias Oertli&quot; dell status:new');">new ones</a>
					<pre class="search-example">realname:&quot;Matthias Oertli&quot; dell status:new</pre>
				</li>
			</ul>
		</div> <!-- END motd -->
