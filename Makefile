## Spyglass Installer
##
## Selfdocumenting Makefile
## Based on https://www.freecodecamp.org/news/self-documenting-makefile/


.PHONY: help install uninstall update


#### Install Paths
USER = $(shell whoami)
SYSTEMD = /etc/systemd/system
BIN_PATH = /usr/local/bin
PRINTER_DATA_PATH=/home/$(USER)/printer_data
CONF_PATH = $(PRINTER_DATA_PATH)/config

all:
	$(MAKE) help

install: ## Install Spyglass as service
	@printf "\nCopying systemd service file ...\n"
	@sudo cp -f "${PWD}/resources/spyglass.service" $(SYSTEMD)
	@sudo sed -i "s/%USER%/$(USER)/g" $(SYSTEMD)/spyglass.service
	@printf "\nCopying spyglass launch script ...\n"
	@sudo ln -sf "${PWD}/scripts/spyglass" $(BIN_PATH)
	@printf "\nCopying basic configuration file ...\n"
	@cp -f "${PWD}/resources/spyglass.conf" $(CONF_PATH)
	@printf "\nPopulate new service file ... \n"
	@sudo systemctl daemon-reload
	@sudo echo "spyglass" >> $(PRINTER_DATA_PATH)/moonraker.asvc
	@printf "\nEnable spyglass service ... \n"
	@sudo systemctl enable spyglass
	@printf "\nTo be sure, everything is setup please reboot ...\n"
	@printf "Thanks for choosing spyglass ...\n"

uninstall: ## Uninstall Spyglass
	@printf "\nDisable spyglass service ... \n"
	@sudo systemctl disable spyglass
	@printf "\nRemove systemd service file ...\n"
	@sudo rm -f $(SYSTEMD)/spyglass.service
	@printf "\nRemoving spyglass launch script ...\n"
	@sudo rm -f $(BIN_PATH)/spyglass
	@sudo sed '/spyglass/d' $(PRINTER_DATA_PATH)/moonraker.asvc > $(PRINTER_DATA_PATH)/moonraker.asvc

update: ## Update Spyglass (via git Repository)
	@git fetch && git pull

upgrade-moonraker: ## In case of old version of spyglass being upgraded to newer version with moonraker update manager compatibility
	@printf "Upgrading systemctl ...\n"
	@sudo cp -f "${PWD}/resources/spyglass.service" $(SYSTEMD)
	@sudo sed -i "s/%USER%/$(USER)/g" $(SYSTEMD)/spyglass.service
	@printf "Upgrading moonraker update manager authorization ...\n"
	@sudo sed '/spyglass/d' $(PRINTER_DATA_PATH)/moonraker.asvc > $(PRINTER_DATA_PATH)/moonraker.asvc
	@sudo echo "spyglass" >> $(PRINTER_DATA_PATH)/moonraker.asvc
	@printf "You can now include the configuration in update-manager to manage Spyglass updates ...\n"
	@printf "Upgrade completed ...\n"
	@printf "Thanks for choosing spyglass ...\n"

help: ## Show this help
	@printf "\nSpyglass Install Helper:\n"
	@grep -E -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
