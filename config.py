import math

class PrintSettings:
    #IT is immutable and does not have a self that updates itself.
    def __init__(self, argDictionnary):
        dic = PrintSettings.addDefaults(argDictionnary)
        for key,value in dic.items():
            setattr(self, key, value)
        self.crossArea = ((self.filamentDiameter/2.0)**2) * math.pi #6.37939


    #def getVolFactor():
    #    pass
    #def getArea():
    #    pass
    #pass
    @staticmethod
    def addDefaults(dict):
        try:
            dict["layerThickness"]
        except KeyError:
            dict["layerThickness"]=0.2

        try:
            dict["line_width"]
        except KeyError:
            dict["line_width"] = 0.4

        try:
            dict["temperature"]
        except KeyError:
            dict["temperature"]=210
    #Speed in  mm/min
        try:
            dict["inAirSpeed"]
        except KeyError:
            dict["inAirSpeed"]=3000
        try:
            dict["flowRate"]
        except KeyError:
            dict["flowRate"] = 0.035  # mm/mm = mm (filament) /mm (nozzle)

        try:
            dict["criticalLength"]
        except KeyError:
            dict["criticalLength"]=35

        try:
            dict["retractionSpeed"]
        except KeyError:
            dict["retractionSpeed"]=2400

        try:
            dict["retractionLength"]
        except KeyError:
            dict["retractionLength"]=5

        try:
            dict["speedRate"]
        except KeyError:
            dict["speedRate"]=1500 # mm/min

        try:
            dict["filamentDiameter"]
        except KeyError:
            dict["filamentDiameter"]=2.85

        try:
            dict["shellSize"]
        except KeyError:

            dict["shellSize"]=3


        saveEffectiveSettings = False
        if saveEffectiveSettings:
            #with fileLock:
            import json
            jsoncontent = json.dumps(dict)
            f1 = open("effectivesettings.json", "w+")
            f1.write(jsoncontent)

        return dict


class Printer_config():
    def __init__(self):
        self.autoZhop = False
        self.bedX = 1000
        self.bedY = 1000
        self.maxExtrusion = 123
        self.hasAutoTemperature = False
