#! /usr/bin/env python



from twisted.web import server, static
from twisted.web.server import Site,NOT_DONE_YET
from twisted.web.resource import Resource
from twisted.internet import reactor,defer,threads


import re
import cgi
import time
import sys
import math


import twisted.internet.reactor
import entangled.dtuple
import hashlib


node = None
post = None


userUsername = None
userEmail = None
userStatus = None

usersignup = None

################# Web interface part ######################################################

class AboutPage(Resource):
    def render_GET(self, request):
        #global  userEmail
        #global userUsername
        #global userStatus

        template = open('about.html')
        templater = str(template.read())

        e =re.sub(r'{{email}}',userEmail,templater)
        s =re.sub(r'{{status}}',userStatus,e)
        n = re.sub(r'{{user}}',userUsername,s)

        request.write(n)
        #request.finish()


class HomePage(Resource):
    def render_GET(self, request):
        template = open('index.html')
        return template.read()

    def render_POST(self, request):
        userpost = cgi.escape(request.args["userpost"][0])
        putPost(userpost)
        return '<script>alert(\"Your tweet has been posted\" );window.history.back();</script>'
''''
class FormPage(Resource):
    def render_GET(self, request):
        #getValue()
        template = open('home.html')
        return template.read()


    def render_POST(self, request):
        userpost = cgi.escape(request.args["userpost"][0])
        putPost(userpost)
        return '<script>alert(\"Your tweet has been posted\" );window.history.back();</script>'
'''

class IndexPage(Resource):
    def render_GET(self,request):
        template = open('welcome.html')
        return template.read()

    def render_POST(self,request):
        global node



        username = cgi.escape(request.args["username"][0])
        password = cgi.escape(request.args["password"][0])

        print username + password
        print 'Started login'

        key = str(username)
        h = hashlib.sha1()
        h.update(key)
        hKey = h.digest()

        emailKey = str(username+'_email')
        h2 = hashlib.sha1()
        h2.update(emailKey)
        hEmail = h2.digest()

        statusKey = str(username+'_status')
        h3 = hashlib.sha1()
        h3.update(statusKey)
        hStatus = h3.digest()



        def checkValue(result,hkey,username,password,request):
            global userUsername
            global userEmail
            global userStatus
            if type(result) == dict:
                value = result[hKey]
                if value == password:
                    print 'Ok login success'
                    userUsername = username
                    print userUsername
                    #request.write('<script> window.location=\"index\"; </script>')
                    #request.finish()

                else:
                    print 'Incorrect login'
                    request.write("<script>alert(\"Incorrect login\");window.history.back();</script>")
                    request.finish()
            else:
                print 'No such user'
                request.write("<script>alert(\"No such user\");window.history.back();</script>")
                request.finish()

        def getEmail(result,hEmail,request):
            global userUsername
            global userEmail
            global userStatus
            if type(result) == dict:
                value = result[hEmail]
                userEmail = value
                print value


        def getStatus(result,hStatus,request):
            global userUsername
            global userEmail
            global userStatus
            if type(result) == dict:
                value = result[hStatus]
                print value
                userStatus = value
                request.write('<script> window.location=\"index\"; </script>')
                request.finish()

        df = node.iterativeFindValue(hKey)
        df.addCallback(checkValue,hKey,username,password,request)

        df2 = node.iterativeFindValue(hEmail)
        df2.addCallback(getEmail,hEmail,request)

        df3 = node.iterativeFindValue(hStatus)
        df3.addCallback(getStatus,hStatus,request)

        return NOT_DONE_YET



class SignupPage(Resource):
    def render_GET(self,request):
        template = open('signup.html')
        return template.read()

    def render_POST(self,request):
        global node
        username = cgi.escape(request.args["username"][0])
        password = cgi.escape(request.args["password"][0])
        email = cgi.escape(request.args["email"][0])
        status = cgi.escape(request.args["status"][0])

        print username + password + email + status

        print 'Started signup'
        key = str(username)
        h = hashlib.sha1()
        h.update(key)
        hKey = h.digest()

        emailKey = str(username+ '_email')
        emailHash = hashlib.sha1()
        emailHash.update(emailKey)
        hEmail = emailHash.digest()

        statusKey = str(username+ '_status')
        statusHash = hashlib.sha1()
        statusHash.update(statusKey)
        hStatus = statusHash.digest()

        follownumKey = str(username+ '_follownum')
        follownumHash = hashlib.sha1()
        follownumHash.update(follownumKey)
        hFollownum = follownumHash.digest()

        def showValue(result,username,hEmail,hStatus,hFollownum,password,email,status,request):

            if type(result) == dict:
                value = result[hKey]
                print 'User already exist'
                request.write("<script>alert(\"User already exist\");window.history.back();</script>")
                request.finish()
            else:
                df2 = node.iterativeStore(hKey, password)
                df3 = node.iterativeStore(hEmail,email)
                df4 = node.iterativeStore(hStatus,status)
                df5 = node.iterativeStore(hFollownum,'0')
                print 'New user created'
                request.write("<script>alert(\"New user created\");window.history.back();</script>")
                request.finish()

        df = node.iterativeFindValue(hKey)
        df.addCallback(showValue,hKey,hEmail,hStatus,hFollownum,password,email,status,request)
        return NOT_DONE_YET



################ End of web interface part ##################################################





def getOption():
    print '1.Post\n2.Retrieve\n3.Exit'
    option = int(raw_input("Enter your option:"))
    if option==1:
        putPost()
    elif option==2:
        getValue()
    elif option==3:
        print '\nStopping Kademlia node.....'
        twisted.internet.reactor.stop()

def putPost(userpost):
    global userUsername
    global node
    print "Startrd posting method"
    key = str(userUsername+'_num')
    h = hashlib.sha1()
    h.update(key)
    hKey = h.digest()

    def showValue(result):

        if type(result) == dict:
            value = result[hKey]
        else:
            value = '0'
        #print str(value)
        numpost = int(value)
        if numpost > 0:
            #value = str(raw_input("Post:"))
            value = str(userpost)
            numpost+=1
            user = userUsername + '_'+ str(numpost)
            print user
            storeValue(user,value,key,str(numpost),0)
        else:
            #value = str(raw_input("Post:"))
            value = str(userpost)
            numpost = 1
            user = userUsername + '_'+ str(numpost)
            print user
            storeValue(user,value,key,str(numpost),0)

    df = node.iterativeFindValue(hKey)
    df.addCallback(showValue)


def storeValue(key,value,originalkey,numpost,flag):
    global node
    h = hashlib.sha1()
    h.update(key)
    hKey = h.digest()



    def completed(result):
        print 'Value Stored'
        if flag == 0:
            storeValue(originalkey,str(numpost),originalkey,numpost,1)
        else:
            print 'OK'
            pass
            #getOption()
    df = node.iterativeStore(hKey, value)
    df.addCallback(completed)


def getEachPost(originalkey,key,numpost):
    global node
    global post
    h = hashlib.sha1()
    h.update(key)
    hKey = h.digest()

    def showValue(result,originalkey,numpost):
        if type(result) == dict:
            value = result[hKey]
        else:
            value = 0


        if numpost ==0:
            pass
            #getOption()
        else:
            #print 'Post :%s' %value
            post = post + value
            print 'Post :%s' %post
            numpost-=1
            key =originalkey + '_' + str(numpost)
            getEachPost(originalkey,key,int(numpost))

    df = node.iterativeFindValue(hKey)
    df.addCallback(showValue,originalkey,numpost)

def getValue():
    global node

    #key = str(raw_input("Username:"))
    key = str("anagh")
    h = hashlib.sha1()
    h.update(key)
    hKey = h.digest()
    originalkey = key

    def showValue(result,originalkey,key):
        if type(result) == dict:
            value = result[hKey]
        else:
            value = 0
        value = int(value)
        if value == 0:
            print 'No post yet'
            #getOption()
        else:
            key = key + '_' + str(value)
            getEachPost(originalkey,key,int(value))

    df = node.iterativeFindValue(hKey)
    df.addCallback(showValue,originalkey,key)




if __name__ == '__main__':
    # if len(sys.argv) < 2:
    #     print 'Usage:\n%s UDP_PORT  [KNOWN_NODE_IP  KNOWN_NODE_PORT]' % sys.argv[0]
    #     print 'or:\n%s UDP_PORT  [FILE_WITH_KNOWN_NODES]' % sys.argv[0]
    #     print '\nIf a file is specified, it should containg one IP address and UDP port\nper line, seperated by a space.'
    #     sys.exit(1)
    # try:
    #     int(sys.argv[1])
    # except ValueError:
    #     print '\nUDP_PORT must be an integer value.\n'
    #     print 'Usage:\n%s UDP_PORT  [KNOWN_NODE_IP  KNOWN_NODE_PORT]' % sys.argv[0]
    #     print 'or:\n%s UDP_PORT  [FILE_WITH_KNOWN_NODES]' % sys.argv[0]
    #     print '\nIf a file is specified, it should contain one IP address and UDP port\nper line, seperated by a space.'
    #     sys.exit(1)

    # if len(sys.argv) == 4:
    #     knownNodes = [(sys.argv[2], int(sys.argv[3]))]
    # elif len(sys.argv) == 3:
    #     knownNodes = []
    #     f = open(sys.argv[2], 'r')
    #     lines = f.readlines()
    #     f.close()
    #     for line in lines:
    #         ipAddress, udpPort = line.split()
    #         knownNodes.append((ipAddress, int(udpPort)))
    # else:
    #     knownNodes = None

    #node = entangled.dtuple.DistributedTupleSpacePeer( udpPort=int(sys.argv[1]) )
    knownNodes = [("192.168.0.103", int("8000"))]
    node = entangled.dtuple.DistributedTupleSpacePeer( udpPort=int("6198") )
    node.joinNetwork(knownNodes)
    #twisted.internet.reactor.callLater(0, getOption)
    print '\n\n*** Wrobel - A P2P Microblogging Platform ***\n\n'

##################################### Call rendering corresponding pages #######################
    root = Resource()
    root.putChild("",IndexPage())
    root.putChild("signup",SignupPage())
    root.putChild("index",HomePage())
    root.putChild("about",AboutPage())

################# Linking static files ########################################

    root.putChild('img', static.File("./img"))
    root.putChild('css', static.File("./css"))
    root.putChild('js', static.File("./js"))
    root.putChild('fonts', static.File("./fonts"))

############################# End of call #######################################################
    wrobelsite = Site(root)

    twisted.internet.reactor.listenTCP(8881, wrobelsite)
    twisted.internet.reactor.run()
    
