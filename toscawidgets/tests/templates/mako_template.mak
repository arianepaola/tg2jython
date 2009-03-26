<%page args="id=''" />
<table id="${id}">
	% for row in rows:
		${makerow(row)}
	% endfor
</table>
   
<%def name="makerow(row)">
	<tr>
	% for name in row:
		<td>${name}</td>
	% endfor
	</tr>
</%def>
