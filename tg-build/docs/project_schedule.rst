===========================================
Project schedule: TurboGears QA initiative
===========================================

:Author: Steven Mohr
:Date: $Date: 2008-07-27 16:23:33 -0300 (Sun, 27 Jul 2008) $
:Revision: $Rev: 5043 $
:Status: Draft

.. contents:: Table of Contents


Project description
-------------------

The goal of the project is to create a system enviroment which automates the
core tests and the creation of new TurboGears eggs. It should also create eggs
for the dependencies. The second goal was to install
SVNChecker and to configure it. This goal was replaced by the
creation of a webinterface which should be used to create new build tasks.
SVN Checker will be installed after Google Summer of Code.


Participants
------------

- Steven Mohr (implementation)
- Christopher Arndt (administrative)


Deliverables
------------

- Configured build master (image or archive)
- Configured slaves for

  * WinXP
  * Win2k(3)
  * WinVista
  * openSolaris(x86)
  * Linux(x86, x86_64)
  * (MacOS)

- Documentation of buildbot system
- Configured SVNChecker
- Documentation of SVNChecker installation


Milestones
----------

1. Configuration of the build master
2. Configuration of build slaves
3. Creation of BuildBot webinterface  


Packages milestone 1
--------------------

1. Creating buildfactory TG 1.0
2. Creating buildfactory TG 1.1
3. Creating buildfactory TG 2.0
4. Creating buildfactory for dependencies


Packages milestone 2
---------------------

1. Basic design of a slave
2. Basic config for unix-like OS
3. Creation of slaves for Ubuntu (x86 + x86_64) and Solaris
4. Documentation of unix slaves
5. Basic config for win OS
6. Creation of slaves for windows 2k,2k3, XP und Vista
7. Documentation of windows slaves

Packages milestone 3
--------------------


Meetings
--------

Project status meetings take place every monday at 6pm via Jabber.


Time table
----------

+------------+----------------------------------------------------------+----------------+
| Date       | Description                                              | Milestone      |
+============+==========================================================+================+
|    6.06.   | Basic design of a slave + finishing build master         | 1 + 2.1        |
+------------+----------------------------------------------------------+----------------+
|    11.06.  | Basic config for unix-like OS                            | 2.2            |
+------------+----------------------------------------------------------+----------------+
|    25.06.  | Creation of slaves for Ubuntu (x86 + x86_64) and Solaris | 2.3            |
+------------+----------------------------------------------------------+----------------+
|    3.07.   | Basic config for win OS                                  | 2.5            |
+------------+----------------------------------------------------------+----------------+
|    17.07.  | Creation of slaves for windows 2k,2k3, XP und Vista      | 2.6            |
+------------+----------------------------------------------------------+----------------+
|    12.07.  | Creation of BuildBot webinterface                        | 3              |
+------------+----------------------------------------------------------+----------------+
|            |                                                          |                |
+------------+----------------------------------------------------------+----------------+


References
----------

- Design document: TurboGears QA initiative (``design_document.rst``)
- Steven's blog: http://stevenmohr.wordpress.com
