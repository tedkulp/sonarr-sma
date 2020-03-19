#!/usr/bin/env python

import os
import sys
import logging
import configparser
import xml.etree.ElementTree as ET
import json
import sqlite3

xml = "/config/config.xml"
db = "/config/nzbdrone.db"
autoProcess = os.path.join(os.environ.get("SMA_PATH", "/usr/local/sma"), "config/autoProcess.ini")


def main():
    if not os.path.isfile(xml):
        logging.error("No Sonarr/Radarr config file found")
        sys.exit(1)

    if not os.path.isfile(autoProcess):
        logging.error("autoProcess.ini does not exist")
        sys.exit(1)

    tree = ET.parse(xml)
    root = tree.getroot()
    port = root.find("Port").text
    try:
        sslport = root.find("SslPort").text
    except:
        sslport = port
    webroot = root.find("UrlBase").text
    webroot = webroot if webroot else ""
    ssl = root.find("EnableSsl").text
    ssl = ssl.lower() in ["true", "yes", "t", "1", "y"] if ssl else False
    apikey = root.find("ApiKey").text
    section = os.environ.get("SMA_RS")
    if not section:
        logging.error("No Sonarr/Radarr specifying ENV variable")
        sys.exit(1)

    safeConfigParser = configparser.ConfigParser()
    safeConfigParser.read(autoProcess)

    # Set FFMPEG/FFProbe Paths
    safeConfigParser.set("Converter", "ffmpeg", "/usr/local/bin/ffmpeg")
    safeConfigParser.set("Converter", "ffprobe", "/usr/local/bin/ffprobe")

    # Set values from config.xml
    safeConfigParser.set(section, "apikey", apikey)
    safeConfigParser.set(section, "ssl", str(ssl))
    safeConfigParser.set(section, "port", sslport if ssl else port)
    safeConfigParser.set(section, "webroot", webroot)

    # Set IP from environment variable
    ip = os.environ.get("HOST")
    if ip:
        safeConfigParser.set(section, "host", ip)
    else:
        safeConfigParser.set(section, "host", "127.0.0.1")

    fp = open(autoProcess, "w")
    safeConfigParser.write(fp)
    fp.close()

    try:
        if not os.path.isfile(db):
            logging.error("nzbdrone.db does not exist")
            sys.exit(1)
        conn = sqlite3.connect(db)
        name = "SMA Post Process"
        settings = {
            "path": "/usr/local/sma/post%s.sh" % section,
            "arguments": ""
        }
        settings = json.dumps(settings, indent=2)
        query = "INSERT OR IGNORE INTO Notifications (ID, Name, OnGrab, OnDownload, OnUpgrade, OnRename, Settings, Tags, Implementation, ConfigContract) VALUES ((SELECT ID FROM Notifications WHERE Name = '%s'), '%s', 0, 1, 1, 0, '%s', '[]', 'CustomScript', 'CustomScriptSettings')" % (name, name, settings)
        conn.execute(query)
        conn.commit()
    except:
        logging.exception("Unable to add post script to Sonarr")


if __name__ == '__main__':
    main()
