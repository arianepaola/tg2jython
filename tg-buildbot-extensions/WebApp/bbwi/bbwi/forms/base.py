#!/usr/bin/env python

__all__ = [
    'DynamicForm',
    'OverviewForm'
]

from turbogears import widgets

class DynamicForm(widgets.Widget):
    params = ['fields', 'submit_text', 'name', 'form_attrs','bs_type']
    fields = []
    submit_text = 'Save'
    form_attrs = {}
    name = 'DynamicForm'
    type =""
    
    template = """\
    <form xmlns:py="http://purl.org/kid/ns#"
      name="${name}"
      class="listform"
      py:attrs="form_attrs"
    >
    <input type="hidden" name="type" value="${bs_type}" />
      <table>
        <thead>
          <tr>
            <th>Parameter name</th>
            <th>Parameter value</th>
          </tr>
        </thead>
        <tbody>
          <tr py:for="i, field in enumerate(fields)"
                class="${i%2 and 'odd' or 'even'}">
            <td>
              <label class="fieldlabel" for="${'field_' + field}" py:content="field" />
            </td>
            <td>
              <input type="text" name="${field}" id="${'field_' + field}" />
              <span class="fielderror" id="${'error_' + field}" />
            </td>
          </tr>
          <tr colspan="2" class="buttonbox">
            <input type="button" value="${submit_text}" id="param_form_submit" />
          </tr>
        </tbody>
      </table>
    </form>
    """

class OverviewForm(widgets.Widget):
    params = ['fields', 'submit_text', 'name', 'form_attrs']
    fields = []
    submit_text = 'Save'
    form_attrs = {}
    name = 'OverviewForm'
    
    template = """\
    <form xmlns:py="http://purl.org/kid/ns#"
      name="${name}"
      class="listform"
      py:attrs="form_attrs"
    >
      <table class="buildstep_list">
  <thead>
    <tr>
     <th>Name of BuildStep</th>
     <th>List of parameter=value pairs</th>
     <th>Action</th>
    </tr>
  </thead>
  <tbody>
    <tr py:for="i, field in enumerate(fields)">
      <td>${field.name}</td>
      <td>${field.get_parameter_as_kv_pairs()}</td>
      <td>
        <a href="${tg.url('/create_bt/edit_bs?name='+str(i))}">Edit</a> 
        <a href="${tg.url('/create_bt/delete_bs?name='+str(i))}">Delete</a> 
      </td>
    </tr>
  </tbody>
</table>
    </form>
    """