				% # FIXME: Why did I make it a list of 2-element tuples when a dict makes more sense? Will fix soon, but do local convesion for now.
				% other_metadata = dict(other_metadata)
				<li class="{{ highlight_class }}">
				<div class="hitlink">
					% linktext = other_metadata.get('name', id)
					% linktext = other_metadata.get('title', linktext)
					<a href="{{ id }}">{{ linktext }}</a>
				</div>

				% if "name" in other_metadata or "title" in other_metadata:
				<div class="hiturl">{{ id }}</div>
				% end

				<span style="white-space: pre-line;">{{! extract }}</span><br />
				% if other_metadata: # only if the list is non-empty
					<ul>
					% for key in other_metadata:
						<li class="metadata">{{ key }}: {{ other_metadata[key] }}</li>
					% end
					</ul>
				% end
				</li>

