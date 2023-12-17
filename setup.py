from __future__ import print_function
from distutils.core import setup
import os

PLUGIN_DIR = 'Extensions.MeteoForeca'

def compile_translate():
	for lang in os.listdir('po'):
		if lang.endswith('.po'):
			src = os.path.join('po', lang)
			lang = lang[:-3]
			destdir = os.path.join('src/locale', lang, 'LC_MESSAGES')
			if not os.path.exists(destdir):
				os.makedirs(destdir)
			dest = os.path.join(destdir, 'MeteoForeca.mo')
			print("Language compile %s -> %s" % (src, dest))
			if os.system("msgfmt '%s' -o '%s'" % (src, dest)) != 0:
				raise RuntimeError("Failed to compile", src)

compile_translate()

setup(name = 'enigma2-plugin-extensions-accuweather',
		version='1.0',
		author='Vasiliks',
		author_email='vasiliks73@gmail.com',
		package_dir = {PLUGIN_DIR: 'src'},
		packages=[PLUGIN_DIR],
		package_data={PLUGIN_DIR: ['images/*','images/*/*', 'skins/*', 'svg/*']},
		description = 'MeteoForeca Forecast plugin',
	)
