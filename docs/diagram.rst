===============
Package Diagram
===============

The package is structured with four module groups. The diagram below illustrates how those groups interact with each other. The main modules, indicated by the green colour, are responsible for preprocessing and deriving information related to the wind. The yellow, blue and red colours indicate the auxiliary modules. The yellow modules are used during the data preprocessing, and the red modules are used for preparing the final data for storage. The blue modules add extra functionalities to the package.


.. figure:: /figures/diagram.png
	:scale: 60%
	:align: center

The name of each module is indicated in the coloured part of each box, and the classes available in each module are listed inside the boxes. The starting point of the dashed lines indicates the classes that are calling other classes or functions from the auxiliary modules. The bold black lines indicate the data flow while using the package for retrieving wind information. The bold red lines indicate that some classes can be used to act on the preprocessed data before continuing with the wind retrieval.
