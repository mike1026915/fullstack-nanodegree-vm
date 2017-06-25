from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
import cgi

engine = create_engine('sqlite:///restaurantMenu.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):

    def basic_header(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()  


    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Hello!</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>&#161 Hola !</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants"):
                self.basic_header()
                all_restaurant = session.query(Restaurant).all()
                output = ""
                output += "<html><body>"
                for r in all_restaurant:
                    output += "<h3>%s" % r.name
                    output += "<a href='/restaurants/%s/edit'>Edit</a>   " % r.id
                    output += "<a href='/restaurants/%s/delete'>Delete</a>" % r.id
                    output += "</h3>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/edit"):
                print self.path
                r_id = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id=r_id).one()
                if restaurant:
                    self.basic_header()
                    output = "<html><body>"
                    output += "<h1>"
                    output += restaurant.name
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/%s/edit' >" % r_id
                    output += "<input name='new_name' type='text' >"
                    output += "<input type='submit' value = 'Rename'>"
                    output += "</form>"
                    output += "</body></html>"

                    self.wfile.write(output)
                return

            if self.path.endswith("/delete"):
                print self.path
                r_id = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id=r_id).one()
                if restaurant:
                    self.basic_header()
                    output = "<html><body>"
                    output += "<h1>"
                    output += restaurant.name
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/%s/delete' >" % r_id
                    output += "<h3>Are you sure to delte %s </h3>" % restaurant.name
                    output += "<input type='submit' value = 'Delete'>"
                    output += "</form>"
                    output += "</body></html>"

                    self.wfile.write(output)
                return

            if self.path.endswith("/restaurants/new"):
                self.basic_header()
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><input name="restaurant_name" type="text" ><input type="submit" value="Create"> </form>'''
                
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):

                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('restaurant_name')

                print messagecontent
                session.add(Restaurant(name=messagecontent[0]))
                session.commit()
                
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('new_name')
                    r_id = self.path.split("/")[2]

                    restaurant = session.query(Restaurant).filter_by(id=r_id).one()
                    if restaurant:
                        restaurant.name = messagecontent[0]
                        session.add(restaurant)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()  
                return

            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('new_name')
                    r_id = self.path.split("/")[2]

                    restaurant = session.query(Restaurant).filter_by(id=r_id).one()
                    if restaurant:
                        session.delete(restaurant)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()  
                return 

        except Exception as e:
            print e


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()