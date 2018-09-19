TRLANGOPTS	= --kwargs --xglobs --opov --tconv
TRCOMPOPTS	= -n -a --verbose
TARGETDIR	= __target__

MAIN		= html5.py
SOURCE		= $(MAIN)
OUTPUT		= $(patsubst %.py,$(TARGETDIR)/%.js,$(SOURCE))

all: $(OUTPUT)

clean:
	rm -rf $(TARGETDIR) __pycache__

$(OUTPUT): $(SOURCE)
	transcrypt $(TRCOMPOPTS) $(TRLANGOPTS) $(patsubst %.py,%,$(SOURCE))

