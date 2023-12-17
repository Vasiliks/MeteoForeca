# -*- coding: utf-8 -*-
# created by Vasiliks 11.2023

from gettext import bindtextdomain, dgettext
from os import environ, path
from enigma import getDesktop
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

try:
    import xml.etree.cElementTree as ETree
except ImportError:
    import xml.etree.ElementTree as ETree


def localeInit():
    environ["LANGUAGE"] = language.getLanguage()[:2]
    bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, "Extensions/MeteoForeca/locale"))


def _(txt):
    return (dgettext(PluginLanguageDomain, txt), '')[txt == '']


PluginLanguageDomain = "MeteoForeca"
ScreenWidth = 1280 if getDesktop(0).size().width() < 1920 else 1920
getFullPath = lambda fname: resolveFilename(SCOPE_PLUGINS, path.join('Extensions', PluginLanguageDomain, fname))
MeteoForeca_skin = ETree.parse(getFullPath('skins/svg.xml')).getroot()
getSkin = lambda skinName: ETree.tostring(MeteoForeca_skin.find('.//screen[@name="%s"]' % skinName), encoding='utf8', method='xml')
localeInit()
language.addCallback(localeInit)
