# MP5 Slicer
© 2016. GPL3

A fully functional slicer software for 3D printing using mp5 standard.
Developed as part of MP5 Project ( [MyMiniFactory Ltd](https://www.myminifactory.com) )

![Some actual objects 3D-printed using the **MP5 Slicer** ~ December 2016](https://repository-images.githubusercontent.com/72203031/dae5c53f-ccea-47a8-acef-d0dcdd1b2e63)
Figure: Two actual objects 3D-printed using the **MP5 Slicer** (~ Dec. 2016) on Ultimaker 2.

Everything ( g-code generation, slicing, shape modelling ) written from scratch,
using [ImpliSolid 3D](https://github.com/sohale/implisolid)
and [mp5 Slicer](https://github.com/sohale/mp5slicer).
Project supported by [MyMiniFactory Ltd](https://www.myminifactory.com), London, UK.

It features a sample curved organic shape, and an sample engineering object (screw) with sharp edged.
The two object shapes were defined using implicit modelling (just algebraic formulas).

* [ImpliSolid 3D](https://github.com/sohale/implisolid) can export STL - with curvature-adaptive surface subdivision.
* [ImpliSolid 3D](https://github.com/sohale/implisolid) can direcly slice the object (bypassing STL gneration) fir geometry-informed slice algorithm.
* It can also Import STL as SDF represenatation.

ut this is using our own slicer (directly from SDF). As you see, 
The details and quality is quite good, . Note there are no facets/mesh.


Out of the box, it can generate G-code of quite good quality.
It took a lot of experimentation by the team (interns and myself).
We experimented with various techniques, adjusting parameters such as speed of movements, FDM plastic injection speed, calibration, fine-tuning of various parameters (Z-offset, layer thickness, velocities, etc).

All those parameters are stored in the [**mp5 file format**](http://sohale.github.io/demos/implisolid-build/demo1/mp5_json_code.html) that we deveoloped for 3D Printing( see a sample [mp5](http://sohale.github.io/demos/implisolid-build/demo1/mp5_json_code.html) file).

[mp5 Slicer](https://github.com/sohale/mp5slicer) is the third iteration in a line of slicers we developed. The source code for the two ohters is also available.

Contact email:
<!-- not -->
`sohale`
<!-- .. -->
at `g`.

© 2016.
GPL3 License.
