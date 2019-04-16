
from flask import Flask, render_template, url_for
import flask, random, os, sys, inspect
app = Flask(__name__, static_url_path='/static')
tempWebVer = '0.1.1'
tempVer = 'Test'

try:
    from w1thermsensor import W1ThermSensor
    sensor = W1ThermSensor()
except:
    print('Failed to load kernel modules, make sure you are running this on an RPI with OneWire and GPIO enabled')

currDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parDir = os.path.dirname(currDir)
sys.path.insert(0,parDir)
import graph, tempreport

@app.route('/')
def main(flaskVer=flask.__version__, tempWebVer=tempWebVer, tempVer=tempVer):
    def measureTemp():
        return random.randint(1,30)#str(sensor.get_temperature()) + '°C'
    return render_template('tempreport.html', flaskVer=flaskVer, tempWebVer=tempWebVer, tempVer=tempVer, measureTemp=measureTemp)

if __name__ == "__main__":
    app.run(host= '0.0.0.0', port= 5000)