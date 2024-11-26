LFLAGS = -L$(ROOTSYS)/lib -lCore -lRIO -lEG -lNet -lHist -lGraf -lGraf3d -lGpad -lTree -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lGui -lMinuit -lm -ldl

CFLAGS = `root-config --cflags`

TARGET = corsikaConverter

default: $(TARGET)

$(TARGET): $(TARGET).cc
	g++ -O2 -Wno-deprecated $(TARGET).cc -o corsikaConverter $(CFLAGS) $(LFLAGS) -rdynamic -Wall

clean:
	$(RM) corsikaConverter
