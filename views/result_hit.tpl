				<li class="{{ highlight_class }}">
				<div class="hitlink">
					% # The `join` is paranoia against multiple metadatas called 'name' or 'title'
					% linktext = '||'.join([ x[1] for x in other_metadata if x[0] == 'name' ]) if "name" in [ x[0] for x in other_metadata ] else id
					% linktext = '||'.join([ x[1] for x in other_metadata if x[0] == 'title' ]) if "title" in [ x[0] for x in other_metadata ] else linktext
					<a href="{{ id }}">{{ linktext }}</a>
				</div>

				% if "name" in [ x[0] for x in other_metadata] or "title" in [ x[0] for x in other_metadata]:
				<div class="hiturl">{{ id }}</div>
				% end

				<span style="white-space: pre-line;">{{! extract }}</span><br />
				% if other_metadata: # only if the list is non-empty
					<ul>
					% for tuple in other_metadata:
						<li class="metadata">{{ tuple[0] }}: {{ tuple[1] }}</li>
					% end
					</ul>
				% end
				</li>

