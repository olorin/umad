		<div id="searchbox">

			<form name="q" method="get" action="/" 
% if searchterm:
				onSubmit="evilSearchedAgain()"
% end
			>
				<table id="searchform"><tr>
					<td class="umadlogo-td"><a href="/?q=mad"><img src="/static/img/umad.png" class="umadlogo" style="border:0;" alt="UMAD logo"></a></td><td><input type="search" id="searchinput" name="q" placeholder="UMAD?" value="{{ searchterm }}" autofocus="autofocus"></td><td><input type="submit" id="searchbutton" class="lsf" value="search"></td>
				</tr></table>
			</form>

			<div id="search-toggles">
				% for doc_type in doc_types_present:
				<div class="doc-type {{ doc_type[1] }}" title="Dismiss all {{ doc_type[0] }}" onClick="javascript:killResultsMatchingClass('{{ doc_type[1] }}');"> {{ doc_type[0] }} <span class="right">✘</span> </div>
				% end
			</div>
		</div> <!-- END searchbox -->
