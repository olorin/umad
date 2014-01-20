% include TOP.tpl

% include searchbox.tpl searchterm=searchterm

% include motd.tpl searchterm=searchterm

% if valid_search_query:
	% include searchresults.tpl searchterm=searchterm, hits=hits, hit_limit=hit_limit
% else:
	% include invalidquery.tpl searchterm=searchterm
% end

% include BOTTOM.tpl
