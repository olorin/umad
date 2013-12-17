				% # FIXME: Why did I make it a list of 2-element tuples when a dict makes more sense? Will fix soon, but do local conversion for now.
				% other_metadata = dict(other_metadata)

				% # Convert CSS highlighting classes to a semantic description of the document type (always plural)
				% highlight_classes_to_doctypes = {}
				% highlight_classes_to_doctypes['highlight-portal-orange'] = "provsys servers"
				% highlight_classes_to_doctypes['highlight-luka'] = "RT tickets"
				% highlight_classes_to_doctypes[''] = "documents of unknown origin"

				<li class="result-card {{ highlight_class }}">
				<div class="hitlink">
					% linktext = other_metadata.get('name', id)
					% linktext = other_metadata.get('title', linktext)
					<a href="{{ id }}">{{ linktext }}</a> <span class="lsf social-button-jabber" title="SHARE with #robots" onClick="javascript:shareWithSysadmins('{{ id.encode('base64').replace('\n','').strip() }}', '{{ linktext.encode('base64').replace('\n','').strip() }}');">sns</span>
					<!-- OPTIONAL FOR NOW
					<a href="https://twitter.com/share" class="twitter-share-button" data-url="{{ id }}" data-text="{{ linktext }}" data-dnt="true">Tweet that shiz</a>
					-->
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
							% metadata_value = other_metadata[key]
							% if isinstance(metadata_value, (str, unicode)):
								<li class="metadata"><strong>{{ key.capitalize() }}:</strong> {{ metadata_value }}</li>
							% else:
								<li class="metadata"><strong>{{ key.capitalize() }}:</strong>
									<ul>
									% for value in metadata_value:
										<li class="metadata-subvalues">{{ value }}</li>
									% end
									</ul>
								</li>
							% end
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

