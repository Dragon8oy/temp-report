import smtplib, datetime, time, csv, sys, os
import tempreport
import graph
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

#Variables for email and the sensor
email_recipients = ['']
last_email_time = datetime.datetime(1970, 1, 1, 0, 0)
email_time_diff = 0

#See data/config.csv for a config file. Use python3 temp.py -c to generate a new one

def updateConfig():
  global delay
  delay = tempreport.readCSVLine('data/config.csv', 2, 'keyword', 'delay', var_type = 'int')
  global gap
  gap = tempreport.readCSVLine('data/config.csv', 2, 'keyword', 'gap', var_type = 'int')
  global threshold_max
  threshold_max = tempreport.readCSVLine('data/config.csv', 2, 'keyword', 'threshold_max', var_type = 'float')
  global threshold_min
  threshold_min = tempreport.readCSVLine('data/config.csv', 2, 'keyword', 'threshold_min', var_type = 'float')
  global graph_point_count
  graph_point_count = tempreport.readCSVLine('data/config.csv', 2, 'keyword', 'graph_point_count', var_type = 'int')
  global area_name
  area_name = tempreport.readCSVLine('data/config.csv', 2, 'keyword', 'area_name', var_type = 'str')

  if delay == None:
    print('Errors occured while reading config values, attempting to fix config file:')
    tempreport.writeConfig('s')
    print('Done')
    updateConfig()
  print('Read config values')

def connectToServer():
  #Connects to gmail's servers
  global server
  server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
  server.connect('smtp.gmail.com', 465)
  print('Connected to server')
  server.login(email_sender, password)
  print('Logged in successfully as ' + email_sender + '\n')

def updateRecipients():
  global email_recipients
  if str(os.path.isfile('data/addresses.csv')) == 'False':
    print('\nNo address file found, starting address editor: \n')
    tempreport.dataEdit()
  print('Addresses:')
  line_count = tempreport.getLineCount('data/addresses.csv')
  email_recipients = ['']
  for line in range(2, line_count + 1):
    if line == 2:
      email_recipients[0] = (tempreport.readCSVLine('data/addresses.csv', 1, 'numbered', line, var_type = 'str'))
      print(email_recipients[0])
    else:
      email_recipients.append(tempreport.readCSVLine('data/addresses.csv', 1, 'numbered', line, var_type = 'str'))
      print(email_recipients[line - 2])

def updateSender():
  global email_sender_name
  global email_sender
  global password
  if str(os.path.isfile('data/sender.csv')) == 'False':
    tempreport.changeSender('e')
  email_sender      = tempreport.readCSVLine('data/sender.csv', 1, 'numbered', 2, var_type = 'str')
  password          = tempreport.readCSVLine('data/sender.csv', 1, 'numbered', 3, var_type = 'str')
  email_sender_name = tempreport.readCSVLine('data/sender.csv', 1, 'numbered', 4, var_type = 'str')

#changeSender

def updateMessage():
  #Reads the image
  with open('graph.png', 'rb') as fp:
    html_image = MIMEImage(fp.read())

  #Updates the message to be sent
  global msg
  msg = MIMEMultipart('alternative')
  msg['Subject'] = str(area_name) + ' Temperature Alert'
  msg['From'] = email_sender_name
  msg['To'] = 'Whomever it may concern'
  html_wrap = '<html><body><p>The temperature is no longer between ' + str(threshold_max) + '°C and ' + str(threshold_min) + '°C. </p><p>The temperature is currently ' + str(temp) + '°C at ' + str(datetime.datetime.now().strftime("%H:%M:%S")) + '</p><p>The highest temperature reached recently is: ' + str(max_temp) + '°C at ' + str(max_temp_time) + '</p><p>The lowest temperature reached recently is: ' + str(min_temp) + '°C at ' + str(min_temp_time) + '</p><br><img alt="Temperature Graph" id="graph" src="cid:graph"></body></html>'
  msgHtml = MIMEText(html_wrap, 'html')

  #Define the image's ID
  img = open('graph.png', 'rb').read()
  msgImg = MIMEImage(img, 'png')
  msgImg.add_header('Content-ID', '<graph>')
  msgImg.add_header('Content-Disposition', 'attachment', filename='graph.png')
  msgImg.add_header('Content-Disposition', 'inline', filename='graph.png')

  msg.attach(msgHtml)
  msg.attach(msgImg)

def sendMessage():
  #Sends the message
  #Gets current time and works out time since the last email sent
  global last_email_time
  email_time_diff = (time.mktime(datetime.datetime.now().timetuple()) - time.mktime(last_email_time.timetuple()))
  #Sends the message if the time is ok
  if email_time_diff >= gap:
    #Sends an email to the addresses in the array
    for x in range(0, len(email_recipients)):
      try:
        error = 0
        server.sendmail(email_sender, email_recipients[x], msg.as_string())
      except:
        print('There was an error while sending the message to ' + email_recipients[x])
        error = 1
      if error == 0:
        print('Email sent to ' + str(email_recipients[x]))
      else:
        error == 0
    print('Sent email to ' + str(len(email_recipients)) + ' addresses')
    print('Email was last sent ' + str(email_time_diff) + ' seconds ago')
    last_email_time = datetime.datetime.now()
  else:
    print('Email was last sent ' + str(email_time_diff) + ' seconds ago')
    print('Email not sent\n')
  try:
    server.quit()
    error = 0
  except:
    print('Failed to logout')
    error = 1
  if error == 0:
    print('\nLogged out\n')

def readRecords():
  global temp
  global max_temp
  global min_temp
  global max_temp_time
  global min_temp_time

  while str(os.path.isfile('data/temp-records.csv')) == 'False':
    print('No records found')
    time.sleep(1)

  max_temp = tempreport.readCSVLine('data/temp-records.csv', 2, 'keyword', 'max', var_type = 'float')
  max_temp_time = tempreport.readCSVLine('data/temp-records.csv', 3, 'keyword', 'max')
  if float(temp) > float(max_temp):
    print('Current temp was higher than recorded max temp, updating locally\n')
    max_temp = temp
    max_temp_time = datetime.datetime.now().strftime("%H:%M:%S")

  min_temp = tempreport.readCSVLine('data/temp-records.csv', 2, 'keyword', 'min', var_type = 'float')
  min_temp_time = tempreport.readCSVLine('data/temp-records.csv', 3, 'keyword', 'min')
  if float(temp) < float(min_temp):
    print('Current temp was lower than recorded min temp, updating locally\n')
    min_temp = temp
    min_temp_time = datetime.datetime.now().strftime("%H:%M:%S")

sys.argv.append(0)
if sys.argv[1] == '-h' or sys.argv[1] == '--help':
  print('Options:')
  print('	-h  | --help           : Display the help menu')
  print('	-a  | --addresses      : Add, remove, view or edit recipient email addresses')
  print('	-p  | --password       : Update the password for the sender address used')
  print('	-s  | --sender         : Change the address of the sender email')
  print('	-n  | --name           : Change the name of the sender')
  print('	-c  | --config         : Generate a new config file')
  print('	-cs | --config-save    : Add missing config entries')
  exit()
elif sys.argv[1] == '-a' or sys.argv[1] == '--address':
  tempreport.dataEdit()
  exit()
elif sys.argv[1] == '-p' or sys.argv[1] == '--password':
  tempreport.changeSender('p')
  exit()
elif sys.argv[1] == '-s' or sys.argv[1] == '--sender':
  tempreport.changeSender('s')
  exit()
elif sys.argv[1] == '-n' or sys.argv[1] == '--name':
  tempreport.changeSender('n')
  exit()
elif sys.argv[1] == '-c' or sys.argv[1] == '--config':
  tempreport.writeConfig('f')
  exit()
elif sys.argv[1] == '-cs' or sys.argv[1] == '--config-save':
  tempreport.writeConfig('s')
  exit()

print('--------------------------------')

#Load the config
tempreport.writeConfig('s')
updateConfig()

try:
  connectToServer()
except:
  print('There was an error while connecting to the email server')
  exit()

def trySendMessage():
  try:
    sendMessage()
  except:
    print('There was an error attempting to send the email, retrying in 3 minutes')
    time.sleep(180)
    trySendMessage()

while True:
  #Measure the temperature
  temp = tempreport.measureTemp()
  readRecords()
  #Update addresses and credentials
  if temp >= threshold_max or temp <= threshold_min:
    updateRecipients()
    updateSender()
    #Create message contents
    graph.generateGraph(graph_point_count, area_name)
    updateMessage()
    #Send the message
    trySendMessage()
  print('--------------------------------\n')
  time.sleep(delay)
