/* forms.js */

function load_param_form() {
    var bs_type_select = $('select_buildsteps');
    name = bs_type_select.value;
    var d = loadJSONDoc('/buildtasks/add_bs?type=' + name);
    d.addCallbacks(show_param_form, json_error);
}

function json_error() {
    alert("Error in loadJSONDoc.");
}

function show_param_form(result) {
    var div = $('param_form_div');
    div.innerHTML = result['form'];
    connect("param_form_submit", 'onclick', submit_parameter);
}

function submit_parameter() {
    var params = formContents('param_form');
    var d = loadJSONDoc('/buildtasks/insert_bs?' + queryString(params[0], params[1]));
    d.addCallbacks(update_overview,json_error) ;
    connect("finish_bt", 'onclick', finish_buildtask);
}

function update_overview(result) {
	var div = $('overview_div');
    div.innerHTML = result['form'];
    
}

function finish_buildtask() {
  var field = $('bt_name') ;
  var d = loadJSONDoc('/buildtasks/finish_bt?'+'bt_name='+field.value);
  d.addErrback(json_error) ;
}