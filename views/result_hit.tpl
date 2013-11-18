				<li class="{{ highlight_class }}"><a href="{{ id }}">{{ id }}</a><br />
				<span style="white-space: pre-line;">{{! extract }}</span><br />
				% if other_metadata:
					<ul>
					% for tuple in other_metadata:
						<li>{{ tuple[0] }}: {{ tuple[1] }}</li>
					% end
					</ul>
				% end
				</li>

