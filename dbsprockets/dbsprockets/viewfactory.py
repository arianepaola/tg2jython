#this might go away.

from view import View

class ViewFactory:
    def create(self, viewConfig, id=None):
        kw = viewConfig.getWidgetArgs()
        if id == None:
            id = viewConfig.__class__.__name__+'_'+viewConfig.identifier
        kw['id'] = id
        parentWidget = viewConfig.widgetType(**kw)
        return View(parentWidget, viewConfig)
