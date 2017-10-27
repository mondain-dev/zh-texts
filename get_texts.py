import sys
import os.path

import re
import requests
import urllib
import random
import pypandoc
import getpass

from os import listdir, makedirs
from time import sleep
from bs4 import BeautifulSoup, Comment
from urlparse import urljoin, urlparse, parse_qsl

from ctext import *

print 'ctext log in'
apisession.post('http://ctext.org/account.pl', {'un':raw_input('ctext username: '), 'pw': getpass.getpass()})

def GetTextChapters(ctext_res=625979):
  base_url = 'http://ctext.org/wiki.pl?'
  r = requests.get(base_url, params= { 'res' : str(ctext_res)})
  soup = BeautifulSoup(r.text, 'lxml')
  chapter_list = list(set([ dict(parse_qsl(urlparse(i['href'])[4]))['chapter'] for i in soup.select('.ctext a')]))
  chapter_id_list = ['ctp:ws' + i for i in chapter_list]
  return chapter_id_list

def SaveFullTexts(ctext_res=625979, output_dir = 'text'):
  chapters = GetTextChapters(ctext_res)
  sleep(30)
  if not os.path.exists(output_dir):
    makedirs(output_dir)
  for chapter_id in chapters:
    text = gettext(chapter_id)
    filename = os.path.join(output_dir, text['title']+'.txt')
    if not os.path.exists(filename):
      print text['title']
      with open(filename, 'w') as f:
        for p in text['fulltext']:
          f.write(p.encode('utf8')+'\n\n')
      sleep(random.uniform(1,5) +  random.gauss(5,1) + 30)

def CText2TeX(fname):
  latex_str = ''
  f = open(fname, 'r')
  for l in f:
    l = l.decode('utf-8')
    r = re.match('(\*+)(.*)', l)
    if r:
      sub_level  = len(r.group(1))
      sub_title  = r.group(2)
      latex_str += ('\\' + 'sub' * (sub_level-1) + 'section{' + sub_title + '}')
    else:
      latex_str += l
  
  return latex_str

def ConvertFullTexts2TeX(input_dir = 'text', output_dir = 'tex'):
  if not os.path.exists(output_dir):
    makedirs(output_dir)
  
  for t in listdir(input_dir):
    r = re.match('(.*).txt$', t)
    if r:
      text_fname = os.path.join(input_dir, t)
      tex_str    = CText2TeX(text_fname)
      tex_fname  = os.path.join(output_dir, r.group(1) + '.tex')
      with open(tex_fname, 'w') as f:
        f.write(tex_str.encode('utf-8'))
