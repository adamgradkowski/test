import arcpy
import pythonaddins
import numpy
import networkx as nx

workspace = arcpy.env.workspace
#desc = arcpy.Describe(workspace)
#path_workspace = desc.path
#polyline_path = path_workspace



class ButtonClass3(object):
    """Implementation for Rysuj_Droge_addin.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pass

class ToolClass2(object):
    """Implementation for Rysuj_Droge_addin.tool (Tool)"""
    def __init__(self):
        self.enabled = True
        self.shape = "Line" # Can set to "Line", "Circle" or "Rectangle" for interactive shape drawing and to activate the onLine/Polygon/Circle event sinks.
        self.cursor = 3
    def onLine(self, line_geometry):

        mxd = arcpy.mapping.MapDocument("Current")
        punkty = arcpy.mapping.ListLayers(mxd)

        #if arcpy.Exists(polyline_path + "\droga.shp"):
        #   arcpy.Delete_management(polyline_path + "\droga.shp")

        #arcpy.CreateFeatureclass_management(polyline_path, "droga", "POLYLINE")


        points = []
        edges = []

        i = 0
        pkt = []
        spr = []
        spr2 = []
        linia_id = []
        linia_pocz = []
        linia_koniec = []
        #A: Autostrady 120
        #S: Ekspresowe 120
        #GP: Glowne ruchu [rzyspieszonego 70
        #G: Glowne 60
        #Z: Zbiorcze 60
        #L: Lokalne 40
        #I: Dojazdowe 30
        odl = []
        odlk = []
        array = arcpy.Array()
        dl = []
        with arcpy.da.SearchCursor(punkty[0], ["FID","SHAPE@","SHAPE@LENGTH", "klasaDrogi"]) as street_data:
            for s in street_data:
                id_part = str(s[1].firstPoint.X)
                id_part_ = str(s[1].firstPoint.Y)
                id = id_part[0:7] + id_part_[0:7]
                p = (id, (s[1].firstPoint.X, s[1].firstPoint.Y))
                if p not in pkt:
                    pkt.append(p)

                id_part = str(s[1].lastPoint.X)
                id_part_ = str(s[1].lastPoint.Y)
                idk = id_part[0:7] + id_part_[0:7]
                p = (id, (s[1].lastPoint.X, s[1].lastPoint.Y))
                V = 0
                if p not in pkt:
                    pkt.append(p)
                if s[3] == 'A':
                    V = 120
                elif s[3] =='S':
                    V = 90
                elif s[3] == 'GP':
                    V = 70
                elif s[3] == 'G':
                    V = 60
                elif s[3] == 'Z':
                    V = 60
                elif s[3] == 'L':
                    V = 40
                elif s[3] == 'I':
                    V = 35
                else:
                    V = 45
                edges.append([s[0], id, idk, s[2], V])

        for pt in pkt:
            odlp = numpy.sqrt((pt[1][0] - line_geometry.firstPoint.X) ** 2 + (pt[1][1] - line_geometry.firstPoint.Y) ** 2)
            odl_k = numpy.sqrt((pt[1][0] - line_geometry.lastPoint.X) ** 2 + (pt[1][1] - line_geometry.lastPoint.Y) ** 2)
            odl.append(odlp)
            odlk.append(odl_k)


        n_odl = numpy.min(odl)
        n_odlk = numpy.min(odlk)
        n_odl_i = odl.index(n_odl)
        n_odl_ik = odlk.index(n_odlk)
        ok = pkt[n_odl_i]
        pkt_P = ok[0]
        okk = pkt[n_odl_ik]
        pkt_K = okk[0]
        print(edges)


        def Create_Graph(start, end, node, edge, name, type = 'shortest'):
            G = nx.Graph()
            for p in node:
                G.add_node(p[0], pos=(p[1][0], p[1][1]))
            if type == 'shortest':
                for e in edge:
                    G.add_edge(e[1], e[2], weight = e[3], id=e[0])
            elif type =='fastest':
                for e in edge:
                    G.add_edge(e[1], e[2], weight = (e[3]/1000)/e[4], id=e[0])
            def dist(a, b):
                x1= 0
                y1= 0
                x2= 0
                y2= 0
                for e in node:
                    if e[0] == a:
                        x1 = e[1][0]
                        y1 = e[1][1]
                    if e[0] == b:
                        x2 = e[1][0]
                        y2 = e[1][1]
                return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

            path = nx.astar_path(G, start, end, dist, weight='weight')
            length_path = nx.astar_path_length(G, start, end, dist, weight='weight')
            #print("dlugosc trasy " + name + ": " + str(length_path))
            tab = []
            for i in range(0, len(path) - 1):
                tab.append(G[path[i]][path[i + 1]]['id'])
            query = '"FID" IN ('
            for i in tab:
                query = query + str(i) + ', '
            query = query[:-2]
            query += ')'
            if arcpy.Exists(name):
                arcpy.Delete_management(name)
            arcpy.MakeFeatureLayer_management(punkty[0], name, query)
            time = 0
            for t in tab:
                for e in edge:
                    if t == e[0]:
                        e[3] *= 1.3
                        time += ((e[3]/1000)/e[4]) * 60
            #print("czas " + name + ": " + str(time) + " min")
            return edge

            '''
        G = nx.Graph()
        for p in pkt:
            G.add_node(p[0],pos = (p[1][0],p[1][1]))
        for e in edges:
           G.add_edge(e[1] , e[2] , weight = e[3], id = e[0])

        path = nx.astar_path(G, pkt_P, pkt_K ,weight = 'weight')
        tab = []
        print(path)
        for i in range(0,len(path)-1):
            tab.append(G[path[i]][path[i+1]]['id'])
        print(tab)
        query = '"FID" IN ('
        for i in tab:
            query = query + str(i) + ', '
        query = query[:-2]
        query += ')'
        print(query)
        if arcpy.Exists("test"):
            arcpy.Delete_management("test")

        arcpy.MakeFeatureLayer_management(punkty[0], "test" , query)

        '''
        #Create_Graph(pkt_P, pkt_K, pkt, edges, 'droga_najkrotsza')
        #for i in (1, 2):
        #   Create_Graph(pkt_P, pkt_K, pkt, edges, "droga_alternatywna" + str(i))
        Create_Graph(pkt_P, pkt_K, pkt, edges, 'droga_najszybsza',"shortest")
        for i in (1, 2):
           Create_Graph(pkt_P, pkt_K, pkt, edges, "droga_alternatywna" + str(i),"shortest")





        '''

        array = arcpy.Array()

        array.add(line_geometry.firstPoint)
        for p in path:
            for py in pkt:
                if p == py[0]:
                    array.add(arcpy.Point(py[1][0],py[1][1]))
        array.add(line_geometry.lastPoint)
        polyline_obj = arcpy.Polyline(array)
        
        path_fc = polyline_path + "\droga.shp"
        cursor = arcpy.da.InsertCursor(path_fc, ['Shape@'])
        cursor.insertRow([polyline_obj])
        del cursor
        '''
        '''
        row_values = []
        for p in pkt:
            row_values.append((p[2],(p[0],p[1])))

        cursor = arcpy.da.InsertCursor('C:/Users/agradkowski/Desktop/ARCPY/texas.gdb/counties',['OBJECTID', 'SHAPE@XY'])

        for row in row_values:
            cursor.insertRow(row)

        del cursor
        '''


        '''
        Tworze trasy alternatywne najpierw musze zwiekszych wczesniejsze o jakiej poltora

        
        for i in tab:
            ind = linia_id.index(i)
            print(dl[ind])
        for i in tab:
            ind = linia_id.index(i)
            dl[ind] *= 1.3
        for i in tab:
            ind = linia_id.index(i)
            print(dl[ind])
        del edges[:]
        for i in range(0, len(linia_id)):
            edges.append((linia_id[i], linia_pocz[i], linia_koniec[i], dl[i]))

        G = nx.Graph()
        for p in pkt:
            G.add_node(p[2], pos=(p[0], p[1]))
        for e in edges:
            G.add_edge(e[1], e[2], weight=e[3], id=e[0])

        path = nx.astar_path(G, pkt_P, pkt_K, weight='weight')
        tab = []

        for i in range(1, len(path)):
            tab.append(G[path[i]][path[i - 1]]['id'])
        query = '"FID" IN ('
        for i in tab:
            query = query + str(i) + ', '
        query = query[:-2]
        query += ')'
        if arcpy.Exists("alternatywa"):
            arcpy.Delete_management("alternatywa")

        arcpy.MakeFeatureLayer_management(punkty[0], "alternatywa" , query)
        '''









        '''
        dane_id = []
        dane_x = []
        dane_y = []

        dane_id_E = []
        dane_dl = []
        dane_P = []
        dane_K = []

        dane_P.extend(linia_pocz)
        dane_P.extend(linia_koniec)
        dane_K.extend(linia_koniec)
        dane_K.extend(linia_pocz)
        dane_dl.extend(dl)
        dane_dl.extend(dl)
        dane_id_E.extend(linia_id)
        dane_id_E.extend(linia_id)


        n = 999999999999999999999999999999999999999999999999999999999999999  # nieskonczonosc
        S = []
        Q = []
        f = []
        g = []
        p = []

        for i in range(0, len(pkt)):
            f.append(n)
            g.append(n)
            p.append(-1)
            dane_id.append(pkt[i].ID)
            dane_x.append(pkt[i].X)
            dane_y.append(pkt[i].Y)
        print("strefa pierwsza")
        ok = pkt[n_odl_i]
        pkt_P = ok.ID
        okk = pkt[n_odl_ik]
        pkt_K = okk.ID
        w_p = pkt_P

        w_k = ''

        S.append(dane_id[dane_id.index(w_p)])
        g[dane_id.index(w_p)] = 0
        f[dane_id.index(w_p)] = 0
        del ok
        del okk
        del linia_id
        del linia_pocz
        del linia_koniec

        while w_p != pkt_K:
            # indeks punktu ktorego sprawdzamy - glownego
            wp_i = [i for i, x in enumerate(dane_P) if x == w_p]
            for i in wp_i:
                if dane_K[i] in S:
                    wp_i.remove(i)
            for i in wp_i:
                id_sasiad = dane_id.index(dane_K[i])
                # dodajemy sasiadow ktorych sa polaczenia z glownego
                #Q.append(dane_K[i])
                if i > len(dane_id):
                    i = dane_id.index(dane_K[i])
                odl_p = dane_dl[i]
                heu = numpy.sqrt((dane_x[id_sasiad] - dane_x[dane_id.index(w_p)]) ** 2 + (
                dane_y[id_sasiad] - dane_y[dane_id.index(w_p)]) ** 2)
                g[id_sasiad] = g[dane_id.index(w_p)] + odl_p
                f[id_sasiad] = g[id_sasiad] + heu
                #w_k = dane_id[id_sasiad]
                if f[id_sasiad] > f[dane_id.index(w_p)] + odl_p and w_p != pkt_P:
                    f[id_sasiad] = f[dane_id.index(w_p)] + odl_p
                    p[id_sasiad] = dane_id[dane_id.index(w_p)]
                elif w_p == pkt_P:
                    f[id_sasiad] = f[dane_id.index(w_p)] + odl_p
                    p[id_sasiad] = dane_id[dane_id.index(w_p)]
            szukaj = [item for item in dane_id if item not in S]
            z = []
            for i in szukaj:
                z.append(f[dane_id.index(i)])

            n_w_d = z.index(numpy.min(z))
            del z
            n_w = szukaj[n_w_d]
            del szukaj
            n_w_i = dane_id.index(n_w)
            S.append(dane_id[n_w_i])
            w_p = dane_id[n_w_i]
            print("strefa druga")
        
        tab_do_rysowania = []
        tab_do_rysowania.append(pkt_K)
        w_K = ''
        while w_K != pkt_P:
            i_K = dane_id.index(pkt_K)
            wp_i = [i for i, x in enumerate(dane_id) if x == pkt_K]
            w_K = p[i_K]

            tab_do_rysowania.insert(0, w_K)
            pkt_K = w_K
            print("strefa trzecia")

        print(tab_do_rysowania)
        array.add(line_geometry.firstPoint)

        pkt_srodek = []
        print("strefa 4")
        for t in tab_do_rysowania:
            for py in pkt:
                if t == py.ID:
                    pkt_srodek.append(py)
                    print(py.ID)
        #for py in pkt:
        #    if py.ID in tab_do_rysowania:
        #        pkt_srodek.append(py)
        #        print(py.ID)
        for p in pkt_srodek:
            array.add(p)
        array.add(line_geometry.lastPoint)
        
        polyline_obj = arcpy.Polyline(array)
        path_fc = polyline_path + "\droga.shp"
        cursor = arcpy.da.InsertCursor(path_fc, ['Shape@'])
        cursor.insertRow([polyline_obj])
        del cursor
        '''

        '''
        tab_do_rysowania = []
        while pkt_K != pkt_P:
            d_id = dane_id.index(pkt_K)
            q = p[d_id]
            tab_do_rysowania.append(q)
            # print(q)
            d_id = dane_id.index(q)
            pkt_K = q
        
        tab_do_rysowania = []
        while pkt_K != pkt_P:
            d_id = dane_id.index(pkt_K)
            q = p[d_id]
            tab_do_rysowania.append(q)
            # print(q)
            d_id = dane_id.index(q)
            pkt_K = q
        print(tab_do_rysowania)
        '''
        '''
        array.add(line_geometry.firstPoint)
        array.add(pkt[n_odl_i])

        print("==================================")
        pkt_srodek = []
        
        for py in pkt:
            if py.ID in tab_do_rysowania and py.ID != pkt_P:
                pkt_srodek.append(py)
                print(py.ID)
        
        if numpy.sqrt((pkt_srodek[0].X - pkt[n_odl_i].X) ** 2 + (pkt_srodek[0].Y - pkt[n_odl_i].Y) ** 2) > numpy.sqrt((pkt_srodek[len(pkt_srodek)-1].X - pkt[n_odl_i].X) ** 2 + (pkt_srodek[len(pkt_srodek)-1].Y - pkt[n_odl_i].Y) ** 2):
            print("Uwaga zamienic tutaj posicjami")
            pkt_srodek.reverse()
        
        for p in pkt_srodek:
            array.add(p)





        array.add(pkt[n_odl_ik])
        array.add(line_geometry.lastPoint)
        #for p in array:
        #    print(p.ID)


        
        polyline_obj = arcpy.Polyline(array)
        path_fc = polyline_path + "\droga.shp"
        cursor = arcpy.da.InsertCursor(path_fc, ['Shape@'])
        cursor.insertRow([polyline_obj])
        del cursor
        '''






        '''
        array = arcpy.Array()


        odl = []
        odlk = []
        pkt = []
        i = 0
        with arcpy.da.SearchCursor(punkty[0], ["SHAPE@XY"]) as street_data:
            for p in street_data:
                x,y = p[0]
                pkt.append(arcpy.Point(x,y,ID = i))
                i +=1
                #print("{}, {}".format(x, y))
                odlp = numpy.sqrt((x - line_geometry.firstPoint.X) ** 2 + (y - line_geometry.firstPoint.Y) ** 2)
                odl_k = numpy.sqrt((x - line_geometry.lastPoint.X) ** 2 + (y - line_geometry.lastPoint.Y) ** 2)

                odl.append(odlp)
                odlk.append(odl_k)
        n_odl = numpy.min(odl)
        n_odlk = numpy.min(odlk)
        n_odl_i = odl.index(n_odl)
        n_odl_ik = odlk.index(n_odlk)

        array.add(line_geometry.firstPoint)

        array.add(pkt[n_odl_i])

        dane_id = []
        dane_x = []
        dane_y = []
        dane_P = [0,1,2,3,4,5,0,5,4,3,2,1]
        dane_K = [1,2,3,4,5,0,5,4,3,2,1,0]
        n = 9999999999999999999999999
        S = []
        Q = []
        d = []
        p = []
        for i in range(0,len(pkt)):
            d.append(n)
            p.append(-1)
            dane_id.append(pkt[i].ID)
            dane_x.append(pkt[i].X)
            dane_y.append(pkt[i].Y)
        Q.extend(dane_id)
        ok = pkt[n_odl_i]
        okk = pkt[n_odl_ik]
        pkt_P = ok.ID
        pkt_K = okk.ID
        start = dane_id.index(pkt_P)
        d[start] = 0
        w_p = pkt_P
        S.append(dane_id[dane_id.index(w_p)])
        Q.remove(dane_id[dane_id.index(w_p)])
        d_kopia = []
        d_kopia.extend(d)
        d_kopia[dane_id.index(w_p)] = n

        while len(Q) != 0:
            wp_i = [i for i, x in enumerate(dane_P) if x == w_p]
            for i in wp_i:
                id_sasiad = dane_id.index(dane_K[i])
                odl = numpy.sqrt((dane_x[id_sasiad] - dane_x[dane_id.index(w_p)]) ** 2 + (
                dane_y[id_sasiad] - dane_y[dane_id.index(w_p)]) ** 2)
                if d[id_sasiad] > d[dane_id.index(w_p)] + odl:
                    d[id_sasiad] = d[dane_id.index(w_p)] + odl
                    d_kopia[id_sasiad] = d[dane_id.index(w_p)] + odl
                    p[id_sasiad] = dane_id[dane_id.index(w_p)]

            n_w_d = d_kopia.index(numpy.min(d_kopia))
            w_p = dane_id[n_w_d]
            S.append(dane_id[n_w_d])
            Q.remove(dane_id[n_w_d])
            print(Q)
            d_kopia[n_w_d] = n

        print(Q)
        print(S)
        print(d)
        print(p)

        tab_do_rysowania = []
        while pkt_K != pkt_P:
            d_id = dane_id.index(pkt_K)
            q = p[d_id]
            tab_do_rysowania.append(q)
            print(q)
            d_id = dane_id.index(q)
            pkt_K = q

        for py in pkt:
            if py.ID in tab_do_rysowania:
        

        array.add(line_geometry.lastPoint)


        polyline_obj = arcpy.Polyline(array)

        path_fc = polyline_path + "\droga.shp"
        cursor = arcpy.da.InsertCursor(path_fc, ['Shape@'])
        cursor.insertRow([polyline_obj])
        del cursor
        '''


