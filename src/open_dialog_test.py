# Copyright 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import db_test_base
import dyn_object
import open_dialog
import message_loop
import settings
import tempfile
import temporary_daemon
import ui_test_case

class OpenDialogTest(ui_test_case.UITestCase):
  def setUp(self):
    self.db_test_base = db_test_base.DBTestBase()
    self.db_test_base.setUp()
    self.daemon = temporary_daemon.TemporaryDaemon()
    self.client_settings_file = tempfile.NamedTemporaryFile()
    self.client_settings = settings.Settings(self.client_settings_file.name)
    self.db = self.daemon.db_proxy
    self.db.add_dir(self.db_test_base.test_data_dir)
    self.options = dyn_object.DynObject()
    self.options.ok = True

  def tearDown(self):
    self.client_settings_file.close()
    self.daemon.close()
    self.db_test_base.tearDown()

  def test_open_dialog(self):
    x = open_dialog.OpenDialog(self.client_settings, self.options, self.db)
    def timeout():
      x.destroy()
      message_loop.quit_main_loop()
    message_loop.post_delayed_task(timeout, 3)
