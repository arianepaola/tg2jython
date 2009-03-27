import unittest

from bbwi.source_generators.gen_buildtask import GenerateBuildTask
from bbwi.model import BuildTask, BuildStep

def test():
    test_list = [BuildStep("EasyInstall",dict(workdir="build",test="all")),\
                     BuildStep("RunSetup",dict(devmode=True,test="all"))]
    b = BuildTask()
    b.set_name("Test")
    for step in test_list:
        b.add_step(step)
    
    g = GenerateBuildTask(b)

    assert g.convert_build_step(test_list[0]) == 'f.addStep(EasyInstall,test="all",workdir="build")'
    
    


