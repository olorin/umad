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
					% include result_hit.tpl highlight_class=hit['highlight_class'], id=hit['id'], extract=hit['extract'], other_metadata=hit['other_metadata'], score=hit['score']
				% end
				</ul>
			% else:
					No results found for <span class="inline-query-display">{{ searchterm }}</span>
			% end
		% else:
			<!-- No results here ^_^ -->
		% end
		</div> <!-- END output -->
