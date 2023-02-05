# COEN317 Distributed System #Programming Assignment 1
**@Huiyu Liu W1648753**

## Description:
This is a description of a programming assignment to build a functional web server. The assignment aims to teach the basics of distributed programming, client/server structures, and high-performance server building. The server listens for connections on a socket and uses a simple text-based protocol for clients to retrieve files. The server translates relative filenames to absolute filenames in the local filesystem and returns HTTP error messages as needed. The assignment requires support for HTTP/1.0 and HTTP/1.1, images, and appropriate error messages but not script parsing or HTTP POST requests. A multi-threaded approach with pthreads library is suggested for incoming connections.

## Submitted File:
1. Home - Santa Clara University_files
    Include all the files index.html needs.
2. index.html
    source of www.scu.edu
3. socket_server.py
    web server code which helps to run w.scu.edu on localhost:port
4. README.txt
    A brief description of the assignment and how to use\

## HOW TO RUN THE PROGRAM?
1. Download 
 from tar czvf PA1-Huiyu_Liu.tar.gz scufile
2. Open terminal and cd to scufile
3. run `./server -document_root "/Users/sandy/Desktop/scufile" -port 8888`
4. open `localhost:8888` on browser