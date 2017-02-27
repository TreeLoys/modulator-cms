#!/usr/local/python27/python
# coding: utf-8
import os
import re
from sitemap import Sitemap

PATH_site_name = "http://chempion-santehnik.ru/"
PATH_module = "../www/module/"
PATH_site = "../www/site/"
PATH_site_out = "../www/"
ROBOT_TXT = ("User-agent:*\n"
"Disallow: /cgi-bin\n"
"Disallow: /site\n"
)
SITEMAP_all_update = "daily"
def file_read(path):
	f = open(path)
	t = f.read()
	f.close()
	return t
def file_write(path, text):
	f = open(path, "w")
	f.write(text)
	f.close()
	return True

#словарь модулей для поиска
map_module = {}
list_module_os = os.listdir(PATH_module)
for list in list_module_os:
	map_module[list.split(".")[0]] = list

#компиляция выражений для поиска
re_map_module = {}
for modul in map_module.keys():
	re_map_module[modul] = re.compile("{{"+modul+"}}")

#замена шаблона на данные
def replace_templar(text):
	flag_reload = False
	for re_map in re_map_module:
		#возможность включения модуль в модуль
		if re_map_module[re_map].search(text):
			flag_reload = True
		text = re_map_module[re_map].sub(file_read(PATH_module+map_module[re_map]), text)
	if flag_reload:
		replace_templar(text)
	return text	

#поиск страниц для сборки модулей
l_page_create = []
def walker(path, path_out=""):
	#создать подкаталог если не существует
	if (not os.path.exists(PATH_site_out+path_out)):
		os.makedirs(PATH_site_out+path_out)
		#l_page_create.append(PATH_site_out+path_out)
	for path_to_data in os.listdir(path):
		if (os.path.isfile(path+path_to_data)):
			file_write(PATH_site_out+path_out+path_to_data, replace_templar(file_read(path + path_to_data)))
			l_page_create.append(PATH_site_out+path_out+path_to_data)
		if(os.path.isdir(path+path_to_data)):
			walker(path+path_to_data+"/", path_out+path_to_data+"/")
walker(PATH_site)

#стабилизация относительных url
URL_STABILIZATION = re.compile("{{{URL_STABILIZATION}}}")
for page in l_page_create:
	if(URL_STABILIZATION.search(file_read(page))):
		rePage = URL_STABILIZATION.sub("", file_read(page))
		link_href = re.compile('href=".*?"');
		for href in link_href.findall(rePage):
			#проверка на абсолютные ссылки
			if(not href[6:10] == "http"):
				rePage = re.sub(href, 'href="'+PATH_site_name+href[6:], rePage)
		link_src = re.compile('src=".*?"');
		for src in link_src.findall(rePage):
			if(not src[5:9] == "http"):
				rePage = re.sub(src, 'src="'+PATH_site_name+src[5:], rePage)
		file_write(page, rePage);
#создание sitemap
sm = Sitemap(changefreq=SITEMAP_all_update)
for page in l_page_create:
	sm.add(PATH_site_name + page[7:])
file_write(PATH_site_out+"sitemap.xml", sm.get_as_string());
l_page_create.append(PATH_site_out+"sitemap.xml")
#создание robots
file_write(PATH_site_out+"robots.txt",ROBOT_TXT)
l_page_create.append(PATH_site_out+"robots.txt")
print "Content-Type: text/html\n\n"
print "<html>"
print "<br>Модулей найдено для подключения:<br>"
for page in os.listdir(PATH_module):
	print page+"<br>"
print "<br>Страниц создано:<br>"
for page in l_page_create:
	print page+"<br>"
print "Генерация для сайта " + PATH_site_name + "завершена."