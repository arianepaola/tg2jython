from tg.environment import make_load_environment
from formstutorial.config.app_cfg import base_config

#Use base_config to setup the environment loader function
load_environment = base_config.make_load_environment()
