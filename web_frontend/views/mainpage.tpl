% include TOP.tpl

% include searchbox.tpl searchterm=searchterm, hits=hits, doc_types_present=doc_types_present

% include motd.tpl searchterm=searchterm

% if valid_search_query:
	% include searchresults.tpl searchterm=searchterm, hits=hits, hit_limit=hit_limit, doc_types_present=doc_types_present
% else:
	% include invalidquery.tpl searchterm=searchterm
% end

% include BOTTOM.tpl
