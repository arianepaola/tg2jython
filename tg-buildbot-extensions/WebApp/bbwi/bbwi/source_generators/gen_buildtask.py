from common import indent

class GenerateBuildTask:
    def __init__(self,build_task,b_function=False,**kwargs):
        self.indentation_level = 0
        self.b_func = b_function
        self.build_task = build_task
        if 'parameter' in kwargs and b_function:
            self.parameter = kwargs['parameter']
        else:
            self.parameter = []
    
    def convert_build_step(self,build_step):
        parameters = ""
        for k,v in build_step.parameter.iteritems():
            if v != "True" and v != "False" and v not in self.parameter:
                parameters = parameters + "%s=\"%s\"," %(k,v)
            else:
                parameters = parameters + "%s=%s," %(k,v)
        parameters = parameters[:-1]
        if parameters == "":
            form_string = "f.addStep(%s%s)\n"
        else:
            form_string = "f.addStep(%s,%s)\n"
            
        return indent(self.indentation_level) + form_string \
                %(build_step.name,parameters)
        
    def generate_source(self):
        temp = ["def %s:\n" % self.build_task.name]
        self.indentation_level = self.indentation_level + 1
        temp.append(indent(self.indentation_level)+"f = BuildFactory()\n")
        for step in self.build_task.build_steps:
            temp.append(self.convert_build_step(step))
        temp.append(indent(self.indentation_level) + "return f\n\n")
        self.indentation_level = 0
        return temp