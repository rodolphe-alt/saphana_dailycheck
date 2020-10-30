# coding=utf-8
################################################
# Rodolphe ALT
# 0.1
# goal : check SAP HANA database from sql, and send mail for a dailycheck
#################################################
import sys
import pyhdb
import datetime
import time
import os
import csv
import smtplib
import socket
#from StringIO import StringIO  # Python2
from io import StringIO		# Python3
from email.mime.text import MIMEText
from hurry.filesize import size
from hurry.filesize import si
from bitmath import *
from prettytable import PrettyTable
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import locale
import traceback
locale.setlocale(locale.LC_ALL, 'fr_FR.utf-8')

# timestamp
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
mydate4hana = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d')
mytime4hana = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')

# settings
file_src = "/opt/scripts/moni_hana/dailycheck_saphana_sqlcode.txt"
file_log = "/opt/scripts/moni_hana/dailycheck_saphana.log"
SAPHANA_SID = 'VX1'
SAPHANA_HOSTNAME = 'hostname'
SAPHANA_SCHEMA = 'SAPHANADB'
SAPHANA_SQLPORT = '30068'                       # adapt this entry according to the tenant
SAPHANA_INDEXPORT = '30067'			# need for sql request
SAPHANA_ADMIN_LOGIN = 'TECH_MONI'
SAPHANA_ADMIN_PWD = 'UltraComplexPassword2020!'
Email_sender = 'From@gmail'
Email_receiver = 'To@gmail'
Email_server = 'smtp.orange.fr'
Email_port = '25'
#Mode_console_or_email='email'			# values email or console
Mode_console_or_email='console'
script_srv_server = socket.gethostname()

# Hana remote connexion
connection = pyhdb.connect(SAPHANA_HOSTNAME, SAPHANA_SQLPORT, SAPHANA_ADMIN_LOGIN, SAPHANA_ADMIN_PWD)
pyhdb.protocol.constants.MAX_MESSAGE_SIZE = 2**19			# The default value is 2**17, which is about 130KB
pyhdb.protocol.constants.MAX_SEGMENT_SIZE = pyhdb.protocol.constants.MAX_MESSAGE_SIZE - 32
cursor = connection.cursor()

# Store the reference, in case you want to show things again in standard output
old_stdout = sys.stdout

# This variable will store everything that is sent to the standard output
result = StringIO()
sys.stdout = result
count = 0
html = "<br>"

if Mode_console_or_email == 'console':
	print("Hello\r")
	print("Please find the results of our dailycheck %s on SAP %s." % (st,SAPHANA_SID))
	print("\n********* HANA CHECKS ********* \r")
if Mode_console_or_email == 'email':
	html = html + "Hello<br>" + ("Please find the results of our dailycheck %s on SAP %s.<br>" % (st,SAPHANA_SID))
	html = html + "<h2>********* HANA CHECKS *********</h2><br>"

try:
	with open(file_src, 'r') as inf:
		for line in inf:
			if len(line)  > 1:
				chara = line[0:3]
				display_error = 0
				error_detail = 'null'
				if chara == "/D:":
					count = count + 1
					if Mode_console_or_email == 'console': print("\n", count, line[3:])
					if Mode_console_or_email == 'email': html = html + "<h2>" + str(count) + line[3:] + "</h2>"
				if chara == "/R:":
					try:
						command_sql = line[3:].replace('SAPHANA_SCHEMA',SAPHANA_SCHEMA)
						command_sql = command_sql.replace('SAPHANA_INDEXPORT',SAPHANA_INDEXPORT)
						cursor.execute(command_sql)
						from prettytable import from_db_cursor
						mytable = from_db_cursor(cursor)
						print(mytable)
						if Mode_console_or_email == 'email':
							html = html + mytable.get_html_string(attributes={
								'border': 1,
								'style': 'border-width: 1px; border-collapse: collapse;'
							}) + "<hr>"
					except Exception:
						display_error = 1
						error_detail = traceback.format_exc()
				if (chara == "/S:" and line.find('1969700') > 0):
					sql_file = line[3:]
					sql_file = sql_file.replace('\n','')
					try:
						sql_file_content = open(sql_file)
						sql_as_string = sql_file_content.read()
						cursor.execute(sql_as_string)
						from prettytable import from_db_cursor
						mytable = from_db_cursor(cursor)
						print(mytable)
						if Mode_console_or_email == 'email':
							html = html + mytable.get_html_string(attributes={
								'border': 1,
								'style': 'border-width: 1px; border-collapse: collapse;'
							}) + "<hr>"
					except Exception:
						display_error = 1
						error_detail = traceback.format_exc()
				if display_error == 1:
					print("====> an error has been occured with the sql : %s" % error_detail)
					if Mode_console_or_email == 'email':
						html = html + ("===> an error has been occured with the sql command : %s<br>" % error_detail)

finally:
	inf.close()


print("\nscript executed on %s.\r" % (script_srv_server))
print("Rodolphe\n")

if Mode_console_or_email == 'email':
	html = html + ("<br>script executed on %s.<br>" % (script_srv_server)) + "Rodolphe"

# Redirect again the std output to screen
sys.stdout = old_stdout

# Then, get the stdout like a string and process it!
result_string = result.getvalue()

# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(result_string, 'plain')
part2 = MIMEText(html, 'html')

if Mode_console_or_email == 'console':
	print(result_string)

if Mode_console_or_email == 'email':
	# SMTP server
	smtpserver = smtplib.SMTP(Email_server, Email_port)
	# MSG building
	msg = MIMEMultipart('alternative')
	msg['Subject'] = ("daily monitoring %s" % (SAPHANA_SID))
	smtpserver.ehlo()
	msg['From'] = Email_sender
	msg['To'] = Email_receiver
	msg.attach(part2)
	smtpserver.sendmail(Email_sender, Email_receiver, msg.as_string())
	print("email sent !")
	smtpserver.quit()

# Log intofile
outF = open(file_log, "w")
outF.writelines(result_string)
outF.close()

connection.commit()
connection.close()
