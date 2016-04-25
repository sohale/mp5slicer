import math

class PrintSettings:
    #IT is immutable and does not have a self that updates itself.
    def __init__(self, argDictionnary):
        dic = PrintSettings.addDefaults(argDictionnary)
        for key,value in dic.items():
            setattr(self, key, value)
        #self.crossArea = 6.376 # cross-section area of feedstock
        self.crossArea = ((self.filamentDiameter/2.0)**2) * math.pi #6.37939
        print("cross area = "+str(self.crossArea))
        #specific to PLA:
        self.volFactor = 1/2.53 # vol of filament -> vol of extruded material


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
            dict["line_width"] = 0.5

        try:
            dict["temperature"]
        except KeyError:
            dict["temperature"]=220
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
            dict["speedRate"]=2200 # mm/min

        try:
            dict["filamentDiameter"]
        except KeyError:
            dict["filamentDiameter"]=2.85

    #     try:
    #         dict["emptyLayer"]
    #     except KeyError:
    #         dict["emptyLayer"] = 0
    #     try:
    #         dict["infillSpace"]
    #     except KeyError:
    #         dict["infillSpace"]=4
    #     try:
    #         dict["topThickness"]
    #     except KeyError:
    #         dict["topThickness"]=0.6
    #     try:
    #         dict["paramSamples"]
    #     except KeyError:
    #         dict["paramSamples"]=75
    #     try:
    #         dict["name"]
    #     except KeyError:
    #         dict["name"]="test"
    # #Speed in  mm/min

        # try:
        #     dict["circleSpeedRate"]
        # except KeyError:
        #     dict["circleSpeedRate"]=1000

        #try:
        #    dict["areaFilament"]
        #except KeyError:
        #    dict["areaFilament"]=6.6
        # try:
        #     dict["bottomLayerSpeed"]
        # except KeyError:
        #     dict["bottomLayerSpeed"]=500

        # try:
        #     dict["shellNumber"]
        # except KeyError:
        #     dict["shellNumber"] = 3
        # try:
        #     dict["critLayerTime"]
        # except KeyError:
        #     dict["critLayerTime"] = 6
        # in seconds
        # try:
        #     dict["zScarGap"]
        # except KeyError:
        #     dict["zScarGap"] = 0.5
        # try:
        #     dict["autoZScar"]
        # except KeyError:
        #     dict["autoZScar"] = True

        #todo: filamentType = PLA or ABS

        saveEffectiveSettings = False
        if saveEffectiveSettings:
            #with fileLock:
            import json
            jsoncontent = json.dumps(dict)
            f1 = open("effectivesettings.json", "w+")
            f1.write(jsoncontent)

        return dict
