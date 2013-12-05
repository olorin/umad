				% # FIXME: Why did I make it a list of 2-element tuples when a dict makes more sense? Will fix soon, but do local convesion for now.
				% other_metadata = dict(other_metadata)

				% # Convert CSS highlighting classes to a semantic description of the document type (always plural)
				% highlight_classes_to_doctypes = { 'highlight-portal-orange':"provsys servers", 'highlight-luka':"RT tickets" }

				<li class="result-card {{ highlight_class }}">
				<div class="hitlink">
					% linktext = other_metadata.get('name', id)
					% linktext = other_metadata.get('title', linktext)
					<a href="{{ id }}">{{ linktext }}</a> <span class="lsf social-button-jabber" title="SHARE with #sysadmins" onClick="javascript:shareWithSysadmins('{{ id.encode('base64').replace('\n','').strip() }}', '{{ linktext.encode('base64').replace('\n','').strip() }}');">sns</span>
				</div>

				% if "name" in other_metadata or "title" in other_metadata:
				<div class="hiturl">{{ id }}</div>
				% end

				<span class="excerpt">{{! extract }}</span><br />

				<div class="metadata-button">
					<span class="lsf">tag</span>

					% if other_metadata: # only if the list is non-empty
					<div class="other-metadata">
						Other metadata
						<ul>
							% for key in other_metadata:
							<li class="metadata"><strong>{{ key.capitalize() }}:</strong> {{ other_metadata[key] }}</li>
							% end
						</ul>
					</div>
					% end
				</div>

				<div class="doc-source-solo">
					<span class="lsf" title="ONLY show {{ highlight_classes_to_doctypes[highlight_class] }}" onClick="javascript:killResultsNotMatchingClass('{{ highlight_class }}');">smile</span>
				</div>

				<div class="doc-source-mute">
					<span class="lsf" title="DISMISS all {{ highlight_classes_to_doctypes[highlight_class] }}" onClick="javascript:killResultsMatchingClass('{{ highlight_class }}');">frustrate</span>
				</div>
				</li>

