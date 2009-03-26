"""
There are several unit conversion modules available for Python.  However, most
are large and complex.  A very small simple set of converters may be
appropriate for WebHelpers.  Here are some alternatives.

Chris Barker wrote some conversion tables (see module body) and recommends a
general convert function::

    convert(type, unit, to_unit, value)

``type`` is a unit type such as "Length", "Volume", "Temperature", "Mass",
etc.  ``unit`` and ``to_unit`` are two units of that type.  ``value`` is the
number you wish to convert.  The result is the value converted to ``to_unit``.

The Python Cookbook has a recipe called "Unit-safe measured quantities" 
(http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/270589)
by George Sakkis that does something similar.  Values are created in a more
conventional manner.  This example shows creating two length values, adding
them, comparing them, displaying them in a particular unit, and changing the
default display unit::

    l1 = Length(12.3,'cm')
    l2 = Length(50,'mm')
    Length.setDefaultUnit("in")
    print l1+l2             # "6.811024 in"
    print 3*l2.value("m")   # "0.15"
    print l1>l2             # "True"

Sakkis notes that values stored as plain floats tend to get confused when
multiple units or external modules are involved.  However, they can't be stored
in a numeric database field.  This implementation also doesn't handle aliases
(different names for the same unit), and has concrete classes only for Length
and Temperature.  It may be worthwhile to refactor this to use a converter like
Barker's, and then plug Barker's tables and aliases into it.  This would allow
users to choose between plain floats and Sakkis objects as desired, and to also
make canned converters as partials.

The Unum project is even more sophistocated, with a large collection of units
that can be used as Python operands.  For instance, ``3 * M/S`` creates a "3
meters per second" object.  Compatible values can be added, and plugged into
Numeric matrices.  In spite of this it's pure Python and has no nonstandard
dependencies.  However, it may be slower than other implementations due to the
overhead of the magic.  And it has a high learning curve, perhaps too high for
non-mathematical users with simple needs.

    * Unum project home:  http://sourceforge.net/projects/unum/
    * Tutorial: http://home.scarlet.be/be052320/Unum_tutorial.html
    * FAQ (including limitations):  http://home.scarlet.be/be052320/faq.html
"""

### Chris Barker's conversion tables.
### (Additional scientific tables are available.)

ConvertDataUnits = {
# All lengths in terms of meter

"Length" : {"meter"      : (1.0,["m","meters","metre"]),
            "centimeter" : (0.01,["cm", "centimeters"]),
            "millimeter"  : (0.001,["mm","millimeters"]),
            "micron"  : (0.000001,["microns"]),
            "kilometer"  : (1000.0,["km","kilometers"]),
            "foot"        : (0.3048,["ft", "feet"]),
            "inch"      : (0.0254,["in","inches"]),
            "yard"       : (0.9144,[ "yrd","yards"]),
            "mile"       : (1609.344,["mi", "miles"]),
            "nautical mile" : (1852.0,["nm","nauticalmiles"]),
            "fathom"  : (1.8288,["fthm", "fathoms"]),
            "latitude degree": (111120.0,["latitudedegrees"]),
            "latitude minute": (1852.0,["latitudeminutes"])
            },

# All Areas in terms of square meter
"Area" : {"square meter"  : (1.0,["m^2","sq m","squaremeter"]),
          "square centimeter": (.0001,["cm^2","sq cm"]),
          "square kilometer"  : (1e6,["km^2","sq km","squarekilometer"]),
          "acre"  : (4046.8564,["acres"]),
          "square mile"  : (2589988.1,["sq miles","squaremile"]),
          "square yard"  : (0.83612736,["sq yards","squareyards"]),
          "square foot"  : (0.09290304,["ft^2", "sq foot","square feet"]),
          "square inch"  : (0.00064516,["in^2", "sq inch","square inches"]),
          "hectar"  : (10000.0,["hectares"]),
          },

# All volumes in terms of cubic meter
"Volume" : {"cubic meter"  : (1.0,["m^3","cu m","cubic meters"]),
            "cubic centimeter"  : (1e-6,["cm^3","cu cm"]),
            "barrels (petroleum)" : (.1589873,["bbl","barrels","barrel","bbls",]),
            "liter"        : (1e-3,["l","liters"]),
            "gallon"       : (0.0037854118, ["gal","gallons","gallon","usgal"]),
            "gallon (UK)"  : (0.004546090, ["ukgal","gallons(uk)"]),
            "million US gallons"  : (3785.4118, ["milliongallons","milgal"]),
            "cubic foot"    : (0.028316847, ["ft^3","cu feet","cubicfeet"]),
            "cubic inch"    : (16.387064e-6, ["in^3","cu inch","cubicinches"]),
            "cubic yard"    : (.76455486, ["yd^3","cu yard","cubicyard","cubicyards"]),
            "fluid oz"      : (2.9573530e-5, ["oz","ounces(fluid)", "fluid oz"]),
            "fluid oz (UK)" : (2.841306e-5, ["ukoz", "fluid oz(uk)"]),
            },

# All Temperature units in K (multiply by, add)
"Temperature" : {"Kelvin"  : ((1.0, 0.0),["K","degrees k","degrees k","degrees kelvin","degree kelvin","deg k"]),
                 "centigrade"     : ((1.0, 273.16),["C","degrees c","degrees celsius","degree celsius","deg c"]),
                 "farenheight"  : ((0.55555555555555558, (273.16*9/5 - 32) ),["F","degrees f","degree f","degrees farenheight","deg f"]),
                 },

# All Mass units in Kg (weight is taken to be mass at standard g)
"Mass" : {"kilograms"  : (1.0,["kg","kilogram"]),
          "pound"     : (0.45359237,["lb","pounds","lbs"]),
          "gram"  : (.001,["g","grams"]),
          "ton"   : (907.18474, ["tons","uston"]),
          "metric ton" : (1000.0, ["tonnes","metric tons"]),
          "slug"       : (14.5939, ["slugs"]),
          "ounce"       : (.028349523, ["oz","ounces"]),
          "ton(UK)"       : (1016.0469, ["ukton","long ton"]),
          },

# All Time In second
"Time" : {"second"  : (1.0,["sec","seconds"]),
          "minute"  : (60.0,["min","minutes"]),
          "hour"    : (3600.0,["hr","hours","hrs"]),
          "day"     : (86400.0,["day","days"]),
          },
# All Velocities in meter per second
"Velocity" : {"meter per second"  : (1.0,["m/s","meters per second","mps"]),
              "centimeter per second"  : (.01,["cm/s"]),
              "kilometer per hour"  : (0.277777,["km/h", "km/hr"]),
              "knot"  : (0.514444,["knots","kts"]),
              "mile per hour"  : (0.44704,["mph","miles per hour"]),
              "foot per second"  : (0.3048,["ft/s", "feet per second", "feet/s"]),
              },
}


# Aliases should be stored in a normalized manner to prevent spelling
# variations from causing lookup failures.  Barker uses the following
# normalizer:
#
#    def normalize_unit(unit):
#        return "".join(unit.lower().split())
#
# Unit arguments are then filtered by this before lookup.
