all: dist/ChemBO.app
	hdiutil create -volname ChemBO -srcfolder dist -ov -format UDZO chembo.dmg

dist/ChemBO.app: clean
	pyinstaller chembo.spec
	mkdir -p dist/ChemBO.app/Contents/MacOS
	mkdir -p dist/ChemBO.app/Contents/Resources
	cp app/ChemBO dist/ChemBO.app/Contents/MacOS
	chmod +x dist/ChemBO.app/Contents/MacOS/ChemBO
	cp app/Info.plist dist/ChemBO.app/Contents
	cp gui/assets/tray-256.icns dist/ChemBO.app/Contents/Resources
	mv dist/run_chembo dist/ChemBO.app/Contents/MacOS
	ln -s /Applications dist/Applications

.PHONY: clean
clean:
	rm -f chembo.dmg
	rm -rf dist
	rm -rf build

