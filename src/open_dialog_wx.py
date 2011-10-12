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
import time
import logging
import os
import wx
import wx.lib.mixins.listctrl  as  listmix
import wx.lib.evtmgr as evtmgr
import sys

from open_dialog import OpenDialogBase

class TestListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

class OpenDialogWx(wx.Dialog, OpenDialogBase):
  def __init__(self, settings, options, db):
    wx.Dialog.__init__(self, None, wx.ID_ANY, "Quick open...", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER, size=(1000,400))
    OpenDialogBase.__init__(self, settings, options, db)

    if wx.Platform == "__WXMAC__":
      wx.SystemOptions.SetOptionInt("mac.listctrl.always_use_generic", False)

    sizer = wx.BoxSizer(wx.VERTICAL)

    top_box = wx.BoxSizer(wx.HORIZONTAL)

    self.status_text = wx.StaticText(self, -1, '')

    top_box.Add((10,0))
    top_box.Add(self.status_text,1, wx.EXPAND | wx.ALL | wx.ALIGN_CENTER_VERTICAL)
    refresh_bn = wx.Button(self, -1, "Refresh")
    refresh_bn.Bind(wx.EVT_BUTTON, lambda *args: self.refresh())
    top_box.Add(refresh_bn)

    middle_box = wx.BoxSizer(wx.HORIZONTAL)
    self._results_list = TestListCtrl(self, -1,
                                      style=wx.LC_REPORT | wx.BORDER_NONE)

    middle_box.Add(self._results_list, 1, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND)

    filter_box = wx.BoxSizer(wx.HORIZONTAL)
    self._filter_ctrl = wx.TextCtrl(self, -1, self._filter_text)
    self.Bind(wx.EVT_CHAR_HOOK, self.on_evt_key_down)
    self.Bind(wx.EVT_TEXT, self.on_evt_text, self._filter_ctrl)
    self.Bind(wx.EVT_TEXT_ENTER, self.on_evt_text_enter, self._filter_ctrl)
    filter_box.Add(self._filter_ctrl, 1, wx.EXPAND)

    lower_sizer = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)

    sizer.Add(top_box, 0, wx.EXPAND|wx.BOTTOM, 8)
    sizer.Add(middle_box, 1, wx.GROW|wx.BOTTOM,8)
    sizer.Add(filter_box, 0, wx.GROW|wx.BOTTOM,7)
    sizer.Add(lower_sizer, 0, wx.ALIGN_RIGHT|wx.BOTTOM)

    outer_sizer = wx.BoxSizer(wx.VERTICAL)
    outer_sizer.Add(sizer, 1, wx.ALL | wx.EXPAND, 8)
    self.SetSizer(outer_sizer)

    self._filter_ctrl.SetFocus()


    self.CenterOnScreen()
    self.Show()

    ok = self.FindWindowById(wx.ID_OK)
    cancel = self.FindWindowById(wx.ID_CANCEL)
    ok.Bind(wx.EVT_BUTTON, self.on_ok)
    cancel.Bind(wx.EVT_BUTTON, self.on_cancel)
    
  def on_ok(self, event):
    self.on_done(False)

  def on_cancel(self, event):
    self.on_done(True)

  def set_status(self,status_text):
    self.status_text.SetLabel(status_text)

  def set_results_enabled(self,en):
    self._results_list.Enable(en)
    if not en:
      self._results_list.ClearAll()
    okbn = self.FindWindowById(wx.ID_OK)
    okbn.Enable(en)

  def on_evt_key_down(self,event):
    code = event.GetKeyCode()
    ctrl = event.ControlDown()
    if self.FindFocus() != self._results_list:
      if code == wx.WXK_UP:
        self.move_selection(-1)
        return
      elif code == wx.WXK_DOWN:
        self.move_selection(1)
        return
    event.Skip()

  def on_evt_text(self,event):
    self.set_filter_text(self._filter_ctrl.GetValue())

  def on_evt_text_enter(self, event):
    self.EndModal(wx.ID_OK)

  def update_results_list(self, files, ranks):
    self._cur_results = files
    self._results_list.ClearAll()
    self._results_list.InsertColumn(0, "Rank")
    self._results_list.InsertColumn(1, "File")
    self._results_list.InsertColumn(2, "Path")
    for i in range(len(files)):
      f = files[i]
      r = ranks[i]
      base = os.path.basename(f)
      path = os.path.dirname(f)
      i = self._results_list.InsertStringItem(sys.maxint, str(r))
      self._results_list.SetStringItem(i, 1, base)
      self._results_list.SetStringItem(i, 2, path)

    if len(files):
      self._results_list.SetItemState(0, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
    c1w = 200
    self._results_list.SetColumnWidth(0, 20)
    self._results_list.SetColumnWidth(1, 200)
    self._results_list.SetColumnWidth(2, self._results_list.GetSize()[0] - c1w)

  def move_selection(self, direction):
    if direction > 0:
      cur = self.get_selected_index(favor_topmost=False)
    else:
      cur = self.get_selected_index(favor_topmost=True)

    if cur == -1:
      return
    next = cur + direction
    N = self._results_list.GetItemCount()
    if next < 0:
      next = 0
    elif next >= N:
      next = N -1
    self._results_list.SetItemState(cur, 0, wx.LIST_STATE_SELECTED)
    self._results_list.SetItemState(next, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
    self._results_list.EnsureVisible(next)

  def get_selected_index(self, favor_topmost=True):
    cur = self.get_selected_indices()
    if len(cur) > 1:
      # clear all selections
      for i in cur:
        self._results_list.SetItemState(i, 0, wx.LIST_STATE_SELECTED)

      # pick the topmost
      if favor_topmost:
        self._results_list.SetItemState(cur[0], wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
      else:
        self._results_list.SetItemState(cur[-1], wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

    return self._results_list.GetNextSelected(-1)

  def get_selected_indices(self):
    all = []
    cur = -1
    while True:
      cur = self._results_list.GetNextSelected(cur)
      if cur == -1:
        break
      all.append(cur)
    return all

  def get_selected_items(self):
    return map(lambda i: self._cur_results[i], self.get_selected_indices())

if __name__ == "__main__":
  # KNOWN BROKEN by work to integrate with message_loop
  import db_test_base
  import settings
  import tempfile
  import temporary_daemon

  db_test_base = db_test_base.DBTestBase()
  db_test_base.setUp()
  daemon = temporary_daemon.TemporaryDaemon()
  client_settings_file = tempfile.NamedTemporaryFile()
  client_settings = settings.Settings(client_settings_file.name)
  db = daemon.db_proxy
  db.add_dir(db_test_base.test_data_dir)
  run(client_settings, db)
  db_test_base.tearDown()
  client_settings_file.close()
