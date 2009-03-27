<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
  <meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
  <title>Welcome to TurboGears</title>
  <script type="text/javascript" src="${tg.url('/static/javascript/forms.js')}"></script>
</head>
<body>

<p class="navbar"><a href="${tg.url('/')}">Start</a></p>

<p><label for="bt_name">Name of the build task:</label><input name="bt_name" id="bt_name" />  
<input type="button" value="Finish build task" id="finish_bt" /></p>
<div id="overview_div"></div>

  <select name="select_buildsteps" id="select_buildsteps">
    <option py:for="steps in buildsteps" py:content="steps.name">Name of BuildStep</option>
  </select>
  <input type="button" name="add_bs" value="New build step" onclick="load_param_form(); return false;" />
  <div id="param_form_div" />
</body>
</html>
