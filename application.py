from flask import Flask,render_template,request,jsonify,send_file
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import os

application = Flask(__name__)
application = app

@app.route("/",methods=['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review",methods=['GET','POST'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form["content"]
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString.replace(" ","%20")
            uclient = uReq(flipkart_url)
            flipkart_page = uclient.read()
            uclient.close()
            flipkart_html = bs(flipkart_page,"html.parser")
            bigbox = flipkart_html.find_all("div", {"class":"_1AtVbE col-12-12"})
            del bigbox[0:3]
            box = bigbox[0]
            product_link = "https://www.flipkart.com" + box.div.div.div.a['href']
            product_req = requests.get(product_link)
            product_html = bs(product_req.text,"html.parser")
            print(product_html)
            commentboxes = product_html.find_all('div', {'class': "_16PBlm"})

            global filename
            try:
                
                filename = searchString + ".csv"
                
            except:
                filename = searchString + ".csv" + "copy"
            fw = open(filename, "w", encoding="utf-8")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    name = 'No Name'

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text


                except:
                    rating = 'No Rating'

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ",e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
                fw.write(searchString+","+name+","+rating+","+commentHead+","+custComment+"\n")
                
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

@app.route('/getPlotCSV') 
def csv_get():
    return send_file(filename,as_attachment=True),os.remove(filename)

    


if __name__=="__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
