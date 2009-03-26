"""
dbmechanic Module

this contains a turbogears controller which allows the user to have a 
phpMyAdmin *cringe*-like interface.  It is intended to be a replacement
for Catwalk

Classes:
Name                               Description
DBMechanic

Exceptions:
None

Functions:
None

Copywrite (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
from tw.api import CSSLink, Link

#register all the resources in the static directory
dbMechanicCss = CSSLink(modname='dbsprockets', filename='dbmechanic/static/css/dbmechanic.css')
dbMechanicFooterImg = Link(modname='dbsprockets', filename='dbmechanic/static/images/tg_under_the_hood.png')