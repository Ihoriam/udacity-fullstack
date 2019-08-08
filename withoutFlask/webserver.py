from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/new'>"
                output += "<input name = 'newRestaurantName' type = 'text' placeholder = 'New Restaurant Name' > "
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"

                self.wfile.write(output.encode())
                return

            if self.path.endswith("/delete"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()

                output = "<html><body>"
                output += "<h1>Do you want to delete {}</h1>".format(myRestaurantQuery.name)
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/{}/delete' >".format(restaurantIDPath)
                output += "<input type='submit' value='Delete'>"
                output += "</form></body></html>"

                self.wfile.write(output.encode())


            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split("/")[2]
                print(restaurantIDPath)

                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if myRestaurantQuery != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = "<html><body>"
                    output += "<h1>"
                    output += myRestaurantQuery.name
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/{}/edit' >".format(restaurantIDPath)
                    output += "<input name = 'newRestaurantName' type='text' placeholder = '{}' >".format(myRestaurantQuery.name)
                    output += "<input type = 'submit' value = 'Rename'>"
                    output += "</form>"
                    output += "</body></html>"

                    self.wfile.write(output.encode())

            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = "<html><body>"
                output += "<a href = '/restaurants/new'><h1>Make new restaurants</h1></a>"
                output += "<hr>"
                restaurants = session.query(Restaurant).all()
                for restaurant in restaurants:
                    output += "<p>{}<p>".format(restaurant.name)
                    output += "<a href='/restaurants/{}/edit'><p>Edit</p></a>".format(restaurant.id)
                    output += "<a href='/restaurants/{}/delete'><p>Delete</p></a>".format(restaurant.id)
                    output += "<hr>"

                output += "</body></html>"

                self.wfile.write(output.encode())
                return

        except IOError:
            self.send_error(404, "File Not Found {}".format(self.path))

    def do_POST(self):
        if self.path.endswith("/new"):
            ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
            if ctype == 'multipart/form-data':
                pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('newRestaurantName')[
                    0].decode('utf-8')
            newRestaurant = Restaurant(name=messagecontent)
            session.add(newRestaurant)
            session.commit()
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()
        
        if self.path.endswith("/edit"):
            ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
            if ctype == 'multipart/form-data':
                pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('newRestaurantName')[
                    0].decode('utf-8')
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if myRestaurantQuery != []:
                    myRestaurantQuery.name = messagecontent
                    session.add(myRestaurantQuery)
                    session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

        if self.path.endswith("/delete"):
            restaurantIDPath = self.path.split("/")[2]
            myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
            if myRestaurantQuery != []:
                session.delete(myRestaurantQuery)
                session.commit()
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print("Web server running on port {}".format(port))
        server.serve_forever()

    except KeyboardInterrupt:
        print("^C entered, stopping web server...")
        server.socket.close()


if __name__ == "__main__":
    main()
