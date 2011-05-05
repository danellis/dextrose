Tutorial
========

Introduction
------------
Dextrose is a WSGI-based web application framework built on top of Werkzeug. It's still in a very experimental stage, so it isn't well documented yet. One of its main features is a tight integration with Javascript widgets on the client side. For example, one might write a page class like this (the database access is MongoEngine):

.. code-block:: python

   class MapPage(Page):
       gmap = GoogleMap(size=(400, 300))
        
       def get(self, place_id):
           place = Place.objects.with_id(place_id)
           self['map'] = self.gmap(place.location, place.markers)
           return self.render('pages/map.html')

       def on_gmap_click(self, event, place_id):
           place = Place.objects.with_id(place_id)
           place.markers.append([event.lat, event.lng])
           place.save()
           return "put_marker_on_map(%f, %f)" % (event.lat, event.lng)

When the map widget in the browser makes an AJAX request in response to a click event, the page is reinstantiated on the server, and its on_gmap_click method is called with the event data, and any arguments from the URL path of the containing page. It returns a piece of Javascript that is executed in the browser.
