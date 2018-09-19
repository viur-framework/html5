TRLANGOPTS = --kwargs --xglobs --opov --tconv
TRCOMPOPTS = -n -a 

SOURCE = html5.py

TARGETDIR = __target__

OUTPUT = $(patsubst %.py,$(TARGETDIR)/%.js,$(SOURCE))

all: $(OUTPUT)

clean:
	rm -rf $(TARGETDIR) __pycache__

$(OUTPUT): $(SOURCE)
	transcrypt $(TRCOMPOPTS) $(TRLANGOPTS) $(patsubst %.py,%,$(SOURCE))

