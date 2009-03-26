import os, sys, os.path
import pkg_resources

from routes import url_for
from sqlalchemy.orm import sessionmaker, scoped_session
from tg.tests.base import TestWSGIController, make_app
from webob import Request, Response
from paste.deploy import loadapp
from paste.fixture import TestApp
from pprint import pprint
from nose.tools import eq_

app = None

def setup():
    global app
    here_dir = os.path.dirname(os.path.abspath(__file__))
    proj_dir = os.path.join(here_dir, 'TG2TestApp')
    
    pkg_resources.working_set.add_entry(proj_dir)

    from tg2testapp.model import DBSession, metadata, User, Group
    app = loadapp('config:development.ini', relative_to=proj_dir)
    app = TestApp(app)
    metadata.drop_all()
    metadata.create_all()

    session = DBSession
    user = User()
    user.user_name = u'asdf'
    user.email = u"asdf@asdf.com"
    user.password = u"asdf"
    
    session.save(user)
    
    for i in range (50):
        group = Group()
        group.group_name=unicode(i)
        session.save(group)
        user.groups.append(group)

    session.save(user)
    session.commit()
    session.flush()
    
def teardown():
    from tg2testapp.model import User, Group, DBSession as session, metadata
    del metadata

class TestDBMechanic:
    def setup(self):
        from tg2testapp.model import users_table, user_group_table, groups_table
        users_table.delete().execute()
        groups_table.delete().execute()
        user_group_table.delete().execute()
        
    def testDatabaseView(self):
        resp = app.get('/dbmechanic')
        s =  resp.body
        assert """<div class="tablelabelwidget">
<a href="/dbmechanic/tableView/town_table">town_table</a>
</div>
<input type="hidden" name="dbsprockets_id" class="hiddenfield" id="databaseView_dbsprockets_id" value="test_tabletg_grouppermissionvisituser_groupvisit_identitygroup_permissiontg_usertown_table">
</div>
      </div>
      <div class="mainView" style="bg-color:#ffffff;">
      </div>
<!--  <div py:for="js in tg_js_bodybottom" py:replace="ET(js.display())" />-->
  <!-- End of main_content -->
  </div>
  <div id="footer">
       <p>TurboGears 2 is a open source front-to-back web development framework written in Python</p>
       <p>Copyright (c) 2005-2008 </p>
  </div>
</body>
</html>""" in s, "actual: %s"%s
    
    def testTableDef(self):
        resp = app.get('/dbmechanic/tableDef/tg_user')
        value =  resp.body
        assert """<tr class="tabledefwidget">
    <td>
        created
    </td>
    <td>
    DateTime(timezone=False)
    </td>
</tr>
<input type="hidden" name="dbsprockets_id" class="hiddenfield" id="tableDef__tg_user_dbsprockets_id" value="">
</table>
      </div>""" in value, value
        
    def testTableView(self):
        from tg2testapp.model import User, Group, DBSession as session
        u = User()
        u.user_name=u'userTableView'
        u.password = u'asdf'
        u.email_address=u"asdftableView@asdf.com"
        session.save(u)
        group = Group()
        group.group_name=u"table_view_group"
        group.display_name=u"group"
        session.save(group)
        session.flush()
        
        resp = app.get('/dbmechanic/tableView/tg_user')
        value =  resp.body
        assert """<thead>
        <tr>
            <th class="col_0">
            </th><th class="col_1">
            user_id
            </th><th class="col_2">
            user_name
            </th><th class="col_3">
            email_address
            </th><th class="col_4">
            display_name
            </th><th class="col_5">
            password
            </th><th class="col_6">
            town
            </th><th class="col_7">
            created
            </th><th class="col_8">
            tg_groups
            </th>
        </tr>
    </thead>
    <tbody>
        <tr class="even">
            <td><a href="/dbmechanic/editRecord/tg_user?user_id=1">"""
        """edit</a>|<a href="/dbmechanic/delete/tg_user?user_id=1">delete</a></td><td>1</td><td>user2</td>"""
        """<td></td><td></td><td>******</td><td>""" in value, value
        
    def testAddRecord(self):
        resp = app.get('/dbmechanic/addRecord/tg_user')
        value =  resp.body
        assert """<td>
                <div>
    <input type="text" id="addRecord__tg_user_created" class="dbsprocketscalendardatetimepicker" name="created" value="2007-12-21 19:02:25" />
    <input type="button" id="addRecord__tg_user_created_trigger" class="date_field_button" value="Choose" />
</div>
            </td>
        </tr><tr class="even">
            <th>
            </th>
            <td>
                <input type="submit" class="submitbutton" id="addRecord__tg_user_submit" value="Submit" />
            </td>
        </tr>
    </table>"""
        
    def testEditRecord(self):
        from tg2testapp.model import User, Group, DBSession as session
        u = User()
        u.user_name=u'user3'
        u.password = u'asdf'
        u.email_address=u"asdf@asdf2.com"
        session.save(u)
        group = Group()
        group.group_name=u"table_view_group"
        group.display_name=u"group"
        session.save(group)
        session.flush()
        resp = app.get('/dbmechanic/editRecord/tg_user?user_id=1')
        value =  resp.body
        assert """<td>
                <div>
    <input type="text" id="editRecord__tg_user_created" class="dbsprocketscalendardatetimepicker" name="created" value="2007-12-21 20:45:00" />
    <input type="button" id="editRecord__tg_user_created_trigger" class="date_field_button" value="Choose" />
</div>
            </td>
        </tr><tr class="even">
            <th>
            </th>
            <td>
                <input type="submit" class="submitbutton" id="editRecord__tg_user_submit" value="Submit" />
            </td>
        </tr>
    </table>
</form>"""

#cant test this until we can do it properly through paste
    def testAdd(self):
        resp = app.get('/dbmechanic/addRecord/tg_user')
        value =  resp.body
        resp = app.get('/dbmechanic/add/tg_user', params=dict(user_id=None,
                                                              user_name=u'new_user',
                                                              email_address=u'new@user.com',
                                                              dbsprockets_id=u'addRecord__tg_user'))
        #actual =  resp.follow().namespace
        actual = resp.namespace
#        eq_({}, value)
        
        expected = {'controller': '/dbmechanic', 
                    #'context': <paste.registry.StackedObjectProxy object at 0x2225f90>, 
                    #'recordsPerPage': 25, 
                    'tableName': 'tg_user', 
                    #'mainCount': 1, 
                    #'page': 1
                    }
        mainValue ={u'town': None, 
                    u'user_id': 1, 
#                           u'created': datetime.datetime(2008, 2, 23, 11, 59, 35, 144897), 
                    u'email_address': u'new@user.com', 
                    'tg_groups': '', 
                    u'display_name': None, 
                    u'password': '******', 
                    u'user_name': u'new_user'}
        
        for key, value in expected.iteritems():
            yield eq_, value, actual[key]
        
        #actualRow = actual['mainValue'][0]

#        for key, value in mainValue.iteritems():
#            yield eq_, value, actualRow[key]

    def testEdit(self):
        from tg2testapp.model import User, Group, DBSession as session
        u = User()
        u.user_name=u'userTestEdit'
        u.password = u'asdf'
        u.email_address=u"test@edit.com"
        session.save(u)
        session.commit()
        session.flush()
        u_id = str(u.user_id)
        resp = app.get('/dbmechanic/editRecord/tg_user?user_id='+u_id)
        value =  resp.body
        resp = app.get('/dbmechanic/edit/tg_user', params=dict(user_id=u_id, 
                                                              user_name=u'new_username',
                                                              email_address=u'newemail@user.com',
                                                              dbsprockets_id=u'editRecord__tg_user'
                                                          ))
        actual =  resp.follow().namespace
        expected = {'controller': '/dbmechanic', 
                    'recordsPerPage': 25, 
                    'tableName': 'tg_user', 
                    'mainCount': 1, 
                    'page': 1}
        mainValue ={u'town': None, 
                    u'user_id': 1, 
#                           u'created': datetime.datetime(2008, 2, 23, 11, 59, 35, 144897), 
                    u'email_address': u'newemail@user.com', 
                    'tg_groups': '', 
                    u'display_name': None, 
                    u'password': '******', 
                    u'user_name': u'new_username'}
        
        for key, value in expected.iteritems():
            yield eq_, value, actual[key]
        actualRow = actual['mainValue'][0]

        for key, value in mainValue.iteritems():
            yield eq_, value, actualRow[key]
            
    def testCreateRelationships(self):
        from tg2testapp.model import User, Group, DBSession as session
        u = User()
        u.user_name=u'userCreateRel'
        u.password = u'asdf'
        u.email_address=u"create@relationships.com"
        session.save(u)
        session.commit()
        group = Group()
        group.group_name=u"create_rel_group"
        group.display_name=u"group"
        session.save(group)
        session.flush()
        u_id = str(u.user_id)
        #add group 1
        resp = app.get('/dbmechanic/edit/tg_user', params=dict(user_id=u_id, 
                                                        user_name=u'new_username',
                                                        email_address=u'newemail@user.com',
                                                        dbsprockets_id=u'editRecord__tg_user',
                                                        many_many_tg_group="1",
                                                          ))

    def testCreateRelationshipsManyMany(self):
        from tg2testapp.model import user_group_table
        user_group_table.insert(values=dict(user_id=1, group_id=2)).execute()
        resp = app.get('/dbmechanic/edit/user_group', params=dict(dbsprockets_id='editRecord__user_group', user_id=1, group_id=2))

    def testEdit(self):
        from tg2testapp.model import User, Group, DBSession as session
        u = User()
        u.user_name=u'userTestEdit'
        u.password = u'asdf'
        u.email_address=u"test@edit.com"
        session.save(u)
        session.commit()
        session.flush()
        u_id = str(u.user_id)
        resp = app.get('/dbmechanic/delete/tg_user?user_id='+u_id)
        
        
