# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin
import octoprint.filemanager
import octoprint.filemanager.util
import requests

class WifisdsupportPlugin(octoprint.plugin.SettingsPlugin,
                          octoprint.plugin.TemplatePlugin):

  ##~~ SettingsPlugin mixin

  def __init__(self):
    self._serial_obj = None

  def get_settings_defaults(self):
    return dict(
      wifi_sd_ip = "flashair"
    )

  ##~~ TemplatePlugin mixin

  def get_template_configs(self):
    return [
      dict(type="settings", custom_bindings=False)
    ]

  ##~~ Softwareupdate hook

  def get_update_information(self):
    # Define the configuration for your plugin to use with the Software Update
    # Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
    # for details.
    return dict(
      WifiSdSupport=dict(
        displayName="WifiSdSupport Plugin",
        displayVersion=self._plugin_version,

        # version check: github repository
        type="github_release",
        user="MSmthng",
        repo="OctoPrint-WifiSdSupport",
        current=self._plugin_version,

        # update method: pip
        pip="https://github.com/MSmthng/OctoPrint-WifiSdSupport/archive/{target_version}.zip"
      )
    )

  def save_to_wifi_sd(self, path, file_object, links=None, printer_profile=None, allow_overwrite=True, *args, **kwargs):
    ip = self._settings.get(["wifi_sd_ip"])
    if ip:
      url = "http://" + ip + "/upload.cgi"
      self._logger.info("Attempt upload: " + url + " " + file_object.filename + " " + path)
      #upload file to sd card using wifi
      files = {'file': (file_object.filename, file_object.stream())}
      try:
        r = requests.post(url, files=files)
      except requests.exceptions.RequestException as e:
        self._logger.info("Connection Error: {}".format(e))
      else:
        self._logger.info("Response: " + r.text.replace('\r','').replace('\n',''))
    else:
      self._logger.info("Empty Wifi Sd Card IP")
    #refresh sd card files
    if self._printer.is_operational():
      self._printer.commands("M20")
    #return unmodified file object
    return file_object


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "WifiSdSupport Plugin"
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
  global __plugin_implementation__
  __plugin_implementation__ = WifisdsupportPlugin()

  global __plugin_hooks__
  __plugin_hooks__ = {
    "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
    "octoprint.filemanager.preprocessor"          : __plugin_implementation__.save_to_wifi_sd
  }

