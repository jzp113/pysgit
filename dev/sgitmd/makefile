PYTHON_VERSION = 2.7
PYTHON_INCLUDE = /usr/include/python$(PYTHON_VERSION)
 
# location of the Boost Python include files and library
 
BOOST_INC = /usr/include/boost
Sgit_INC_DIR = ../lib/sgitapi/linux_x64
LIBS= -lsgitquotapi -lsgittradeapi
INC_DIR= ../
 
# compile mesh classes
TARGET = sgitmd
 
$(TARGET).so: $(TARGET).o
	g++ -lpthread -shared -Wl,--export-dynamic $(TARGET).o $(LIBS) -lboost_python -lboost_thread -o $(TARGET).so
 
$(TARGET).o: $(TARGET).cpp
	g++ -I$(PYTHON_INCLUDE) -I$(BOOST_INC) -I$(INC_DIR) -I$(Sgit_INC_DIR) -fPIC -c $(TARGET).cpp

clean:
	rm *.o *.so