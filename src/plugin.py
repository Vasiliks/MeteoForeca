# -*- coding: utf-8 -*-
# coded by Vasiliks 12.2023
import os
import csv
import json
import requests
from six import unichr, ensure_str
from enigma import addFont
from Components.ActionMap import ActionMap
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigText, configfile, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Language import language
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.ScrollLabel import ScrollLabel
from . import _, getSkin, ScreenWidth

# Set default configuration
MAIN_URL = "https://www.foreca.com"
Plugin_Path = os.path.dirname(os.path.realpath(__file__))
HEADERS = {'User-Agent': 'Mozilla/5.0 (SmartHub; SMART-TV; U; Linux/SmartTV; Maple2012) AppleWebKit/534.7 (KHTML, like Gecko) SmartTV Safari/534.7', 'Accept-Encoding': 'gzip, deflate'}
lang = language.getLanguage()[:2]
plugin_version = '1.0'
city_list = '/etc/enigma2/meteoforeca_city.json'
addFont(Plugin_Path + "/skins/Stylo_Bold.ttf", "MFRegular", 100, 1)


def write_log(value):
    with open("/tmp/meteoforeca.log", 'a') as f:
        f.write('%s\n' % value)


def show_svg(svg_file, svg):
    svg.instance.setScale(1)
    svg.instance.setPixmapFromFile(svg_file)
    svg.instance.show()


meteoforecacfg = config.plugins.meteoforeca = ConfigSubsection()

meteoforecacfg.city = ConfigText(default='100703448/Kyiv-Ukraine')

choices = [('c', _('Celsius')), ('f', _('Fahrenheit'))]
meteoforecacfg.temperature = ConfigSelection(default='c', choices=choices)
temperature_unit = {'c': ensure_str(unichr(176))+"C",
                    'f': ensure_str(unichr(176))+"F"}

choices = [('s', _('m/s')), ('kmh', _('km/h')),
           ('mph', _('Miles per hour')), ('bft', _('Beaufort'))]
meteoforecacfg.wind_speed = ConfigSelection(default='s', choices=choices)
wind_speed_unit = {'s': _('m/s'), 'kmh': _('km/h'), 'mph': _('mph'), 'bft': _('bft')}

choices = [('pres', _('hPa')), ('presmmhg', _('mmHg')), ('presinhg', _('inHg'))]
meteoforecacfg.pressure = ConfigSelection(default='presmmhg', choices=choices)
pressure_unit = {'pres': _('hPa'), 'presmmhg': _('mmHg'), 'presinhg': _('inHg')}

choices = [('mm', _('mm')), ('in', _('in'))]
meteoforecacfg.precipitation = ConfigSelection(default='mm', choices=choices)
precipitation_unit = {'mm': _('mm'), 'in': _('in')}


daily = {'0': _('MIDNIGHT'), '1': _('MORNING'), '2': _('AFTERNOON'), '3': _('EVENING')}


def download_json():
    URL = '{}/{}/{}/detailed-forecast'.format(MAIN_URL, lang, meteoforecacfg.city.value)
    req = requests.get(URL, headers=HEADERS).content.decode()
    fc = req[req.find('data: [{')+7:]
    city = fc.find("window.addRecent")
    ec = fc[city+17:]
    e = ec.find("});")
    h = ec[:e+1]
    FC = fc[:fc.find('}],')+1]
    g = ''
    j = 0
    for i in FC:
        if i == "{":
            i = i.replace("{", '"item' + str(j) + '": {')
            j += 1
        g += i
    g = '{ "items": %d, %s }' % (j, g)
    return json.loads(g), json.loads(h)


class MeteoForeca(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin = getSkin("MeteoForeca")
        self.setTitle(_("Enigma2 MeteoForeca  ver. %s") % plugin_version)
        self["key_red"] = Label(_("Exit"))
        self["key_blue"] = Label(_('Settings'))
        self["city"] = ScrollLabel()
        self.Day = 0

        for z in range(0, 4):
            self["date{}".format(z)] = Label()
            self["time{}".format(z)] = Label()
            self["wx{}".format(z)] = Label()
            self["symb{}".format(z)] = Pixmap()
            self["uvi{}".format(z)] = Pixmap()
            self["temperature{}".format(z)] = Label()
            self["flike{}".format(z)] = ScrollLabel()
            self["windspeed{}".format(z)] = Label()
            self["windgust{}".format(z)] = Label()
            self["windd{}".format(z)] = Pixmap()
            self["rhum{}".format(z)] = ScrollLabel()
            self["pres{}".format(z)] = ScrollLabel()
            self["rain{}".format(z)] = ScrollLabel()
            self["rainp{}".format(z)] = ScrollLabel()

        self['actions'] = ActionMap(["MeteoForecaActions"], {
            "cancel": self.cancel,
            "red": self.cancel,
            "blue": self.MeteoForecaconf,
            "ok": self.cancel,
            "left": self.keyLeft,
            "right": self.keyRight,
            "info": self.about,
            }, -1)
        self.onLayoutFinish.append(self.weather)

    def MeteoForecaconf(self):
        self.session.openWithCallback(self.weather, MeteoForecaConf)

    def weather(self):
        self.Forecast, info_city = download_json()
        info = _('Country :{}\n').format(info_city['countryName'])
        info += _('Location :{}\n').format(info_city['name'])
        info += _('Timezone :{}\n').format(info_city['timezone'])
        info += _('Longitude :{}\n').format(info_city['lon'])
        info += _('Latitude :{}\n').format(info_city['lat'])
        info += _('Elevation :{}\n').format(info_city['elevation'])
        self["city"].setText(info)
        self.MeteoForeca_Forecast()

    def MeteoForeca_Forecast(self):
        dt = self.Forecast.get("item0").get("time").split('T')[0]
        days = []
        period = []
        for i in range(0, self.Forecast.get("items")):
            item = "item" + str(i)
            date, time = self.Forecast.get(item).get("time").split('T')
            if date != dt:
                days.append(period)
                dt = date
                period = []
            period.append(item)
        days.append(period)
        z = 4 - len(days[self.Day])
        for y in days[self.Day]:
            one = self.Forecast.get(y)
            date, time = one.get("time").split('T')
            self["date{}".format(z)].setText(date)
            self["time{}".format(z)].setText(daily[str(z)])
            self["wx{}".format(z)].setText(one.get("wx"))
            self["temperature{}".format(z)].setText(str(one.get("temp" + meteoforecacfg.temperature.value.replace('c', ''))) + temperature_unit[meteoforecacfg.temperature.value])
            self["flike{}".format(z)].setText(_("Feels like ") + str(one.get("flike" + meteoforecacfg.temperature.value.replace('c', ''))) + temperature_unit[meteoforecacfg.temperature.value])
            self["pres{}".format(z)].setText(_("Pressure :") + str(one.get(meteoforecacfg.pressure.value)) + pressure_unit[meteoforecacfg.pressure.value])
            self["windspeed{}".format(z)].setText(str(one.get("winds" + meteoforecacfg.wind_speed.value.replace('s', ''))) + wind_speed_unit[meteoforecacfg.wind_speed.value])
            self["windgust{}".format(z)].setText(str(one.get("maxwind" + meteoforecacfg.wind_speed.value.replace('s', ''))) + wind_speed_unit[meteoforecacfg.wind_speed.value])
            show_svg("{}/svg/w{}.svg".format(Plugin_Path, one.get("windd")), self["windd{}".format(z)])
            show_svg("{}/svg/{}.svg".format(Plugin_Path, one.get("symb")), self["symb{}".format(z)])
            show_svg("{}/svg/uvi{}.svg".format(Plugin_Path, one.get("uvi")), self["uvi{}".format(z)])
            self["rhum{}".format(z)].setText(_("Relative humidity :") + str(one.get("rhum")) + "%")
            self["rain{}".format(z)].setText(_("Rain :") + str(one.get("rain" + meteoforecacfg.precipitation.value.replace('mm', ''))) + precipitation_unit[meteoforecacfg.precipitation.value])
            self["rainp{}".format(z)].setText(_("Precip chance :") + str(one.get("rainp")) + "%")
            z += 1

    def keyRight(self):
        self.Day += 1
        if self.Day > 13:
            self.Day = 0
            self.hide_all()
        self.MeteoForeca_Forecast()

    def keyLeft(self):
        self.Day -= 1
        if self.Day == 0:
            self.hide_all()
        if self.Day < 0:
            self.Day = 13
        self.MeteoForeca_Forecast()

    def hide_all(self):
        for z in range(0, 4):
            self["date{}".format(z)].setText("")
            self["time{}".format(z)].setText("")
            self["wx{}".format(z)].setText("")
            self["symb{}".format(z)].instance.hide()
            self["uvi{}".format(z)].instance.hide()
            self["temperature{}".format(z)].setText("")
            self["flike{}".format(z)].setText("")
            self["windspeed{}".format(z)].setText("")
            self["windgust{}".format(z)].setText("")
            self["windd{}".format(z)].instance.hide()
            self["rhum{}".format(z)].setText("")
            self["pres{}".format(z)].setText("")
            self["rain{}".format(z)].setText("")
            self["rainp{}".format(z)].setText("")

    def cancel(self):
        self.close()

    def about(self):
        self.session.open(MessageBox, _('MeteoForecaForecast\nEnigma2 plugin ver. %s\n©2023 Vasiliks') % plugin_version,
                          MessageBox.TYPE_INFO, simple=True)


class MeteoForecaConf(ConfigListScreen, Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.skin = getSkin("MeteoForecaConf")
        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label(_('Save'))
        self.setTitle(_('Settings'))
        ConfigListScreen.__init__(self, [
         getConfigListEntry(_('Temperature:'), meteoforecacfg.temperature),
         getConfigListEntry(_('Wind speed:'), meteoforecacfg.wind_speed),
         getConfigListEntry(_('Pressure:'), meteoforecacfg.pressure),
         getConfigListEntry(_('Precipitation:'), meteoforecacfg.precipitation),
         getConfigListEntry(_('City:'), meteoforecacfg.city)
         ])
        self['actions'] = ActionMap(["MeteoForecaActions"], {
            'ok': self.save, 'green': self.save,
            'cancel': self.exit, 'red': self.exit}, -2)

    def save(self):
        for x in self['config'].list:
            x[1].save()
        self.close()

    def exit(self):
        for x in self['config'].list:
            x[1].cancel()
        self.close()


def main(session, **kwargs):
    session.open(MeteoForeca)


def Plugins(**kwargs):
    icon = "images/foreca-logo.svg"
    return [
        PluginDescriptor(name=_("MeteoForeca"),
                         where=[PluginDescriptor.WHERE_PLUGINMENU],
                         description=_("MeteoForeca Plugin"),
                         icon=icon,
                         fnc=main)
    ]
