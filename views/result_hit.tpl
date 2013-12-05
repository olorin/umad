				% # FIXME: Why did I make it a list of 2-element tuples when a dict makes more sense? Will fix soon, but do local convesion for now.
				% other_metadata = dict(other_metadata)

				% # Convert CSS highlighting classes to a semantic description of the document type (always plural)
				% highlight_classes_to_doctypes = { 'highlight-portal-orange':"provsys servers", 'highlight-luka':"RT tickets" }

				<li class="result-card {{ highlight_class }}">
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

				<div class="doc-source-solo">
					<span class="lsf" title="ONLY show {{ highlight_classes_to_doctypes[highlight_class] }}" onClick="javascript:killResultsNotMatchingClass('{{ highlight_class }}');">smile</span>
				</div>

				<div class="doc-source-mute">
					<span class="lsf" title="DISMISS all {{ highlight_classes_to_doctypes[highlight_class] }}" onClick="javascript:killResultsMatchingClass('{{ highlight_class }}');">frustrate</span>
				</div>
				</li>

