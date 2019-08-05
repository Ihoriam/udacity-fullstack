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
            if self.path.endswith("/restaurants/new"):
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
                    output += "<a href='#'><p>Edit</p></a>"
                    output += "<a href='#'><p>Delete</p></a>"
                    output += "<hr>"

                output += "</body></html>"

                self.wfile.write(output.encode())
                return

            # if self.path.endswith("/hola"):
            #     self.send_response(200)
            #     self.send_header('Content-type', 'text/html')
            #     self.end_headers()
            #     output = ""
            #     output += "<html><body>"
            #     output += "<h1>&#161 Hola !</h1>"
            #     output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
            #     output += "</body></html>"
            #     self.wfile.write(output.encode())
            #     print(output)
            #     return

        except IOError:
            self.send_error(404, "File Not Found {}".format(self.path))

    def do_POST(self):
        if self.path.endswith("/new"):
            print("do_post")
            self.send_response(301)
            self.send_header('Location', '/restaurants')
            self.end_headers()
            output = ""
            output += "<html><body>"
            output += "Create new restaurant"
            output += '<h2> Enter the restaurant name </h2>'
            output += "<form method='POST' enctype='multipart/form-data' action='/restaurants'><input name='newRestaurantName' type='text'><input type='submit' value='Submit'></form>"
            output += "</body></html>"

            ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
            if ctype == 'multipart/form-data':
                pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('newRestaurantName')[
                    0].decode('utf-8')
            print("Passed if")
            newRestaurant = Restaurant(name=messagecontent)
            session.add(newRestaurant)
            session.commit()
            print(messagecontent)
            self.wfile.write(output.encode())


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
