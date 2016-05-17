#!/usr/bin/env python
"""
Connected Mobility Arena Presentation GUI Prototype.

@author: U{Marina Rantanen<marinar@kth.se>}
"""
import os
import gtk
import pygtk
pygtk.require('2.0')
import pygtk_chart
from pygtk_chart import bar_chart

from sml_world.srv import AddDemand, StartBusRoute
from sml_world.msg import ProjectedDemand
import rospy

import mocap

import sys
import signal
import threading

green = gtk.gdk.color_parse("green")
red = gtk.gdk.color_parse("red")
standardgray = gtk.gdk.Color(red=25000, green=25000, blue=25000, pixel=0)


class CMAWindow(gtk.Window):
    """Create GUI window."""


    def __init__(self):
        gtk.Window.__init__(self)
        self.set_size_request(1820, 950)
        self.set_position(gtk.WIN_POS_CENTER)

        self.base_path = '/home/mma/catkin_ws/src/sml_world/scripts'
        #self.base_path = '/home/dcarballal/catkin/src/sml_world/scripts'

        self.bkg = gtk.Image()
        self.bkgimagepath = self.base_path + '/resources/bkg_light.png'
        self.bkg.set_from_file(self.bkgimagepath)

        self.head = gtk.Image()
        self.headimagepath = self.base_path + '/resources/heading.png'
        self.head.set_from_file(self.headimagepath)

        self.statsimage = gtk.Image()
        self.statsimagepath = self.base_path + '/resources/start.jpg'

        self.closebtn = gtk.Image()
        self.closebtnimagepath = self.base_path + '/resources/closebtn.jpg'
        self.closebtn.set_from_file(self.closebtnimagepath)

        self.statsimage.set_from_file(self.statsimagepath)

        self.hbox_graph = gtk.HBox(False, 0)
        self.hbox_info = gtk.HBox()
        self.vbox = gtk.VBox(False, 0)
        fixed = gtk.Fixed()
        self.add(self.vbox)
        self.vbox.add(fixed)

        self.vbox.pack_start(self.hbox_info, False, False, 1)
        self.hbox_info.pack_end(self.statsimage, True, True, 0)
        self.vbox.pack_start(self.hbox_graph, True, True, 0)


        #Eventwindow = gtk.Label("Events ")
        #Eventwindow.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))

        #DynamicStats = gtk.Label("Dynamic routing stats")
        #DynamicStats.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))

        #StaticStats = gtk.Label("Traffic ")
        #StaticStats.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))

        #PassengerStats = gtk.Label("Passenger stats ")
        #PassengerStats.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))

        queueevent = gtk.Button("Queue on \n highway")
        blacklabel = queueevent.get_children()[0]
        queueevent.modify_bg(gtk.STATE_NORMAL, standardgray)
        blacklabel.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
        queueevent.set_size_request(110, 110)
        queueevent.connect("clicked", self.on_queue_clicked)

        roadevent = gtk.Button("Closed road")
        blacklabel = roadevent.get_children()[0]
        roadevent.modify_bg(gtk.STATE_NORMAL, standardgray)
        blacklabel.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
        roadevent.set_size_request(110, 110)
        roadevent.connect("clicked", self.on_road_clicked)

        heroevent = gtk.Button("National hero\ncelebration")
        blacklabel = heroevent.get_children()[0]
        heroevent.modify_bg(gtk.STATE_NORMAL, standardgray)
        blacklabel.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
        heroevent.set_size_request(110, 110)
        heroevent.connect("clicked", self.on_hero_clicked)

        subwayevent = gtk.Button("Subway\nmeltdown")
        blacklabel = subwayevent.get_children()[0]
        subwayevent.modify_bg(gtk.STATE_NORMAL, standardgray)
        blacklabel.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
        subwayevent.set_size_request(110, 110)
        subwayevent.connect("clicked", self.on_sub_clicked)

        closeButton = gtk.Button()
        #closeButton = gtk.Button("_Close", use_underline=True)
        #blacklabel = closeButton.get_children()[0]
        #closeButton.modify_bg(gtk.STATE_NORMAL, standardgray)
        #blacklabel.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
        #closeButton.set_size_request(187, 44)
        closeButton.set_image(self.closebtn)
        closeButton.connect("clicked", self.on_close_clicked)

        Dynstats = gtk.ScrolledWindow()
        Dynstats.set_size_request(430, 240)
        textbuffer = gtk.TextBuffer()
        textbuffer.set_text('Bus information \n Active buses: 10 '
                            '\n Requested stops: \n Waiting time: 5 minutes \n Travel time: 45 minutes')
        textview = gtk.TextView(buffer=textbuffer)
        Dynstats.add(textview)

        Dynvalues = gtk.ScrolledWindow()
        Dynvalues.set_size_request(80, 240)
        textbuffer = gtk.TextBuffer()
        textbuffer.set_text(' \n 4 \n 57 \n \n +50 ')
        textview2 = gtk.TextView(buffer=textbuffer)
        Dynvalues.add(textview2)

        self.Passtats = gtk.ScrolledWindow()
        self.Passtats.set_size_request(430, 240)
        passtext = gtk.TextBuffer()
        passtext.set_text('Static bus routing equivalent: \n Active buses: 3 \n Waiting time: 30 minutes \n Travel time: 45 minutes ')
        self.passview = gtk.TextView(buffer=passtext)
        self.Passtats.add(self.passview)

        fixed.put(self.head, 60, 10)

        fixed.put(queueevent, 60, 135)
        fixed.put(roadevent, 60, 250)

        fixed.put(heroevent, 180, 135)
        fixed.put(subwayevent, 180, 250)

        fixed.put(closeButton, 1360, 135)


        #fixed.put(Eventwindow, 60, 40)
        #fixed.put(PassengerStats, 60, 365)
        #fixed.put(DynamicStats, 450, 40)
        #fixed.put(StaticStats, 450, 365)

        fixed.put(Dynstats, 340, 135)
        #fixed.put(Dynvalues, 1041, 185)
        fixed.put(self.Passtats, 775, 135)
        self.demand = [('now', 7, 'Now'),
            ('plusone', 15, '+1h'),
            ('plustwo', 24, '+2h'),
            ('plusthree', 15, '+3h'),
            ('plusfour', 10, '+4h')]
        self.passenger_graph(-1)

        rospy.Subscriber('/projected_demand', ProjectedDemand, self.update_proj_demand)
        print('Subscriber set up')

    def on_queue_clicked(self, button):
        print("\"Queue event\" button was clicked")

        statsimagepath = self.base_path + '/resources/queue.jpg'
        self.statsimage.set_from_file(statsimagepath)
        event_id = 1
        self.stat_graph(event_id)
        self.passenger_graph(event_id)
#        os.system("rosservice call spawn_vehicle"{vehicle_id: 2, class_name: 'Bus', x: 0.0, y: 0.0, yaw: 0.0, v: 10.0, node_id: -504, toggle_sim: true}"")

    def on_road_clicked(self, button):
        print("\"Road event\" button was clicked")
        statsimagepath = self.base_path + '/resources/stop.jpg'
        self.statsimage.set_from_file(statsimagepath)
        event_id = 2
        self.stat_graph(event_id)
        self.passenger_graph(event_id)

    def on_hero_clicked(self, button):
        statsimagepath = self.base_path + '/resources/hero.jpg'
        self.statsimage.set_from_file(statsimagepath)
        event_id = 3
        self.stat_graph(event_id)
        self.passenger_graph(event_id)
        self.add_demand_to_model(-274, 40)
        self.add_demand_to_model(-302, 30)
        self.add_demand_to_model(-444, 20)
        rospy.wait_for_service('/start_bus_route')
        start_bus = rospy.ServiceProxy('/start_bus_route', StartBusRoute)
        start_bus([-274,-302,-444], 814, -444)

    def update_proj_demand(self, data):
        print('UPDATING DEMAND')
        proj_demand = list(data.next4hoursdemand)
        if not proj_demand:
            return
        print(proj_demand)
        self.demand = [('now', proj_demand[0], 'Now'),
            ('plusone', proj_demand[1], '+1h'),
            ('plustwo', proj_demand[2], '+2h'),
            ('plusthree', proj_demand[3], '+3h'),
            ('plusfour', proj_demand[4], '+4h'),
           ]
        self.passenger_graph(-1)

    def add_demand_to_model(self, bus_id, demand_added):
        rospy.wait_for_service('/add_demand')
        d_add = rospy.ServiceProxy('/add_demand', AddDemand)
        d_add(bus_id, demand_added)

    def on_sub_clicked(self, button):
        print("\"Subway event\" button was clicked")
#        self.statsimage.set_from_file("concertstats.jpg")
        statsimagepath = self.base_path + '/resources/subway.jpg'
        self.statsimage.set_from_file(statsimagepath)
        event_id = 4
        self.stat_graph(event_id)
        self.passenger_graph(event_id)

    

        '''
    def demand(self, event_id):
        demand = [('now', 100, 'Now'),
            ('plusone', 52, '+1h'),
            ('plustwo', 20, '+2h'),
            ('plusthree', 65, '+3h'),
            ('plusfour', 78, '+4h'),
           ]
        return demand
        '''
    def stats(self, event_id):
        #Routing statistics
        if event_id == 0:
            stats = [('waitingtime', 0, 'Waiting time'),
                ('traveltime', 0, 'Travel time'),
                ('fuelconsumption', 0, 'Fuel consumption'),
                ('cost', 0, 'Cost'),
               ]
        elif event_id == 1:
            stats = [('waitingtime', 80, 'Waiting time'),
                ('traveltime', 52, 'Travel time'),
                ('fuelconsumption', 101, 'Fuel consumption'),
                ('cost', 65, 'Cost'),
               ]
        elif event_id == 2:
            stats = [('waitingtime', 90, 'Waiting time'),
                ('traveltime', 78, 'Travel time'),
                ('fuelconsumption', 150, 'Fuel consumption'),
                ('cost', 120, 'Cost'),
               ]
        elif event_id == 3:
            stats = [('waitingtime', 43, 'Waiting time'),
                ('traveltime', 67, 'Travel time'),
                ('fuelconsumption', 89, 'Fuel consumption'),
                ('cost', 100, 'Cost'),
               ]
        elif event_id == 4:
            stats = [('waitingtime', 86, 'Waiting time'),
                ('traveltime', 98, 'Travel time'),
                ('fuelconsumption', 82, 'Fuel consumption'),
                ('cost', 100, 'Cost'),
               ]
        return stats

    def stat_graph(self, event_id):
        data = self.stats(event_id)

        statchart = bar_chart.BarChart()

        statchart.title.set_text('Impact of dynamic routing')
        statchart.grid.set_visible(True)
        statchart.grid.set_line_style(pygtk_chart.LINE_STYLE_DOTTED)
        statchart.set_mode(bar_chart.MODE_VERTICAL)

        for bar_info in data:
            bar = bar_chart.Bar(*bar_info)
            if bar_info[1] <= 100:
                bar.set_color(green)
            elif bar_info[1] > 100:
                bar.set_color(red)
            statchart.add_bar(bar)
            #statchart.queue_draw()


        self.hbox_graph.pack_start(statchart, True, True, 0)

        #width, height = 400, 300
        #box.set_size_request(width, height)

        def cb_bar_clicked(statchart, bar):
            print "Bar '%s' clicked." % bar.get_label()

        statchart.connect("bar-clicked", cb_bar_clicked)
        statchart.show()

    def passenger_graph(self, event_id):
        # data = self.demand(event_id)
        barchart = bar_chart.BarChart()

        barchart.title.set_text('Estimated number of passengers upcoming hours')
        barchart.grid.set_visible(True)
        barchart.grid.set_line_style(pygtk_chart.LINE_STYLE_DOTTED)
        barchart.set_mode(bar_chart.MODE_HORIZONTAL)
        rospy.logwarn(self.demand)

        for bar_info in self.demand:
            bar_info = list(bar_info)
            bar = bar_chart.Bar(bar_info[0], bar_info[1], bar_info[2])
            bar.set_color(standardgray)
            barchart.add_bar(bar)
            barchart.queue_draw()

        for widget in self.hbox_graph.get_children():
            self.hbox_graph.remove(widget)

        self.hbox_graph.pack_start(barchart)

        def cb_bar_clicked(barchart, bar):
            print "Bar '%s' clicked." % bar.get_label()

        barchart.connect("bar-clicked", cb_bar_clicked)

        barchart.show()


#    def on_redbus_clicked(self, button):
#        print("\"Red bus\" button was clicked")
#    #        os.system("rosservice call spawn_vehicle \"{vehicle_id: 1, class_name: 'Bus', x: 0.0, y: 0.0, yaw: 0.0, v: 10.0, node_id: -384, toggle_sim: true}\" ")
#        os.system("rosservice call spawn_vehicle \"{vehicle_id: 1, class_name: 'Bus', x: 0.0, y: 0.0, yaw: 0.0, v: 10.0, node_id: -542, toggle_sim: true}\" ")

#    def on_greenbus_clicked(self, button):
#        print("\"Green bus\" button was clicked")
#    #        os.system("rosservice call spawn_vehicle \"{vehicle_id: 2, class_name: 'Bus', x: 0.0, y: 0.0, yaw: 0.0, v: 12.0, node_id: -100, toggle_sim: true}\" ")
#        os.system("rosservice call spawn_vehicle \"{vehicle_id: 2, class_name: 'Bus', x: 0.0, y: 0.0, yaw: 0.0, v: 12.0, node_id: -300, toggle_sim: true}\" ")

#    def on_yellowbus_clicked(self, button):
#        print("\"Yellow bus\" button was clicked")
#        os.system("rosservice call spawn_vehicle \"{vehicle_id: 3, class_name: 'Bus', x: 60.0, y: -60.0, yaw: 0.0, v: 15.0, node_id: -220, toggle_sim: true}\" ")

#    def on_stop_clicked(self, button):
#        print("\"Stop\" button was clicked")

#    def on_log_clicked(self, button):
#        def on_close_clicked(button):
#            print("Closing application")
#            gtk.main_quit()
#            print("\"Log\" button was clicked")
#            logwin = gtk.Window()
#        logwin.set_size_request(500, 500)
#        vbox = gtk.VBox()
#        fixed = gtk.Fixed()
#        logwin.add(vbox)
#        vbox.add(fixed)
#        closeButton = gtk.Button("_Close", use_underline=True)
#        closeButton.connect("clicked", on_close_clicked)
#        fixed.put(closeButton, 0, 0)
#        logwin.show_all()

    def on_close_clicked(self, button):
        print("Closing application")
        gtk.main_quit()


def qualisys_pos(body_id, x, y, yaw):
    drawingarea = gtk.DrawingArea()
    drawingarea.set_size_request(600, 300)
    drawable = drawingarea.window


def qualisys_info():
    """
    Qualisys data listener.
    @param qs_body:
    """
    stop = False

    def signal_handler(signal, frame):
        stop = True
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    Qs = mocap.Mocap(info=1)
    bodies = Qs.find_available_bodies(printinfo=1)

    #pick the first valid body
    id_body = Qs.get_id_from_name("Iris2")
    body = mocap.Body(Qs, id_body)
    pose = body.getPose()
    qsid = pose['id']
    qsx = pose['x']
    qsy = pose['y']
    qsyaw = pose['yaw']

    qualisys_pos(qsid, qsx, qsy, qsyaw)

    #while not stop:
        #pose = body.getPose()

rospy.init_node('GUI')
win = CMAWindow()
win.connect("delete-event", gtk.main_quit)
win.show_all()
gtk.gdk.threads_init()
thread = threading.Thread(target=gtk.main)
thread.start()
rospy.spin()
