#!/usr/local/bin/python
# coding: utf-8

import pygtk
pygtk.require('2.0')
import gtk, gobject
import re
import gtk.gdk
import math
import json
import MySQLdb
import hello
#import os
#import pango
#import sys
#import subprocess
import threading
#import string
#import time

gtk.gdk.threads_init()

class MainWindow(threading.Thread):
	def __init__(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)
		
		self.window.set_size_request(1200, 600)
		
		#argumenty
		self.trescPlikuOrg = '';
		self.trescPlikuTlum = '';
		
		#menu
		self.menu_item1 = gtk.MenuItem("Otwórz oryginał")
		self.menu_item1.connect("activate", self.otworzPlik, 'org')
		self.menu_item1.show()
		
		self.menu_item2 = gtk.MenuItem("Otwórz tłumaczenie")
		self.menu_item2.connect("activate", self.otworzPlik, 'tlum')
		self.menu_item2.show()
		
		self.menu_item3 = gtk.MenuItem("Otwórz JSON")
		self.menu_item3.connect("activate", self.otworzJSON)
		self.menu_item3.show()
		
		self.menu_item4 = gtk.MenuItem("Zapisz JSON")
		self.menu_item4.connect("activate", self.zapiszJSON)
		self.menu_item4.show()
		
		self.menu_item5 = gtk.MenuItem("Wygeneruj Tex")
		self.menu_item5.connect("activate", self.zapiszTex)
		self.menu_item5.show()
		
		self.menu = gtk.Menu()
		self.menu.append(self.menu_item1)
		self.menu.append(self.menu_item2)
		self.menu.append(self.menu_item3)
		self.menu.append(self.menu_item4)
		self.menu.append(self.menu_item5)
		
		self.root_menu = gtk.MenuItem("Plik")
		self.root_menu.show()
		self.root_menu.set_submenu(self.menu)
				
		self.menu_bar = gtk.MenuBar()
		self.menu_bar.append(self.root_menu)
		self.menu_bar.show()
		
		self.menuWrapper = gtk.HBox(False, 0)
		self.menuWrapper.pack_start(self.menu_bar, True, True, 5)
		self.menuWrapper.show()
		
		hello.say_hello('aaa')
		
		#body
		self.mainvbox = gtk.VBox(False, 0)
		
		self.hboxOrg = gtk.VBox(False, 0)
		self.hboxTlum = gtk.VBox(False, 0)
		self.hboxOrg.show()
		self.hboxTlum.show()
		
		self.linie = []
			
		self.bodybox = gtk.VBox(True, 0)
		self.sterownia = gtk.HBox(True, 0)
		self.sterownia.show();
		
		#przyciski
		self.buttonTyl = gtk.Button("<<<")
		self.buttonTyl.connect("clicked", self.doTylu, "check button 1")
		self.sterownia.pack_start(self.buttonTyl, True, False, 0)
		self.buttonTyl.show()
		
		self.tfStrona = gtk.Entry()
		self.tfStrona.connect("key_release_event", self.zmienStrone)
		self.tfStrona.set_width_chars(4)
		self.sterownia.pack_start(self.tfStrona, False, False, 0)
		self.tfStrona.show()
				
		self.ngStrona = gtk.Entry()
		self.ngStrona.set_width_chars(20)
		self.sterownia.pack_start(self.ngStrona, False, False, 0)
		self.ngStrona.show()

		self.buttonPrzod = gtk.Button(">>>")
		self.buttonPrzod.connect("clicked", self.doPrzodu, "check button 2")
		self.sterownia.pack_start(self.buttonPrzod, True, False, 0)
		self.buttonPrzod.show()
		
		self.bodybox.pack_start(self.sterownia, False)
		self.bodybox.show()
		
		self.zdania = [[],[]]
		
		self.sw = gtk.ScrolledWindow()
		self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.sw.add_with_viewport(self.bodybox)
		self.sw.show()
		
		self.strona = 0;
		self.elementow_na_strone = 5;
		
		self.mainvbox.pack_start(self.menuWrapper, False)
		self.mainvbox.pack_start(self.sw, True, True)
		
		self.mainvbox.show()
		
		self.window.add(self.mainvbox)
		self.window.show()
	def otworzPlik(self, widget, data=None):
		self.filew = gtk.FileSelection("File selection")
		self.filew.connect("destroy", self.destroy)
		self.filew.ok_button.connect("clicked", self.wybor_pliku, data)
		self.filew.cancel_button.connect("clicked", lambda w: self.filew.destroy())
		self.filew.show()
	def wybor_pliku(self, widget, data=None):
		infile = open(self.filew.get_filename(), "r")
		if infile:
			if(data == 'org'):
				self.trescPlikuOrg = infile.read()
			else:
				self.trescPlikuTlum = infile.read()
			infile.close()
		if(data == 'org'):
			self.zdania[0] = re.split('[\.\;\?\!]', self.trescPlikuOrg)
			for (i, item) in enumerate(self.zdania[0]):
				self.zdania[0][i] = self.zdania[0][i].strip(' \t\n\r')
				if(len(self.zdania[0][i]) < 1):
					del self.zdania[0][i]
		else:
			self.zdania[1] = re.split('[\.\;\?\!]', self.trescPlikuTlum)
			for (i, item) in enumerate(self.zdania[1]):
				self.zdania[1][i] = self.zdania[1][i].strip(' \t\n\r')
				if(len(self.zdania[1][i]) < 1):
					del self.zdania[1][i]
		self.rysujPola(self)
		self.filew.hide()
	def otworzJSON(self, widget, data=None):
		self.filej = gtk.FileSelection("File selection")
		self.filej.connect("destroy", self.destroy)
		self.filej.ok_button.connect("clicked", self.wyborJSON, data)
		self.filej.cancel_button.connect("clicked", lambda w: self.filej.destroy())
		self.filej.show()
	def wyborJSON(self, widget, data=None):
		infile = open(self.filej.get_filename(), "r")
		sjson = infile.read()
		teksty = json.loads(sjson)
		
		#usuwamy
		for item in self.zdania:
			for child in item:
				child = []

		for item in teksty:
			if(len(item) > 1):
				self.zdania[0].append(item[0])
				self.zdania[1].append(item[1])
			else:
				print "Blad"
		infile.close()
		self.filej.hide()
		self.rysujPola(self)
	def zapiszJSON(self, widget, data=None):
		self.filek = gtk.FileSelection("File selection")
		self.filek.connect("destroy", self.destroy)
		self.filek.ok_button.connect("clicked", self.wyborZapiszJSON, data)
		self.filek.cancel_button.connect("clicked", lambda w: self.filek.destroy())
		self.filek.show()
	def wyborZapiszJSON(self, widget, data=None):
		infile = open(self.filek.get_filename(), "w")
		
		sjson = []
		
		if(len(self.zdania[0]) > len(self.zdania[1])):
			for (i, item) in enumerate(self.zdania[0]):
				sjsonitem = []
				sjsonitem.append(item)
				if(i < len(self.zdania[1])):
					sjsonitem.append(self.zdania[1][i])
				else:
					sjsonitem.append("")
				sjson.append(sjsonitem)
		else:
			for (i, item) in enumerate(self.zdania[1]):
				sjsonitem = []
				if(i < len(self.zdania[0])):
					sjsonitem.append(self.zdania[0][i])
				else:
					sjsonitem.append("")
				sjsonitem.append(item)
				sjson.append(sjsonitem)
		print json.dumps(sjson)
		infile.write(json.dumps(sjson))
		infile.close()
		self.filek.hide()
	def zapiszTex(self, widget, data=None):
		self.filet = gtk.FileSelection("File selection")
		self.filet.connect("destroy", self.destroy)
		self.filet.ok_button.connect("clicked", self.wyborZapiszTex, data)
		self.filet.cancel_button.connect("clicked", lambda w: self.filet.destroy())
		self.filet.show()
	def wyborZapiszTex(self, widget, data=None):
		pattern = re.compile(ur'[^\w_\-\s:,\.\?!;]+', re.UNICODE);
		
		data = []
		nrPliku = 0
		texstring = ""
		
		self.db = MySQLdb.connect(host="localhost", user="semantyka", passwd="XqdDwn5hbj8R944Y", db="Semantyka")
		
		if(len(self.zdania[0]) > len(self.zdania[1])):
			for (i, item) in enumerate(self.zdania[0]):
				print i
				texstring = texstring + "\\begingl\n\gla\n"
				texstring = texstring + "" + pattern.sub('', self.zdania[0][i]) + "//\n"
				#texstring = texstring + "\glb\n"
				#for (j, word) in enumerate(re.split(" ", self.zdania[0][i])):
				#	word = re.sub(r"[^a-zA-Z]", "", word)
				#	if(not word):
				#		texstring = texstring + "{} "
				#	else:
				#		tlum = self.sprawdzWBazie(self, word)
				#		data = json.loads(tlum)
				#		opis = ""
				#		print data
				#		if("odmiana" in data):
				#			for odmiana in data["odmiana"]:
				#				opis = opis + " \n" + odmiana
				#		else:
			#				opis = opis + data["opis"]
				#			
				#		texstring = texstring + opis + " "
				#texstring = texstring + "\\newline\n"
				if(i < len(self.zdania[1])):
					texstring = texstring + "\glft\n" + pattern.sub('', self.zdania[1][i])
				texstring = texstring + "//\n\endgl" + "\n\\\\\n"
				print texstring
				return
				if(i%3000 == 0 and i != 0):
					#print texstring
					data.append(texstring)
					nrPliku = nrPliku + 1
					data.append(nrPliku)
					self.zapiszDoTex(self,data)
					del data[:]
					continue
		else:
			for (i, item) in enumerate(self.zdania[1]):
				print i				
				texstring = texstring + "\\begingl\n\gla\n"
				if(i < len(self.zdania[0])):
					texstring = texstring + "" + pattern.sub('', self.zdania[0][i]) + "//\n"
				#texstring = texstring + "\glb\n"
				#for (j, word) in enumerate(re.split(" ", self.zdania[0][i])):
				#	word = re.sub(r"[^a-zA-Z]", "", word)
				#	if( not word):
				#		texstring = texstring + "{} "
				#	else:
				#		tlum = self.sprawdzWBazie(self, word)
				#		data = json.loads(tlum)
				#		opis = ""
				#		if("odmiana" in data):
				#			for odmiana in data["odmiana"]:
				#				opis = opis + odmiana + " "
				#		elif("opis" in data):
				#			opis = opis + data["opis"] + " "
				#		else:
				#			opis = opis + "{} "
				#			
				#		texstring = texstring + opis + " "
				#		print texstring
				#
				#texstring = texstring + "\\newline\n"
				texstring = texstring + "\glft\n" + pattern.sub('', self.zdania[1][i])
				texstring = texstring + "//\n\endgl" + "\n\\\\\n"
				if(i%3000 == 0 and i != 0):
					#print texstring
					data.append(texstring)
					nrPliku = nrPliku + 1
					data.append(nrPliku)
					self.zapiszDoTex(self,data)
					del data[:]
					continue		
		data.append(texstring)
		nrPliku = nrPliku + 1
		data.append(nrPliku)
		self.zapiszDoTex(self,data)
		del data[:]		
		self.db.close()
		self.filet.hide()
	def zapiszDoTex(self, widget, data=None):
		headerstring = "\\documentclass[12pt, letterpaper]{book}\n"
		headerstring = headerstring + "\\usepackage[utf8]{inputenc}\n"
		headerstring = headerstring + "\\usepackage[LGR, T1]{fontenc}\n"
		headerstring = headerstring + "\\usepackage{expex}\n"
		headerstring = headerstring + "\\usepackage{amsmath}\n"
		headerstring = headerstring + "\\usepackage[polish,latin]{babel}\n"
		headerstring = headerstring + "\\usepackage{multicol}\n"
		headerstring = headerstring + "\\usepackage{textgreek}\n"
		headerstring = headerstring + "\\usepackage{xcolor}\n"
		headerstring = headerstring + "\\setlength{\columnsep}{1cm}\n"
		headerstring = headerstring + "\\begin{document}\n"
		
		footerstring = ""
		footerstring = footerstring + "\\end{document}\\\\";
		
		suffix = "_" + str(data[1])
		filename = re.sub(r"^(.*)[\.]([^\.]+)$", r"\1" + suffix + r".\2", self.filet.get_filename())
		
		infile = open(filename, "w")
		infile.write(headerstring + data[0] + footerstring)
		infile.close()
	def sprawdzWBazie(self, widget, data=None):
		cur = self.db.cursor()
		cur.execute("SELECT json FROM wiki WHERE lower(slowo) = \"" + data.decode('utf-8').lower() + "\"")
		for row in cur.fetchall():
			return row[0]
	def przetasuj(self, widget, event, wersja, zdanie):
		if event.keyval == 65365:
			if(zdanie > 0):
				lacznik = self.zdania[wersja][zdanie]
				self.zdania[wersja][zdanie-1] = self.zdania[wersja][zdanie-1] + " " + lacznik
				del self.zdania[wersja][zdanie]
			self.rysujPola(self)
		if event.keyval == 65366:
			if(zdanie > 0):
				rozdzielnik = widget.get_buffer().get_text(*widget.get_buffer().get_bounds())
				rozdzielone	= re.split('\|', rozdzielnik)
				for (i, item) in enumerate(rozdzielone):
					if(i == 0):
						self.zdania[wersja][zdanie] = item.strip(' \t\n\r')
					else:
						self.zdania[wersja].insert(zdanie+i, item.strip(' \t\n\r'))
			self.rysujPola(self)
	def doTylu(self, widget, data=None):
		print "Do tyłu"
		self.strona = self.strona - 1
		if(self.strona < 0):
			if(len(self.zdania[0]) > len(self.zdania[1])):
				self.strona = int(math.ceil(len(self.zdania[0])/self.elementow_na_strone))
			else:
				self.strona = int(math.ceil(len(self.zdania[1])/self.elementow_na_strone))
		self.tfStrona.set_text(str(self.strona))
		print "--", self.strona
		self.rysujPola(self)
	def doPrzodu(self, widget, data=None):
		print "Do Przodu"
		self.strona = self.strona + 1
		if(len(self.zdania[0]) > len(self.zdania[1])):
			if(math.ceil(len(self.zdania[0])/self.elementow_na_strone) < self.strona):
				self.strona = 0
		else:
			if(math.ceil(len(self.zdania[1])/self.elementow_na_strone) < self.strona):
				self.strona = 0
		self.tfStrona.set_text(str(self.strona))
		print "--", self.strona
		self.rysujPola(self)
	def zmienStrone(self, widget, data=None):
		print "Zmiana Strony"
		numer_strony = widget.get_text()
		if(numer_strony.isdigit()):
			self.strona = int(numer_strony)
		if(math.ceil(len(self.zdania[0])/self.elementow_na_strone) < self.strona 
			and math.ceil(len(self.zdania[1])/self.elementow_na_strone) < self.strona):
			self.strona = 0
			widget.set_text('0')
		print "--", self.strona
		self.rysujPola(self)
	def rysujPola(self, widget):		
		for item in self.linie:
			children = item.get_children()
			for child in children:
				podchildren = child.get_children()
				for podchild in podchildren:
					child.remove(podchild)
					
		print "Dlug-org: ", len(self.zdania[0])
		print "Dlug-tlum: ", len(self.zdania[1])
		print "ofset:strona/na_stronę: ", self.strona*self.elementow_na_strone, ":", self.strona, self.elementow_na_strone
		#org
		if(self.strona*self.elementow_na_strone < len(self.zdania[0])):
			j = 0
			print "A"
			for i in range(self.strona*self.elementow_na_strone, (self.strona*self.elementow_na_strone)+self.elementow_na_strone):
				print "A1: ", i
				if(j >= len(self.linie)):
					self.linie.append(gtk.HBox(True, 0))
					self.linie[j].show()
					hboxOrg = gtk.VBox(False, 0)
					hboxTlum = gtk.VBox(False, 0)
					hboxOrg.show()
					hboxTlum.show()
					self.linie[j].pack_start(hboxOrg, False)
					self.linie[j].pack_start(hboxTlum, False)
					self.bodybox.pack_start(self.linie[i], False)
				if(i < len(self.zdania[0])):
					textbuffer = gtk.TextBuffer()
					textfield = gtk.TextView(textbuffer)
					textfield.set_cursor_visible(True)
					textfield.set_editable(True)
					textfield.set_wrap_mode(gtk.WRAP_WORD)
					textfield.set_border_width(5)
					textfield.connect("key_release_event", self.przetasuj, 0, i)
					textbuffer.set_text(self.zdania[0][i])
					children = self.linie[j].get_children()
					children[0].add(textfield)
					textfield.show()
					j = j + 1
				else:
					break
		#tlum
		if(self.strona*self.elementow_na_strone < len(self.zdania[1])):
			j = 0
			print "B"
			for i in range(self.strona*self.elementow_na_strone, (self.strona*self.elementow_na_strone)+self.elementow_na_strone):
				print "B1: ", i
				if(j >= len(self.linie)):
					self.linie.append(gtk.HBox(True, 0))
					self.linie[j].show()
					hboxOrg = gtk.VBox(False, 0)
					hboxTlum = gtk.VBox(False, 0)
					hboxOrg.show()
					hboxTlum.show()
					self.linie[j].pack_start(hboxOrg, False)
					self.linie[j].pack_start(hboxTlum, False)
					self.bodybox.pack_start(self.linie[i], False)
				if(i < len(self.zdania[1])):
					textbuffer = gtk.TextBuffer()
					textfield = gtk.TextView(textbuffer)
					textfield.set_cursor_visible(True)
					textfield.set_editable(True)
					textfield.set_wrap_mode(gtk.WRAP_WORD)
					textfield.set_border_width(5)
					textfield.connect("key_release_event", self.przetasuj, 1, i)
					textbuffer.set_text(self.zdania[1][i])
					children = self.linie[j].get_children()
					children[1].add(textfield)
					textfield.show()
					j = j + 1
				else:
					break
		return True
	def destroy(self, widget, data=None):
		gtk.main_quit()
	def delete_event(self, widget, event, data=None):
		print "delete event occurred"
		return False
	def main(self):
		gtk.main()

if __name__ == "__main__":
	hello = MainWindow()
	hello.main()
