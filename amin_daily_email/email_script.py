#!/usr/bin/env python2.7
import datetime
import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import requests
import subprocess
from collections import defaultdict
import csv
import argparse
from pprint import pprint
import pickle
import time
import json
import sqlite3 as lite

SONGKICK_URL='http://api.songkick.com/api/3.0/metro_areas/26330/calendar.json?apikey=Eq2DVsvLqVYSCLs9&page=%s&per_page=50'
ECHONEST_URL='http://developer.echonest.com/api/v4/artist/profile?api_key=QHMQXB0SAIWRUFIKV&id=songkick:artist:%s&format=json&bucket=discovery&bucket=discovery_rank&bucket=hotttnesss&bucket=familiarity&bucket=familiarity_rank&bucket=hotttnesss_rank'


VENUES=['The Fillmore','O.co Coliseum','Public Works','Mezzanine','SAP Center','The Warfield','Rickshaw Stop','Bottom of the Hill',
        'The Chapel','Zellerbach Hall','Fox Theater','The Filmore','Bill Graham Civic Auditorium','Greek Theatre','The Independent']


def get_songkick():
  today = datetime.datetime.now()
  sk_data=requests.get(SONGKICK_URL%1).json()
  length=sk_data['resultsPage']['totalEntries']
  counter = int(length/50 + 1)
  artist_id_set=set()
  sk_backup=[]
  j=1
  while True:
    print 'page %s'%j
    sk_data=requests.get(SONGKICK_URL%j).json()
    if sk_data['resultsPage']['results']:
      j+=1
      try:
        for r in sk_data['resultsPage']['results']['event']:
          if r['venue']['displayName'] in VENUES:
            artist=[]
            pprint(r)
            sys.exit(1)
            for perf in r['performance']:
              artist_id_set.add(perf['artist']['id'])
              #artist.append(((perf['displayName'],perf['artist']['id'])))
              artist.append(perf['displayName'])
            sk_backup.append({
                              'type':r['type'],
                              'popularity':r['popularity'],
                              'event_name':r['displayName'],
                              'date':r['start']['datetime'].split('T')[0],
                              'artist':artist,
                              'location':r['location']['city'],
                              'venue':r['venue']['displayName']
                            })
      except Exception as e:
        print e
    else:
      break

  '''
  for i in range(1,counter):
    print 'page %s'%i
    try:
      sk_data=requests.get(SONGKICK_URL%i).json()
      for r in sk_data['resultsPage']['results']['event']:
        if r['venue']['displayName'] in VENUES:
          artist=[]
          for perf in r['performance']:
            artist_id_set.add(perf['artist']['id'])
            #artist.append(((perf['displayName'],perf['artist']['id'])))
            artist.append(perf['displayName'])
          sk_backup.append({
                            'type':r['type'],
                            'popularity':r['popularity'],
                            'event_name':r['displayName'],
                            'date':r['start']['datetime'].split('T')[0],
                            'artist':artist,
                            'location':r['location']['city'],
                            'venue':r['venue']['displayName']
                          })
    except Exception as e:
      print e
  '''
  with open('songkick_%s.csv'%(today.strftime("%Y-%m-%d")), 'wb') as f:
    spamwriter = csv.writer(f)
    csv_data=['date','type','venue','location','event_name','artist','popularity']
    spamwriter.writerow(csv_data)
    for show in sk_backup:
      try:
        spamwriter.writerow([show['date'],show['type'],show['venue'],show['location'],show['event_name'],",".join(show['artist']),show['popularity']])
      except Exception as e:
        print e

  #pickle.dump(sk_backup,open('%s-songkick-backup'%(today.strftime("%Y-%m-%d")),'wb'))
  #pickle.dump(artist_id_set,open('%s-artist-set'%(today.strftime("%Y-%m-%d")),'wb'))

def send_email(new_shows):
    sender = "Amin Heydari <aheydari3@gmail.com>"
    testing_email=['tickets@hellahungry.com']
    receivers = ' ,'.join(testing_email)
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "%s - Latest Bay Area concert"
    msg['From'] = sender
    msg['To'] = receivers
    html1="""\
        <head>
          <style>
          table,th,td
          {
          border:1px solid black;
          border-collapse:collapse;
          }
          th,td
          {
          padding:10px;
          }
          </style>
          </head>
        <html>
            <body>
              <p>
              Bay Area concerts daily digest. New concerts announced:<br>
              <table CELLPADDING="2" CELLSPACING="2" WIDTH="300">
                <tr>
                  <th >Date</th>
                  <th >Venue</th>
                  <th >Location</th>
                  <th >Artist(s)</th>
                  <th >Songkick Score</th>
                  <th >Max Discovery</th>
                  <th >Max Discovery Rank</th>
                  <th >Max Hotttnesss</th>
                  <th >Max Hotttnesss Rank</th>
                  <th >Max Familiarity</th>
                  <th >Max Familiarity Rank</th>
                </tr>
          """
    for key,show in new_shows.items():
      html1+="""\
                <tr>
                  <td style="text-align:Left;">%s</td>
                  <td style="text-align:Left;">%s</td>
                  <td style="text-align:Left;">%s</td>
                  <td with="500",style="text-align:Left;">%s</td>
                  <td style="text-align:Left;">%s</td>
                  <td style="text-align:Left;">%s</td>
                  <td style="text-align:Left;">%s</td>
                  <td style="text-align:Left;">%s</td>
                  <td style="text-align:Left;">%s</td>
                  <td style="text-align:Left;">%s</td>
                  <td style="text-align:Left;">%s</td>
                </tr>"""%(show['show_date'],show['venue'],show['location'],
                          show['artist'],show['sk_pop'],show['discovery'],show['discovery_r'],
                          show['hot'],show['hot_r'],show['familiarity'],show['familiarity_r'])
    html1+="""\
              </table><br>
              </p>
            </body>
        </html>"""



    
    part2 = MIMEText(html1, 'html')
    msg.attach(part2)
    s = smtplib.SMTP('smtp.gmail.com:587')
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login('aheydari3@gmail.com','northfacemehdi2@')
    #s.sendmail(sender, emaillookup[t], msg.as_string())
    s.sendmail(sender, testing_email, msg.as_string())
    s.quit()

def songkick_db():
  artist_id_set=set()
  artist_dict={}
  sk_backup=[]
  j=1
  while True:
    try:
      print 'page %s'%j
      sk_data=requests.get(SONGKICK_URL%j).json()
      j+=1
      for r in sk_data['resultsPage']['results']['event']:
          if r['venue']['displayName'] in VENUES:
            artist=[]
            for perf in r['performance']:
              artist_id_set.add(perf['artist']['id'])
              artist_dict[perf['artist']['displayName']]=perf['artist']['id']

              #artist.append(((perf['displayName'],perf['artist']['id'])))
              artist.append(perf['displayName'])
            sk_backup.append((r['id'],r['start']['date'],r['type'],r['displayName'],r['location']['city'],r['venue']['displayName'],
                            ",".join(artist),r['popularity']))
    except Exception as e:
      print e
      break

  new_shows={}
  new_artists_id=set()
  con = lite.connect('amin.db')
  with con:
    cur = con.cursor()
    #insert new shows into db
    for show in sk_backup:
      #max_artist=defaultdict(list)
      max_artist={}
      for key in ['discovery','discovery_rank','familiarity','familiarity_rank','hotttnesss','hotttnesss_rank']:
        max_artist[key]=list()

      cur.execute("SELECT event_id FROM test")
      event_ids=[i[0] for i in cur.fetchall()]
      if show[0] not in event_ids:
          cur.execute("INSERT INTO test(event_id,show_date,show_type,event_name,location,venue,artist,sk_pop) VALUES(?,?,?,?,?,?,?,?)", show)
          artist_count=1
          for artist in show[6].split(','):
            if (artist_count%120) == 0:
              time.sleep(60)
              print 'sleeping'
            else:
              try:
                echo_data=requests.get(ECHONEST_URL%artist_dict[artist]).json()
                #pprint(echo_data)
                if 'artist' in echo_data['response'].keys():
                  ed_name=echo_data['response']['artist']['name']
                  ed_id=echo_data['response']['artist']['id']
                  ed_d=echo_data['response']['artist']['discovery']
                  ed_dr=echo_data['response']['artist']['discovery_rank']
                  ed_f=echo_data['response']['artist']['familiarity']
                  ed_fr=echo_data['response']['artist']['familiarity_rank']
                  ed_h=echo_data['response']['artist']['hotttnesss']
                  ed_hr=echo_data['response']['artist']['hotttnesss_rank']
                  
                  max_artist['discovery'].append(ed_d)
                  max_artist['discovery_rank'].append(ed_dr)
                  max_artist['familiarity'].append(ed_f)
                  max_artist['familiarity_rank'].append(ed_fr)
                  max_artist['hotttnesss'].append(ed_h)
                  max_artist['hotttnesss_rank'].append(ed_hr)
                  data=(ed_name,ed_id,ed_d,ed_dr,ed_f,ed_fr,ed_h,ed_hr)
                  cur.execute("SELECT sk_id FROM echonest")
                  sk_ids=[i[0] for i in cur.fetchall()]
                  
                  #######UPDATE THIS SO IT ALWAYS PUTS THE LATEST SCORES RATHER THAN WHAT'S ALREADY IN THE DB###################    
                  if ed_id not in sk_ids:
                    cur.execute("INSERT INTO echonest(name,sk_id,discovery,discovery_rank,familiarity,familiarity_rank,hotttnesss,hotttnesss_rank)\
                               VALUES(?,?,?,?,?,?,?,?)", data)
                  else:
                    print 'already have it'
                #echonest_backup.append(echo_data['response']['artist'])
              except Exception as e:
                print e
                print 'did not find data for',artist
            artist_count+=1

          for key in ['discovery','discovery_rank','familiarity','familiarity_rank','hotttnesss','hotttnesss_rank']:
            if not max_artist[key]:
              #print key, max_artist[key]
              max_artist[key].append(0)

                  
          new_shows[show[0]]=dict(
                        show_date=show[1],
                        show_type=show[2],
                        event_name=show[3],
                        location=show[4],
                        venue=show[5],
                        artist=show[6],
                        sk_pop=show[7],
                        hot=max(max_artist['hotttnesss']),
                        hot_r=min(max_artist['hotttnesss_rank']),
                        discovery=max(max_artist['discovery']),
                        discovery_r=min(max_artist['discovery_rank']),
                        familiarity=max(max_artist['familiarity']),
                        familiarity_r=min(max_artist['familiarity_rank']),
                        )

  pprint(new_shows)
  if new_shows:
    send_email(new_shows)
    print 'email sent'


  '''
  cur.execute("SELECT MAX(id) FROM test")
  current_rowid=cur.fetchall()[0][0]
  if not current_rowid:
    current_rowid=0
  last_row=cur.lastrowid
  if last_row:
    cur.execute("SELECT * FROM test WHERE id > %s and id <= %s"%(current_rowid,last_row))
    new_data=[i for i in cur.fetchall()]
  else:
    print 'no new row'
  '''

  '''
  for show in new_shows:
    try:
        for artist in new_shows[show]['artist'].split(','):
          print artist,artist_dict[artist]
          new_artists_id.add((show[0],artist_dict[artist]))
    except Exception as e:
        print new_shows[show]['artist']
        new_artists_id.add(artist_dict[artist])

    '''
    #print current_rowid, cur.lastrowid
    #cur.executemany("INSERT INTO test(show_date,show_type,event_name,location,venue,artist,sk_pop) VALUES(?,?,?,?,?,?,?)", sk_backup)

def collect_echonest():
  today = datetime.datetime.now()
  artist_data=pickle.load(open("2014-03-09-artist-set",'rb'))
  echonest_backup=[]
  total_artists=len(artist_data)
  i=1
  for artist in artist_data:
    print '%s/%s'%(i,len(artist_data))
    if (i%120) == 0:
      time.sleep(60)
    else:
      try:
        echo_data=requests.get(ECHONEST_URL%artist).json()
        echonest_backup.append(echo_data['response']['artist'])
      except Exception as e:
        print artist
        print echo_data
    i+=1
  pickle.dump(echonest_backup,open('%s-echonest-backup'%(today.strftime("%Y-%m-%d")),'wb'))


def get_venue():
  today = datetime.datetime.now()
  sk_data=requests.get(SONGKICK_URL%1).json()
  length=sk_data['resultsPage']['totalEntries']
  counter = int(length/50 + 1)
  venue_set=set()
  for i in range(1,counter):
    print 'page %s'%i
    try:
      sk_data=requests.get(SONGKICK_URL%i).json()
      for r in sk_data['resultsPage']['results']['event']:
        venue_set.add((r['venue']['displayName'],r['location']['city']))
    except Exception as e:
      print e
  for i in venue_set:
    print '%s,%s'%(i[0],i[1])
  #pickle.dump(sk_backup,open('%s-songkick-backup'%(today.strftime("%Y-%m-%d")),'wb'))


def pickle_json():
  data = pickle.load( open( "2014-03-10-echonest-backup", "rb" ) )
  with open('2014-03-10-echonest-backup.json', 'w') as outfile:
    json.dump(data, outfile)


def main():
  #pickle_json()
  #get_venue()
  #get_songkick()
  '''
  new_shows={}
  new_shows[19466019]=dict(artist= 'Among the Torrent,A Thousand Dead,Anisoptera',
                          discovery= 0.30538724448822274,
                          discovery_r= 179935,
                          event_name='Among the Torrent with A Thousand Dead and Anisoptera at Bottom of the Hill (April 22, 2014)',
                          familiarity= 0.215672,
                          familiarity_r= 413889,
                          hot= 0.319032,
                          hot_r= 204950,
                          location='San Francisco, CA, US',
                          show_date= '2014-04-22',
                          show_type= 'Concert',
                          sk_pop= 6e-06,
                          venue='Bottom of the Hill'
                          )
  send_email(new_shows)
  '''
  songkick_db()
  #collect_echonest()
    



if __name__ == '__main__':
	main()
