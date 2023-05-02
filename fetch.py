from bs4 import BeautifulSoup
import requests as req
from flask import Flask, abort, jsonify,request


def fetchData(code):    
    
    link=f"https://iechub.rfi.it/ArriviPartenze/ArrivalsDepartures/Monitor?Arrivals=False&Search=&PlaceId={code}"
    s=req.Session()
    orario=[]
    binario=[]
    ritardo=[]
    da=[]
    resp= s.get(link).text
    soup= BeautifulSoup(resp, 'html.parser')
    time=soup.find_all("td",{"id": "ROrario"})
    bin=soup.find_all("td",{"id": "RBinario"})
    rit=soup.find_all("td",{"id": "RRitardo"})
    to=soup.find_all("td",{"id": "RStazione"})
    for i in time:
        orario.append(i.text)
    for i in rit:
        ritTime=str(i.text).strip()
        #print(f"ritTime: {ritTime}, {bool( not ritTime)}")
        if not ritTime:
            #print("ye")
            ritTime=0
            ritardo.append(ritTime)
        else: 
            ritardo.append(ritTime)

    for i in bin:
        tempBin=str(i).split("<div>")[1].split()[0].split("</div>")[0]
        if not tempBin:
            binario.append("X")
        else:
            binario.append(str(i).split("<div>")[1].split()[0].split("</div>")[0])
            
    for i in to:
        da.append(str(i).split("<div>")[1].split("</div>")[0].strip())
        

    return da,orario,binario,ritardo

app = Flask(__name__)
diz=dict()

@app.route('/getinfo')
def fetch():
    src = request.args.get('from')
    num= request.args.get('n')

    if not num.isdecimal() or int(num)>20:
        return abort(400, "number error")
    
    if not src.isdecimal():
        return abort(404, 'Station not found')
    
    verso,orario,treno,ritardo=fetchData(src)
    if not verso:
        return abort(404, 'Station not found')
    diz=[]
    for i in range(int(num)):
        lineData={}
        try:
            lineData['to']=verso[i]
            lineData['orario']=orario[i]
            lineData['binario']=treno[i]
            lineData['ritardo']=ritardo[i]
        except:
            continue
        diz.append(lineData) 
          
    return jsonify(diz)

@app.route("/stazioni")
def stations():
    link="https://iechub.rfi.it/ArriviPartenze/"
    s=req.Session()
    resp= s.get(link).text
    soup= BeautifulSoup(resp, 'html.parser')
    html='usa CTRL+F per cercare la tua stazione <br><br><br><table>'
    for i in soup.find_all("option"):
        html+=f"<tr><td>{i.text}</td><td>&emsp;{i.get('value')}</td></tr>"
    html+="</table>"
    return html

@app.route('/showinfo')
def show():
    src = request.args.get('from')
    num= request.args.get('n')

    if not src.isdecimal():
        return abort(404, 'Station not found')
    
    if not num.isdecimal() or int(num)>20:
        return abort(400, "number error")
     
    verso,orario,treno,ritardo=fetchData(src)
    if not verso:
        return abort(404, 'Station not found')
    html=''
    for i in range(int(num)):
        try:
            html+=f"Il treno delle {orario[i]} verso {verso[i]} parte dal binario {treno[i]} con un ritardo di {ritardo[i]} minuti<br>"
        except:
            html+=""
    return html

    

if __name__=='__main__':
    app.run(port=5000)

