# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of Stalker and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import datetime
import unittest
from sqlalchemy import Column, ForeignKey

from stalker.conf import defaults
from stalker.db.session import DBSession
from stalker.errors import CircularDependencyError
from stalker import (SimpleEntity, Entity, TaskableEntity, Project, Repository,
                     StatusList, Status, Task, Type, User)

class SomeClass(TaskableEntity):
    pass

class SomeOtherClass(object):
    pass

class TestClass(SimpleEntity):
    __tablename__ = "TestClasses"
    testClass_id = Column("id", ForeignKey("SimpleEntities.id"),
                          primary_key=True)
    #tasks = 
        
class TaskTester(unittest.TestCase):
    """Tests the stalker.models.task.Task class
    """
    
    @classmethod
    def setUpClass(cls):
        """set up tests in class level
        """
        DBSession.remove()
    
    def setUp(self):
        """setup the test
        """
        self.test_data_status_wip = Status(
            name="Work In Progress",
            code="WIP"
        )
        
        self.test_data_status_complete = Status(
            name="Complete",
            code="CMPLT"
        )
        
        self.test_data_status_pending_review = Status(
            name="Pending Review",
            code="PNDR"
        )
        
        self.test_data_task_status_list = StatusList(
            name="Task Statuses",
            statuses=[self.test_data_status_wip,
                      self.test_data_status_pending_review,
                      self.test_data_status_complete],
            target_entity_type=Task,
        )

        self.test_data_project_status_list = StatusList(
            name="Project Statuses",
            statuses=[self.test_data_status_wip,
                      self.test_data_status_pending_review,
                      self.test_data_status_complete],
            target_entity_type=Project,
        )

        self.test_data_movie_project_type = Type(
            name="Movie Project",
            code='movie',
            target_entity_type=Project,
        )

        self.test_data_test_repository_type = Type(
            name="Test Repository Type",
            code='test',
            target_entity_type=Repository,
        )

        self.test_data_test_repository = Repository(
            name="Test Repository",
            type=self.test_data_test_repository_type
        )

        self.test_data_project1 = Project(
            name="Test Project1",
            code='tp1',
            type=self.test_data_movie_project_type,
            status_list=self.test_data_project_status_list,
            repository=self.test_data_test_repository
        )

        self.test_data_user1 = User(
            name="User1",
            login="user1",
            email="user1@user1.com",
            password="1234"
        )

        self.test_data_user2 = User(
            name="User2",
            login="user2",
            email="user2@user2.com",
            password="1234"
        )

        self.test_data_dependent_task1 = Task(
            name="Dependent Task1",
            task_of=self.test_data_project1,
            status_list=self.test_data_task_status_list,
        )

        self.test_data_dependent_task2 = Task(
            name="Dependent Task2",
            task_of=self.test_data_project1,
            status_list=self.test_data_task_status_list,
        )

        # for task_of attribute tests
        self.test_data_simpleEntity = SimpleEntity(
            name="Test SimpleEntity",
        )

        self.mock_entity = Entity(
            name="Test Entity"
        )

        self.kwargs = {
            "name": "Modeling",
            "description": "A Modeling Task",
            "parent": self.test_data_project1,
            "priority": 500,
            "resources": [self.test_data_user1, self.test_data_user2],
            "effort": datetime.timedelta(4),
            "duration": datetime.timedelta(2),
            "depends": [self.test_data_dependent_task1,
                        self.test_data_dependent_task2],
            "is_complete": False,
            "bookings": [],
            "versions": [],
            "is_milestone": False,
            "status": 0,
            "status_list": self.test_data_task_status_list,
        }

        # create a test Task
        self.test_data_task = Task(**self.kwargs)
    
    def test___auto_name__class_attribute_is_set_to_False(self):
        """testing if the __auto_name__ class attribute is set to False for
        Task class
        """
        self.assertFalse(Task.__auto_name__)
    
    def test_priority_argument_is_skipped_defaults_to_DEFAULT_TASK_PRIORITY(
    self):
        """testing if skipping the priority argument will default the priority
        attribute to DEFAULT_TASK_PRIORITY.
        """
        self.kwargs.pop("priority")
        new_task = Task(**self.kwargs)
        self.assertEqual(new_task.priority, defaults.DEFAULT_TASK_PRIORITY)

    def test_priority_argument_is_given_as_None_will_default_to_DEFAULT_TASK_PRIORITY(
    self):
        """testing if the priority argument is given as None will default the
        priority attribute to DEFAULT_TASK_PRIORITY.
        """
        self.kwargs["priority"] = None
        new_task = Task(**self.kwargs)
        self.assertEqual(new_task.priority, defaults.DEFAULT_TASK_PRIORITY)

    def test_priority_attribute_is_given_as_None_will_default_to_DEFAULT_TASK_PRIORITY(
    self):
        """testing if the priority attribute is given as None will default the
        priority attribute to DEFAULT_TASK_PRIORITY.
        """
        self.test_data_task.priority = None
        self.assertEqual(self.test_data_task.priority,
                         defaults.DEFAULT_TASK_PRIORITY)

    def test_priority_argument_any_given_other_value_then_integer_will_default_to_DEFAULT_TASK_PRIORITY(self):
        """testing if any other value then an positif integer for priority
        argument will default the priority attribute to DEFAULT_TASK_PRIORITY.
        """
        test_values = ["a324", None, []]

        for test_value in test_values:
            self.kwargs["priority"] = test_value
            new_task = Task(**self.kwargs)
            self.assertEqual(new_task.priority, defaults.DEFAULT_TASK_PRIORITY)

    def test_priority_attribute_any_given_other_value_then_integer_will_default_to_DEFAULT_TASK_PRIORITY(self):
        """testing if any other value then an positif integer for priority
        attribute will default it to DEFAULT_TASK_PRIORITY.
        """
        test_values = ["a324", None, []]

        for test_value in test_values:
            self.test_data_task.priority = test_value
            self.assertEqual(self.test_data_task.priority,
                             defaults.DEFAULT_TASK_PRIORITY)

    def test_priority_argument_is_negative(self):
        """testing if the priority argument is given as a negative value will
        set the priority attribute to zero.
        """
        self.kwargs["priority"] = -1
        new_task = Task(**self.kwargs)
        self.assertEqual(new_task.priority, 0)

    def test_priority_attribute_is_negative(self):
        """testing if the priority attribute is given as a negative value will
        set the priority attribute to zero.
        """
        self.test_data_task.priority = -1
        self.assertEqual(self.test_data_task.priority, 0)

    def test_priority_argument_is_too_big(self):
        """testing if the priority argument is given bigger then 1000 will
        clamp the priority attribute value to 1000
        """
        self.kwargs["priority"] = 1001
        new_task = Task(**self.kwargs)
        self.assertEqual(new_task.priority, 1000)

    def test_priority_attribute_is_too_big(self):
        """testing if the priority attribute is set to a value bigger than 1000
        will clamp the value to 1000
        """
        self.test_data_task.priority = 1001
        self.assertEqual(self.test_data_task.priority, 1000)

    def test_priority_argument_is_float(self):
        """testing if float numbers for prority argument will be converted to
        integer
        """
        test_values = [500.1, 334.23]
        for test_value in test_values:
            self.kwargs["priority"] = test_value
            new_task = Task(**self.kwargs)
            self.assertEqual(new_task.priority, int(test_value))

    def test_priority_attribute_is_float(self):
        """testing if float numbers for priority attribute will be converted to
        integer
        """
        test_values = [500.1, 334.23]
        for test_value in test_values:
            self.test_data_task.priority = test_value
            self.assertEqual(self.test_data_task.priority, int(test_value))

    def test_priority_attribute_is_working_properly(self):
        """testing if the priority attribute is working properly
        """
        test_value = 234
        self.test_data_task.priority = test_value
        self.assertEqual(self.test_data_task.priority, test_value)

    def test_resources_argument_is_skipped(self):
        """testing if the resources attribute will be an empty list when the
        resources argument is skipped
        """
        self.kwargs.pop("resources")
        new_task = Task(**self.kwargs)
        self.assertEqual(new_task.resources, [])

    def test_resources_argument_is_None(self):
        """testing if the resources attribute will be an empty list when the
        resources argument is None
        """
        self.kwargs["resources"] = None
        new_task = Task(**self.kwargs)
        self.assertEqual(new_task.resources, [])

    def test_resources_attribute_is_None(self):
        """testing if a TypeError will be raised whe the resources attribute
        is set to None
        """
        self.assertRaises(TypeError, setattr, self.test_data_task,
                          "resources", None)

    def test_resources_argument_is_not_list(self):
        """testing if a TypeError will be raised when the resources argument is
        not a list
        """
        self.kwargs["resources"] = "a resource"
        self.assertRaises(TypeError, Task, **self.kwargs)

    def test_resources_attribute_is_not_list(self):
        """testing if a TypeError will be raised when the resources attribute
        is set to any other value then a list
        """
        self.assertRaises(TypeError, setattr, self.test_data_task, "resources",
                          "a resource")

    def test_resources_argument_is_set_to_a_list_of_other_values_then_User(self):
        """testing if a TypeError will be raised when the resources argument is
        set to a list of other values then a User
        """
        self.kwargs["resources"] = ["a", "list", "of", "resources",
                                    self.test_data_user1]
        self.assertRaises(TypeError, Task, **self.kwargs)

    def test_resources_attribute_is_set_to_a_list_of_other_values_then_User(self):
        """testing if a TypeError will be raised when the resources attribute
        is set to a list of other values then a User
        """
        self.kwargs["resources"] = ["a", "list", "of", "resources",
                                    self.test_data_user1]
        self.assertRaises(TypeError, self.test_data_task, **self.kwargs)

    def test_resources_attribute_is_working_properly(self):
        """testing if the resources attribute is working properly
        """
        test_value = [self.test_data_user1]
        self.test_data_task.resources = test_value
        self.assertEqual(self.test_data_task.resources, test_value)

    def test_resources_argument_backreferences_to_User(self):
        """testing if the User instances passed with the resources argument
        will have the current task in their User.tasks attribute
        """
        # create a couple of new users
        new_user1 = User(
            name="test1",
            login="test1",
            email="test1@test.com",
            password="test1"
        )

        new_user2 = User(
            name="test2",
            login="test2",
            email="test2@test.com",
            password="test2"
        )

        # assign it to a newly created task
        self.kwargs["resources"] = [new_user1]
        new_task = Task(**self.kwargs)

        # now check if the user has the task in its tasks list
        self.assertIn(new_task, new_user1.tasks)

        # now change the resources list
        new_task.resources = [new_user2]
        self.assertIn(new_task, new_user2.tasks)
        self.assertNotIn(new_task, new_user1.tasks)

        # now append the new resource
        new_task.resources.append(new_user1)
        self.assertIn(new_task, new_user1.tasks)

    def test_resources_attribute_backreferences_to_User(self):
        """testing if the User instances passed with the resources argument
        will have the current task in their User.tasks attribute
        """
        # create a new user
        new_user = User(
            name="Test User",
            login="testuser",
            email="testuser@test.com",
            password="testpass"
        )

        # assign it to a newly created task
        #self.kwargs["resources"] = [new_user]
        new_task = Task(**self.kwargs)
        new_task.resources = [new_user]

        # now check if the user has the task in its tasks list
        self.assertIn(new_task, new_user.tasks)

    def test_resources_attribute_will_clear_itself_from_the_previous_Users(
    self):
        """testing if the resources attribute is updated will clear itself from
        the current resources tasks attribute.
        """
        # create a couple of new users
        new_user1 = User(
            name="Test User1",
            login="testuser1",
            email="testuser1@test.com",
            password="testpass"
        )

        new_user2 = User(
            name="Test User2",
            login="testuser2",
            email="testuser2@test.com",
            password="testpass"
        )

        new_user3 = User(
            name="Test User3",
            login="testuser3",
            email="testuser3@test.com",
            password="testpass"
        )

        new_user4 = User(
            name="Test User4",
            login="testuser4",
            email="testuser4@test.com",
            password="testpass"
        )

        # now add the 1 and 2 to the resources with the resources argument
        # assign it to a newly created task
        self.kwargs["resources"] = [new_user1, new_user2]
        new_task = Task(**self.kwargs)

        # now check if the user has the task in its tasks list
        self.assertIn(new_task, new_user1.tasks)
        self.assertIn(new_task, new_user2.tasks)

        # now update the resources list
        new_task.resources = [new_user3, new_user4]

        # now check if the new resources has the task in their tasks attribute
        self.assertIn(new_task, new_user3.tasks)
        self.assertIn(new_task, new_user4.tasks)

        # and if it is not in the previous users tasks
        self.assertNotIn(new_task, new_user1.tasks)
        self.assertNotIn(new_task, new_user2.tasks)

    def test_resources_attribute_will_handle_append(self):
        """testing if the resources attribute will handle appending users
        """
        # create a couple of new users
        new_user1 = User(
            name="Test User1",
            login="testuser1",
            email="testuser1@test.com",
            password="testpass"
        )
        
        new_user2 = User(
            name="Test User2",
            login="testuser2",
            email="testuser2@test.com",
            password="testpass"
        )
        
        new_user3 = User(
            name="Test User3",
            login="testuser3",
            email="testuser3@test.com",
            password="testpass"
        )
        
        new_user4 = User(
            name="Test User4",
            login="testuser4",
            email="testuser4@test.com",
            password="testpass"
        )

        # now add the 1 and 2 to the resources with the resources argument
        # assign it to a newly created task
        self.kwargs["resources"] = [new_user1, new_user2]
        new_task = Task(**self.kwargs)

        # now check if the user has the task in its tasks list
        self.assertIn(new_task, new_user1.tasks)
        self.assertIn(new_task, new_user2.tasks)

        # now update the resources list
        new_task.resources.append(new_user3)
        new_task.resources.append(new_user4)

        # now check if the new resources has the task in their tasks attribute
        self.assertIn(new_task, new_user3.tasks)
        self.assertIn(new_task, new_user4.tasks)

    def test_resources_attribute_will_handle_extend(self):
        """testing if the resources attribute will handle extendeding users
        """
        # create a couple of new users
        new_user1 = User(
            name="Test User1",
            login="testuser1",
            email="testuser1@test.com",
            password="testpass"
        )
        
        new_user2 = User(
            name="Test User2",
            login="testuser2",
            email="testuser2@test.com",
            password="testpass"
        )
        
        new_user3 = User(
            name="Test User3",
            login="testuser3",
            email="testuser3@test.com",
            password="testpass"
        )
        
        new_user4 = User(
            name="Test User4",
            login="testuser4",
            email="testuser4@test.com",
            password="testpass"
        )
        
        # now add the 1 and 2 to the resources with the resources argument
        # assign it to a newly created task
        self.kwargs["resources"] = [new_user1, new_user2]
        new_task = Task(**self.kwargs)

        # now check if the user has the task in its tasks list
        self.assertIn(new_task, new_user1.tasks)
        self.assertIn(new_task, new_user2.tasks)

        # now update the resources list
        new_task.resources.extend([new_user3, new_user4])

        # now check if the new resources has the task in their tasks attribute
        self.assertIn(new_task, new_user3.tasks)
        self.assertIn(new_task, new_user4.tasks)

    def test_resources_attribute_will_handle___setitem__(self):
        """testing if the resources attribute will handle __setitem__ing users
        """
        # create a couple of new users
        new_user1 = User(
            name="Test User1",
            login="testuser1",
            email="testuser1@test.com",
            password="testpass"
        )
        
        new_user2 = User(
            name="Test User2",
            login="testuser2",
            email="testuser2@test.com",
            password="testpass"
        )
        
        new_user3 = User(
            name="Test User3",
            login="testuser3",
            email="testuser3@test.com",
            password="testpass"
        )
        
        new_user4 = User(
            name="Test User4",
            login="testuser4",
            email="testuser4@test.com",
            password="testpass"
        )
        
        # now add the 1 and 2 to the resources with the resources argument
        # assign it to a newly created task
        self.kwargs["resources"] = [new_user1, new_user2]
        new_task = Task(**self.kwargs)

        # now check if the user has the task in its tasks list
        self.assertIn(new_task, new_user1.tasks)
        self.assertIn(new_task, new_user2.tasks)

        # now update the resources list
        new_task.resources[0] = new_user3
        new_task.resources[1] = new_user4

        # now check if the new resources has the task in their tasks attribute
        self.assertIn(new_task, new_user3.tasks)
        self.assertIn(new_task, new_user4.tasks)

        # and check if the first and second tasks doesn't have task anymore
        self.assertNotIn(new_task, new_user1.tasks)
        self.assertNotIn(new_task, new_user2.tasks)

    def test_resources_attribute_will_handle___setslice__(self):
        """testing if the resources attribute will handle __setslice__ing users
        """
        # create a couple of new users
        new_user1 = User(
            name="Test User1",
            login="testuser1",
            email="testuser1@test.com",
            password="testpass"
        )
        
        new_user2 = User(
            name="Test User2",
            login="testuser2",
            email="testuser2@test.com",
            password="testpass"
        )
        
        new_user3 = User(
            name="Test User3",
            login="testuser3",
            email="testuser3@test.com",
            password="testpass"
        )

        new_user4 = User(
            name="Test User4",
            login="testuser4",
            email="testuser4@test.com",
            password="testpass"
        )
       
        # now add the 1 and 2 to the resources with the resources argument
        # assign it to a newly created task
        self.kwargs["resources"] = [new_user1, new_user2]
        new_task = Task(**self.kwargs)

        # now check if the user has the task in its tasks list
        self.assertIn(new_task, new_user1.tasks)
        self.assertIn(new_task, new_user2.tasks)

        # now update the resources list
        new_task.resources[1:2] = [new_user3, new_user4]

        # now check if the new resources has the task in their tasks attribute
        self.assertIn(new_task, new_user1.tasks)
        self.assertIn(new_task, new_user3.tasks)
        self.assertIn(new_task, new_user4.tasks)

        # and check if the first and second tasks doesn't have task anymore
        self.assertNotIn(new_task, new_user2.tasks)

    def test_resources_attribute_will_handle_insert(self):
        """testing if the resources attribute will handle inserting users
        """
        # create a couple of new users
        new_user1 = User(
            name="Test User1",
            login="testuser1",
            email="testuser1@test.com",
            password="testpass"
        )
        
        new_user2 = User(
            name="Test User2",
            login="testuser2",
            email="testuser2@test.com",
            password="testpass"
        )
        
        new_user3 = User(
            name="Test User3",
            login="testuser3",
            email="testuser3@test.com",
            password="testpass"
        )

        new_user4 = User(
            name="Test User4",
            login="testuser4",
            email="testuser4@test.com",
            password="testpass"
        )
        
        # now add the 1 and 2 to the resources with the resources argument
        # assign it to a newly created task
        self.kwargs["resources"] = [new_user1, new_user2]
        new_task = Task(**self.kwargs)

        # now check if the user has the task in its tasks list
        self.assertIn(new_task, new_user1.tasks)
        self.assertIn(new_task, new_user2.tasks)

        # now update the resources list
        new_task.resources.insert(0, new_user3)
        new_task.resources.insert(0, new_user4)

        # now check if the new resources has the task in their tasks attribute
        self.assertIn(new_task, new_user1.tasks)
        self.assertIn(new_task, new_user2.tasks)
        self.assertIn(new_task, new_user3.tasks)
        self.assertIn(new_task, new_user4.tasks)

    def test_resources_attribute_will_handle___add__(self):
        """testing if the resources attribute will handle __add__ing users
        """
        # create a couple of new users
        new_user1 = User(
            name="Test User1",
            login="testuser1",
            email="testuser1@test.com",
            password="testpass"
        )
        
        new_user2 = User(
            name="Test User2",
            login="testuser2",
            email="testuser2@test.com",
            password="testpass"
        )
        
        new_user3 = User(
            name="Test User3",
            login="testuser3",
            email="testuser3@test.com",
            password="testpass"
        )

        new_user4 = User(
            name="Test User4",
            login="testuser4",
            email="testuser4@test.com",
            password="testpass"
        )
        
        # now add the 1 and 2 to the resources with the resources argument
        # assign it to a newly created task
        self.kwargs["resources"] = [new_user1, new_user2]
        new_task = Task(**self.kwargs)

        # now check if the user has the task in its tasks list
        self.assertIn(new_task, new_user1.tasks)
        self.assertIn(new_task, new_user2.tasks)

        # now update the resources list
        new_task.resources = new_task.resources + [new_user3, new_user4]

        # now check if the new resources has the task in their tasks attribute
        self.assertIn(new_task, new_user1.tasks)
        self.assertIn(new_task, new_user2.tasks)
        self.assertIn(new_task, new_user3.tasks)
        self.assertIn(new_task, new_user4.tasks)

    def test_resources_attribute_will_handle___iadd__(self):
        """testing if the resources attribute will handle __iadd__ing users
        """
        # create a couple of new users
        new_user1 = User(
            name="Test User1",
            login="testuser1",
            email="testuser1@test.com",
            password="testpass"
        )

        new_user2 = User(
            name="Test User2",
            login="testuser2",
            email="testuser2@test.com",
            password="testpass")

        new_user3 = User(
            name="Test User3",
            login="testuser3",
            email="testuser3@test.com",
            password="testpass")

        new_user4 = User(
            name="Test User4",
            login="testuser4",
            email="testuser4@test.com",
            password="testpass"
        )

        # now add the 1 and 2 to the resources with the resources argument
        # assign it to a newly created task
        self.kwargs["resources"] = [new_user1, new_user2]
        new_task = Task(**self.kwargs)

        # now check if the user has the task in its tasks list
        self.assertIn(new_task, new_user1.tasks)
        self.assertIn(new_task, new_user2.tasks)

        # now update the resources list
        new_task.resources += [new_user3, new_user4]

        # now check if the new resources has the task in their tasks attribute
        self.assertIn(new_task, new_user1.tasks)
        self.assertIn(new_task, new_user2.tasks)
        self.assertIn(new_task, new_user3.tasks)
        self.assertIn(new_task, new_user4.tasks)

    def test_resources_attribute_will_handle_pop(self):
        """testing if the resources attribute will handle popping users
        """
        # create a couple of new users
        new_user1 = User(
            name="Test User1",
            login="testuser1",
            email="testuser1@test.com",
            password="testpass"
        )
        
        new_user2 = User(
            name="Test User2",
            login="testuser2",
            email="testuser2@test.com",
            password="testpass"
        )

        # now add the 1 and 2 to the resources with the resources argument
        # assign it to a newly created task
        self.kwargs["resources"] = [new_user1, new_user2]
        new_task = Task(**self.kwargs)

        # now check if the user has the task in its tasks list
        self.assertIn(new_task, new_user1.tasks)
        self.assertIn(new_task, new_user2.tasks)

        # now pop the resources
        new_task.resources.pop(0)
        self.assertNotIn(new_task, new_user1.tasks)

        new_task.resources.pop()
        self.assertNotIn(new_task, new_user2.tasks)

    def test_resources_attribute_will_handle_remove(self):
        """testing if the resources attribute will handle removing users
        """
        # create a couple of new users
        new_user1 = User(
            name="Test User1",
            login="testuser1",
            email="testuser1@test.com",
            password="testpass"
        )
        
        new_user2 = User(
            name="Test User2",
            login="testuser2",
            email="testuser2@test.com",
            password="testpass"
        )

        # now add the 1 and 2 to the resources with the resources argument
        # assign it to a newly created task
        self.kwargs["resources"] = [new_user1, new_user2]
        new_task = Task(**self.kwargs)

        # now check if the user has the task in its tasks list
        self.assertIn(new_task, new_user1.tasks)
        self.assertIn(new_task, new_user2.tasks)

        # now pop the resources
        new_task.resources.remove(new_user1)
        self.assertNotIn(new_task, new_user1.tasks)

        new_task.resources.remove(new_user2)
        self.assertNotIn(new_task, new_user2.tasks)
    
    def testing_resources_attribute_will_be_an_empty_list_for_a_container_Task(self):
        """testing if the resources attribute will be an empty list for a
        container Task
        """
        self.fail('test is not implemented yet')
    
    def testing_resources_attribute_will_not_append_any_data_to_itself_for_a_container_Task(self):
        """testing if the resources attribute will not append any data to
        itself for a container Task
        """
        self.fail('test is not implemented yet')
    
    def test_effort_and_duration_argument_is_skipped(self):
        """testing if the effort attribute is set to the default value of
        duration divided by the number of resources
        """
        self.kwargs.pop("effort")
        self.kwargs.pop("duration")

        new_task = Task(**self.kwargs)

        self.assertEqual(new_task.duration, defaults.DEFAULT_TASK_DURATION)
        self.assertEqual(new_task.effort, defaults.DEFAULT_TASK_DURATION *
                                          len(new_task.resources))

    def test_effort_argument_skipped_but_duration_is_present(self):
        """testing if the effort argument is skipped but the duration is
        present the effort attribute is calculated from the
        duration * len(resources) formula
        """
        self.kwargs.pop("effort")
        new_task = Task(**self.kwargs)

        self.assertEqual(new_task.duration, self.kwargs["duration"])
        self.assertEqual(new_task.effort, new_task.duration *
                                          len(new_task.resources))

    def test_effort_argument_present_but_duration_is_skipped(self):
        """testing if the effort argument is present but the duration is
        skipped the duration attribute is calculated from the
        effort / len(resources) formula
        """
        self.kwargs.pop("duration")
        new_task = Task(**self.kwargs)

        self.assertEqual(new_task.effort, self.kwargs["effort"])
        self.assertEqual(new_task.duration, new_task.effort /
                                            len(new_task.resources))

    def test_effort_and_duration_argument_is_None(self):
        """testing if the effort and duration is None then effort will be
        calculated from the value of duration and count of resources
        """
        self.kwargs["effort"] = None
        self.kwargs["duration"] = None
        new_task = Task(**self.kwargs)
        self.assertEqual(new_task.duration, defaults.DEFAULT_TASK_DURATION)
        self.assertEqual(new_task.effort, new_task.duration *
                                          len(new_task.resources))

    def test_effort_attribute_is_set_to_None(self):
        """testing if the effort attribute is set to None then the effort is
        calculated from duration and count of resources
        """
        self.test_data_task.effort = None
        self.assertEqual(self.test_data_task.effort,
                         self.test_data_task.duration *
                         len(self.test_data_task.resources))

    def test_effort_argument_is_not_an_instance_of_timedelta(self):
        """testing if effort attribute is calculated from the duration
        attribute when the effort argument is not an instance of timedelta
        """
        self.kwargs["effort"] = "not a timedelta"
        new_task = Task(**self.kwargs)
        self.assertIsInstance(new_task.effort, datetime.timedelta)
        self.assertEqual(new_task.effort, new_task.duration *
                                          len(new_task.resources))

    def test_effort_attribute_is_not_an_instance_of_timedelta(self):
        """testing if effort attribute is calculated from the duration
        attribute when it is set to something else then a timedelta instance.
        """
        self.test_data_task.effort = "not a timedelta"
        self.assertIsInstance(self.test_data_task.effort, datetime.timedelta)
        self.assertEqual(self.test_data_task.effort,
                         self.test_data_task.duration *
                         len(self.test_data_task.resources))

    def test_effort_attribute_is_working_properly(self):
        """testing if the effort attribute is working properly
        """
        test_value = datetime.timedelta(18)
        self.test_data_task.effort = test_value
        self.assertEqual(self.test_data_task.effort, test_value)

    def test_effort_argument_preceeds_duration_argument(self):
        """testing if the effort argument is preceeds duration argument 
        """
        self.kwargs["effort"] = datetime.timedelta(40)
        self.kwargs["duration"] = datetime.timedelta(2)

        new_task = Task(**self.kwargs)

        self.assertEqual(new_task.effort, self.kwargs["effort"])
        self.assertEqual(new_task.duration, self.kwargs["effort"] /
                                            len(self.kwargs["resources"]))

    def test_effort_attribute_changes_duration(self):
        """testing if the effort attribute changes the duration
        """
        test_effort = datetime.timedelta(100)
        test_duration = test_effort / len(self.test_data_task.resources)

        # be sure it is not already in the current value
        self.assertNotEqual(self.test_data_task.duration, test_duration)

        self.test_data_task.effort = test_effort

        self.assertEqual(self.test_data_task.duration, test_duration)

    def test_duration_attribute_changes_effort(self):
        """testing if the duration attribute changes the effort attribute value
        by the effort = duration / len(resources) formula
        """
        test_duration = datetime.timedelta(100)
        test_effort = test_duration * len(self.test_data_task.resources)

        # be sure it is not already in the current value
        self.assertNotEqual(self.test_data_task.effort, test_effort)
        self.test_data_task.duration = test_duration
        self.assertEqual(self.test_data_task.effort, test_effort)

    def test_duration_attribute_will_be_equal_to_effort_if_there_is_no_resources_argument(self):
        """testing if the duration will be equal to the effort if there is no
        resource assigned
        """
        self.kwargs.pop("resources")
        new_task = Task(**self.kwargs)

        self.assertEqual(new_task.effort, self.kwargs["effort"])
        self.assertEqual(new_task.effort, new_task.duration)

    def test_depends_argument_is_skipped_depends_attribute_is_empty_list(self):
        """testing if the depends attribute is an empty list when the depends
        argument is skipped
        """
        self.kwargs.pop("depends")
        new_task = Task(**self.kwargs)
        self.assertEqual(new_task.depends, [])

    def test_depends_argument_is_none_depends_attribute_is_empty_list(self):
        """testing if the depends attribute is an empty list when the depends
        argument is None
        """
        self.kwargs["depends"] = None
        new_task = Task(**self.kwargs)
        self.assertEqual(new_task.depends, [])

    def test_depends_argument_is_not_a_list(self):
        """testing if a TypeError will be raised when the depends argument is
        not a list
        """
        self.kwargs["depends"] = self.test_data_dependent_task1
        self.assertRaises(TypeError, Task, **self.kwargs)

    def test_depends_attribute_is_not_a_list(self):
        """testing if a TypeError will be raised when the depends attribute is
        set to something else then a list
        """
        self.assertRaises(TypeError, setattr, self.test_data_task, "depends",
                          self.test_data_dependent_task1)

    def test_depends_argument_is_a_list_of_other_objects_than_a_Task(self):
        """testing if a TypeError will be raised when the depends argument is
        a list of other typed objects than Task
        """
        test_value = ["a", "dependent", "task", 1, 1.2]
        self.kwargs["depends"] = test_value
        self.assertRaises(TypeError, Task, **self.kwargs)

    def test_depends_attribute_is_a_list_of_other_objects_than_a_Task(self):
        """testing if a TypeError will be raised when the depends attribute is
        set to a list of other typed objects than Task
        """
        test_value = ["a", "dependent", "task", 1, 1.2]
        self.assertRaises(TypeError, setattr, self.test_data_task, "depends",
                          test_value)

    #def test_depends_argument_shifts_the_start_date_by_traversing_dependency_list(self):
        #"""testing if the depends argument shifts the start_date attribute by
        #traversing the dependent tasks list and placing the current task after
        #the latest dependent task
        #"""
        #self.fail("test is not implemented yet")

    #def test_depends_attribute_shifts_the_start_date_by_traversing_dependency_list(self):
        #"""testing if the depends attribute shifts the start_date attribute by
        #traversing the dependent tasks list
        #"""
        #self.fail("test is not implemented yet")

    def test_depends_attribute_doesnt_allow_simple_cyclic_dependencies(self):
        """testing if a CircularDependencyError will be raised when the depends
        attribute has a simple circular dependency in dependencies
        """
        # create two new tasks A, B
        # make B dependent to A
        # and make A dependent to B
        # and expect a CircularDependencyError
        self.kwargs["depends"] = None

        taskA = Task(**self.kwargs)
        taskB = Task(**self.kwargs)

        taskB.depends = [taskA]

        self.assertRaises(CircularDependencyError, setattr, taskA, "depends",
            [taskB])

    def test_depends_attribute_doesnt_allow_cyclic_dependencies(self):
        """testing if a CircularDependencyError will be raised when the depends
        attribute has a circular dependency in dependencies
        """
        # create three new tasks A, B, C
        # make B dependent to A
        # make C dependent to B
        # and make A dependent to C
        # and expect a CircularDependencyError
        self.kwargs["depends"] = None

        self.kwargs["name"] = "taskA"
        taskA = Task(**self.kwargs)

        self.kwargs["name"] = "taskB"
        taskB = Task(**self.kwargs)

        self.kwargs["name"] = "taskC"
        taskC = Task(**self.kwargs)

        taskB.depends = [taskA]
        taskC.depends = [taskB]

        self.assertRaises(CircularDependencyError, setattr, taskA, "depends",
            [taskC])

    def test_depends_attribute_doesnt_allow_more_deeper_cyclic_dependencies(self):
        """testing if a CircularDependencyError will be raised when the depends
        attribute has a deeper circular dependency in dependencies
        """
        # create new tasks A, B, C, D
        # make B dependent to A
        # make C dependent to B
        # make D dependent to C
        # and make A dependent to D
        # and expect a CircularDependencyError
        self.kwargs["depends"] = None

        self.kwargs["name"] = "taskA"
        taskA = Task(**self.kwargs)
        self.kwargs["name"] = "taskB"
        taskB = Task(**self.kwargs)
        self.kwargs["name"] = "taskC"
        taskC = Task(**self.kwargs)
        self.kwargs["name"] = "taskD"
        taskD = Task(**self.kwargs)

        taskB.depends = [taskA]
        taskC.depends = [taskB]
        taskD.depends = [taskC]

        self.assertRaises(CircularDependencyError, setattr, taskA, "depends",
            [taskD])

    def test_is_complete_attribute_is_None(self):
        """testing if the is_complete attribute will be False when set to None
        """
        self.test_data_task.is_complete = None
        self.assertEqual(self.test_data_task.is_complete, False)

    def test_is_complete_attribute_evaluates_the_given_value_to_a_bool(self):
        """testing if the is_complete attribute is evaluated correctly to a bool
        value when set to anything other than a bool value.
        """
        test_values = [1, 0, 1.2, "A string", "", [], [1]]
        for test_value in test_values:
            self.test_data_task.is_complete = test_value
            self.assertEqual(self.test_data_task.is_complete, bool(test_value))

    def test_is_milestone_argument_is_skipped(self):
        """testing if the default value of the is_milestone attribute is going
        to be False when the is_milestone argument is skipped
        """
        self.kwargs.pop("is_milestone")
        new_task = Task(**self.kwargs)
        self.assertEqual(new_task.is_milestone, False)


    def test_is_milestone_argument_is_None(self):
        """testing if the is_milestone attribute will be set to False when the
        is_milestone argument is given as None
        """
        self.kwargs["is_milestone"] = None
        new_task = Task(**self.kwargs)
        self.assertEqual(new_task.is_milestone, False)

    def test_is_milestone_attribute_is_None(self):
        """testing if the is_milestone attribute will be False when set to None
        """
        self.test_data_task.is_milestone = None
        self.assertEqual(self.test_data_task.is_milestone, False)

    def test_is_milestone_argument_evaluates_the_given_value_to_a_bool(self):
        """testing if the is_milestone attribute is evaluated correctly to a
        bool value when the is_milestone argument is anything other than a bool
        value.
        """
        test_values = [1, 0, 1.2, "A string", "", [], [1]]
        for i, test_value in enumerate(test_values):
            self.kwargs["name"] = "test" + str(i)
            self.kwargs["is_milestone"] = test_value
            new_task = Task(**self.kwargs)
            self.assertEqual(new_task.is_milestone, bool(test_value))

    def test_is_milestone_attribute_evaluates_the_given_value_to_a_bool(self):
        """testing if the is_milestone attribute is evaluated correctly to a
        bool value when set to anything other than a bool value.
        """
        test_values = [1, 0, 1.2, "A string", "", [], [1]]
        for test_value in test_values:
            self.test_data_task.is_milestone = test_value
            self.assertEqual(self.test_data_task.is_milestone, bool(test_value))

    def test_is_milestone_argument_makes_the_resources_list_an_empty_list(self):
        """testing if the resources will be an empty list when the is_milestone
        argument is given as True
        """
        self.kwargs["is_milestone"] = True
        self.kwargs["resources"] = [self.test_data_user1,
                                    self.test_data_user2]
        new_task = Task(**self.kwargs)
        self.assertEqual(new_task.resources, [])

    def test_is_milestone_attribute_makes_the_resource_list_an_empty_list(self):
        """testing if the resources will be an empty list when the is_milestone
        attribute is given as True
        """
        self.test_data_task.resources = [self.test_data_user1,
                                         self.test_data_user2]
        self.test_data_task.is_milestone = True
        self.assertEqual(self.test_data_task.resources, [])

    
    #def test_bookings_argument_is_skipped(self):
        #"""testing if the bookings attribute will be an empty list when the
        #bookings argument is skipped
        #"""
        #self.kwargs.pop("bookings")
        #new_task = Task(**self.kwargs)
        #self.assertEqual(new_task.bookings, [])

    #def test_bookings_argument_is_None(self):
        #"""testing if the booking attribute will be an empty list when the
        #bookings argument is None
        #"""
        #self.fail("test is not implemented yet")

    def test_bookings_attribute_is_None(self):
        """testing if a TypeError will be raised when the bookings attribute
        is set to None
        """
        self.assertRaises(TypeError, setattr, self.test_data_task, "bookings",
                          None)

    #def test_bookings_argument_is_not_a_list(self):
        #"""testing if a TypeError will be raised when the bookings argument is
        #not a list
        #"""
        #self.fail("test is not implemented yet")

    def test_bookings_attribute_is_not_a_list(self):
        """testing if a TypeError will be raised when the bookings attribute is
        not set to a list
        """
        self.assertRaises(TypeError, setattr, self.test_data_task, "bookings",
                          123)

    #def test_bookings_argument_is_not_a_list_of_Booking_instances(self):
        #"""testing if a TypeError will be raised when the bookings argument is
        #not a list of Booking instances
        #"""
        #self.fail("test is not implemented yet")

    def test_bookings_attribute_is_not_a_list_of_Booking_instances(self):
        """testing if a TypeError will be raised when the bookings attribute is
        not a list of Booking instances
        """
        self.assertRaises(TypeError, setattr, self.test_data_task, "bookings",
            [1, "1", 1.2, "a booking", []])

    #def test_versions_argument_is_skipped(self):
        #"""testing if the versions attribute will be an empty list when the
        #versions argument is skipped
        #"""
        #self.fail("test is not implemented yet")

    #def test_versions_argument_is_None(self):
        #"""testing if the versions attribute will be an empty list when the
        #versions argument is None
        #"""
        #self.fail("test is not implemented yet")

    def test_versions_attribute_is_None(self):
        """testing if a TypeError will be raised when the versions attribute
        is set to None
        """
        self.assertRaises(TypeError, setattr, self.test_data_task, "versions",
                          None)

    #def test_versions_argument_is_not_a_list(self):
        #"""testing if a TypeError will be raised when the versions argument is
        #not a list
        #"""
        #self.fail("test is not implemented yet")

    def test_versions_attribute_is_not_a_list(self):
        """testing if a TypeError will be raised when the versions attribute is
        set to a value other than a list
        """
        self.assertRaises(TypeError, setattr, self.test_data_task, "versions",
                          1)
        
    #def test_versions_argument_is_not_a_list_of_Version_instances(self):
        #"""testing if a TypeError will be raised when the versions argument is
        #a list of other objects than Version instances
        #"""
        #self.fail("test is not implemented yet")

    def test_versions_attribute_is_not_a_list_of_Version_instances(self):
        """testing if a TypeError will be raised when the versions attribute is
        set to a list of other objects than Version instances
        """

        self.assertRaises(TypeError, setattr, self.test_data_task, "versions",
            [1, 1.2, "a version"])

    #def test_parent_task_argument_is_skiped(self):
        #"""testing if the parent_task attribute will be None when the
        #parent_task argument is skipped.
        #"""
        #self.fail("test is not implemented yet")

    #def test_parent_task_argument_is_None(self):
        #"""testing if the parent_task attribute will be None when the
        #parent_task argument is None
        #"""
        #self.fail("test is not implemented yet")

    #def test_parent_task_attribute_is_set_to_None(self):
        #"""testing if the parent_task attribute will be None when it is set to
        #None.
        #"""
        #self.fail("test is not implemented yet")

    #def test_parent_task_argument_is_not_a_Task_instance(self):
        #"""testing if a TypeError will be raised when the parent_task argument
        #is not a Task instance
        #"""
        #self.fail("test is not implemented yet")

    #def test_parent_task_attribute_is_not_a_Task_instance(self):
        #"""testing if a TypeError will be raised when the parent_task argument
        #is not a Task instance
        #"""
        #self.fail("test is not implemented yet")
    
    #def test_parent_task_argument_is_a_Task_instance(self):
        #"""testing if the Task given with the parent_task argument will have
        #the new task in its sub_tasks attribute
        #"""
        #self.fail("test is not implemented yet")

    #def test_parent_task_attribute_is_a_Task_instance(self):
        #"""testing if the Task given with the parent_task attribute will have
        #the current task in its sub_tasks attribute
        #"""
        #self.fail("test is not implemented yet")

    def test_equality(self):
        """testing the equality operator
        """
        entity1 = Entity(**self.kwargs)
        task1 = Task(**self.kwargs)

        self.assertFalse(self.test_data_task == entity1)
        self.assertTrue(self.test_data_task == task1)

    def test_inequality(self):
        """testing the inequality operator
        """
        entity1 = Entity(**self.kwargs)
        task1 = Task(**self.kwargs)

        self.assertTrue(self.test_data_task != entity1)
        self.assertFalse(self.test_data_task != task1)
    
    def test_parent_argument_is_skipped(self):
        """testing if the Task is still be able to be created without a parent
        """
        self.fail('test is not implemented yet')
    
    def test_parent_argument_is_None(self):
        """testing if the task is still be able to be created without a parent
        """
        self.fail('test is not implemented yet')
    
    def test_parent_attribute_is_set_to_None(self):
        """testing if the parent attribute can be set to None
        """
        self.fail('test is not implemented yet')
    
    def  test_parent_argument_is_not_a_Task_instance(self):
        """testing if a TypeError will be raised when the parent argument is
        not a Task instance
        """
        self.fail('test is not implemented yet')
    
    def test_parent_attribute_is_not_a_Task_instance(self):
        """testing if a TypeError will be raised when the parent attribute is
        not a Task instance
        """
        self.fail('test is not implemented yet')
    
    # there is no way to generate a CycleError by using the parent argument,
    # cause the Task is just created, it is not in relationship with other
    # Tasks, there is no parent nor child.
    
    def test_parent_attribute_creates_a_cycle(self):
        """testing if a CycleError will be raised if a child class is tried to
        be set as a parent.
        """
        self.fail('test is not implemented yet')
    
    def test_parent_argument_is_working_properly(self):
        """testing if the parent argument is working properly
        """
        self.fail('test is not implemented yet')
    
    def test_parent_attribute_is_working_properly(self):
        """testing if the parent attribute is working properly
        """
        self.fail('test is not implemented yet')
    
    def test_children_attribute_is_empty_list_by_default(self):
        """testing if the children attribute is an empty list by default
        """
        self.fail('test is not implemented yet')
    
    def test_children_attribute_is_set_to_None(self):
        """testing if a TypeError will be raised when the children attribute is
        set to None
        """
        self.fail('test is not implemented yet')
    
    def test_children_attribute_accepts_Tasks_only(self):
        """testing if a TypeError will be raised when the item assigned to the
        children attribute is not a Task instance
        """
        self.fail('test is not implemented yet')
    
    def test_children_attribute_is_working_properly(self):
        """testing if the children attribute is working properly
        """
        self.fail('test is not implemented yet')
    
    def test_is_leaf_attribute_is_read_only(self):
        """testing if the is_leaf attribute is a read only attribute
        """
        self.fail('test is not implemented yet')
    
    def test_is_leaf_attribute_is_working_properly(self):
        """testing if the is_leaf attribute is True for a Task without a child
        Task and False for Task with at least one child Task
        """
        self.fail('test is not implemented yet')
    
    def test_is_container_attribute_is_read_only(self):
        """testing if the is_container attribute is a read only attribute
        """
        self.fail('test is not implemented yet')
    
    def test_is_container_attribute_working_properly(self):
        """testing if the is_container attribute is True for a Task with at
        least one child Task and False for a Task with no child Task
        """
        self.fail('test is not implemented yet')
    
    def test_project_attribute_is_a_read_only_attribute(self):
        """testing if the project attribute is a read only attribute
        """
        self.assertRaises(AttributeError, setattr, self.test_data_task,
                          'project', self.test_data_project1)
    
    def test_project_attribute_returns_task_of_project_attribute(self):
        """testing if the project attribute returns the Task.task_of.project
        value
        """
        self.assertEquals(self.test_data_task.project,
                          self.test_data_task.task_of.project)
    
    def test_start_date_attribute_value_of_a_container_task_is_defined_by_its_child_tasks(self):
        """testing if the start_date attribute value is defined by the earliest
        start date of the children Tasks for a container Task
        """
        self.fail('test is not implemented yet')
    
    def test_start_date_attribute_value_doesnt_change_for_a_container_Task(self):
        """testing if the start_date attribute doesn't change when it is set to
        another value for a container Task.
        """
        self.fail('test is not implemented yet')
    
    def test_end_date_attribute_value_of_a_container_task_is_defined_by_its_child_tasks(self):
        """testing if the end_date attribute value is defined by the latest
        end date value of the children Tasks for a container Task.
        """
        self.fail('test is not implemented yet')
    
    def test_end_date_attribute_value_doesnt_change_for_a_container_Task(self):
        """testing if the end_date attribute doesn't change when it is set to
        another value for a container Task.
        """
        self.fail('test is not implemented yet')
