from tw.api import Widget
from tw.forms import CalendarDatePicker, CalendarDateTimePicker, TableForm
from tw.forms.fields import SingleSelectField, MultipleSelectField, InputField
from formencode.schema import Schema
from formencode.validators import Bool

class DBSprocketsCalendarDatePicker(CalendarDatePicker):
    date_format = '%Y-%m-%d'

class DBSprocketsTimePicker(CalendarDateTimePicker):
    date_format = '%H:%M:%S'

class DBSprocketsCalendarDateTimePicker(CalendarDateTimePicker):
    date_format = '%Y-%m-%d %H:%M:%S'

class ContainerWidget(Widget):
    template = "genshi:dbsprockets.widgets.templates.container"
    params = ["controller",]

class TableLabelWidget(Widget):
    template = "genshi:dbsprockets.widgets.templates.tableLabel"
    params = ["identifier", "controller"]
    
class RecordViewWidget(Widget):
    template = "genshi:dbsprockets.widgets.templates.recordViewTable"
    params = ["identifier"]

class RecordFieldWidget(Widget):
    template = "genshi:dbsprockets.widgets.templates.recordField"
    params = ['identifier', 'controller']

class TableDefWidget(Widget):
    template = "genshi:dbsprockets.widgets.templates.tableDef"
    params = ["identifier"]

class TableWidget(Widget):
    template = "genshi:dbsprockets.widgets.templates.table"
    
class DBSprocketsTableForm(TableForm):
    validator = Schema(ignore_missing_keys=True, allow_extra_fields=True)
    template = "genshi:dbsprockets.widgets.templates.tableForm"
    
    def update_params(self, d):
        super(DBSprocketsTableForm, self).update_params(d)
        
#custom checkbox widget since I am not happy with the behavior of the TW one
class DBSprocketsCheckBox(InputField):
    template = "genshi:dbsprockets.widgets.templates.checkbox"
    validator = Bool
    def update_params(self, d):
        InputField.update_params(self, d)
        try:
            checked = self.validator.to_python(d.value)
        except Invalid:
            checked = False
        d.attrs['checked'] = checked or None

class ForeignKeyMixin(Widget):
    params = ["tableName", "provider"]
    def _my_update_params(self, d,nullable=False):
        viewColumn = self.provider.getViewColumnName(self.tableName)
        idColumn = self.provider.getIDColumnName(self.tableName)
        rows = self.provider.select(self.tableName, columnsLimit=[idColumn, viewColumn])
        rows= [(row[idColumn], row[viewColumn]) for row in rows]
        if nullable:
            rows.append([None,"-----------"])
        if len(rows) == 0:
            return {}
        d['options']= rows
        
        return d
    
class ForeignKeySingleSelectField(SingleSelectField, ForeignKeyMixin):
    params=["nullable"]
    nullable=False
    def update_params(self, d):
        self._my_update_params(d,nullable=self.nullable)
        SingleSelectField.update_params(self, d)
        return d

class ForeignKeyMultipleSelectField(MultipleSelectField, ForeignKeyMixin):
    def update_params(self, d):
        self._my_update_params(d)
        MultipleSelectField.update_params(self, d)
        return d
