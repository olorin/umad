			<div id="motd">
				<h2>Don't panic.</h2>

				<p>Pop your search term in, Elasticsearch (that's <em>ES</em> for particularly hoopy froods) will do the rest. Try searching for ticket numbers, customer names, people's names, phone numbers, anything you can think of.</p>

				<p>ES joins multiple search terms with <em>AND</em> by default (ie. the document must contain all the terms you specify).</p>

				<p>Different types of documents have different associated metadata that you can search on. Try it out:
					<ul>
						<li>Search for tickets that have <a href="javascript:fillInSearchBox('emails:matt.palmer@anchor.com.au');">been womble'd</a></li>
						<li>Perhaps a server <a href="javascript:fillInSearchBox('customer:roosters');">belonging to the Roosters</a></li>
						<li>Tickets that <a href="javascript:fillInSearchBox('realnames:&quot;Matthias Oertli&quot; dell');">Matthias has had a hand in, with Dell</a></li>
						<li>...but only the <a href="javascript:fillInSearchBox('realnames:&quot;Matthias Oertli&quot; dell status:new');">new ones</a></li>
					</ul>
				</p>
			</div>
