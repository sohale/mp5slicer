; thanks to https://ultimaker.com/en/community/16078-start-end-gcode-for-um2
G28 ; home all axes
G1 X10 Y15 F3000 ; bring extruder to the front
G92 E0 ; zero the extruded length
G1 Z30 ; lower
G1 E20 F225 ; purge nozzle with 20mm of filament
G1 X80 Y60 F3000 ; move aside of the puddle of primed plastic
G92 E0 ; zero the extruded length again