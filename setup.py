# Copyright 2012 10gen, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This file will be used with PyPi in order to package and distribute the final product.

classifiers = """
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Programming Language :: Python
Programming Language :: JavaScript
Topic :: Database
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: Unix
"""

from distutils.core import setup

__doc__ = ""
doclines = __doc__.split("\n")

setup(
  name="edda",
  version="0.7.0",
  maintainer="10Gen",
  maintainer_email="kaushal.parikh@10gen.com",
  #url = "https://github.com/kchodorow/edda",
  license="http://www.apache.org/licenses/LICENSE-2.0.html",
  platforms=["any"],
  description=doclines[0],
  classifiers=filter(None, classifiers.split("\n")),
  long_description="\n".join(doclines[2:]),
  #include_package_data=True,
  packages=['edda', 'edda.filters', 'edda.post', 'edda.ui',
            'edda.sample_logs', 'edda.ui.display.js', 'edda.ui.display.style',
            'edda.ui.display', 'edda.sample_logs.hp', 'edda.sample_logs.pr'
           ],
  #packages = find_packages('src'),  # include all packages under src
  #package_dir = {'':'src'},   # tell distutils packages are under src
  scripts=['scripts/edda'],
  install_requires=['pymongo'],

  package_data={
    # If any package contains *.txt files, include them:
    'edda.ui.display.js': ['*.js'],
    'edda.ui.display.style': ['*.css', '*.ico'],
    'edda.ui.display': ['*.jpg', '*.html'],
    'edda.sample_logs.hp': ['*.log'],
    'edda.sample_logs.pr': ['*.log'],
    # And include any *.dat files found in the 'data' subdirectory
    # of the 'mypkg' package, also:
  }
)
