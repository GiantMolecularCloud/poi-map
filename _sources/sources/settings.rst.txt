========
Settings
========

Options for the application itself, the InfluxDB connection and all connected devices are configured using a config file.
The docker image assumes that this file is called `config.yaml` but for local execution the name can be whatever.

Example
=======

A minimal example of the config can look like this:

.. code-block:: json
   :caption: config.json
   :name: config.json

   {
       "title": "Heidelberg",
       "database": "tests/test-data/poi.parquet",
       "categories": ["landmark", "university", "transportation", "nature"]
   }


Available settings
==================

Aside from the three basic settings (title, databse file, categories), further details can be set (zoomlevel, port, loglevel).


.. autopydantic_model:: poi_map.config.models.POIMapConfig
   :class-doc-from: class
   :inherited-members: BaseModel
